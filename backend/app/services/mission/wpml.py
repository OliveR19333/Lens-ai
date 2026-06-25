"""DJI WPML 2.0 XML document builders (spec §6.2).

Produces the two XML members of a DJI mapping ``.kmz``:

* ``template.kml``  — area boundary polygon + mission template metadata
* ``waylines.wpml`` — executable flight path with per-waypoint photo actions

Heights in WPML are expressed in **metres**; the rest of this package works in
feet (spec §14.2), so altitudes are converted at the boundary here.

References: DJI Cloud API "Waypoint (WPML)" route file specification, v2.0.
The Mini 4 Pro drone enum value is **67** (spec §14.2 — confirm against the
WPML 2.0 spec at build time).
"""
from __future__ import annotations

from typing import List, Sequence, Tuple
from xml.sax.saxutils import escape

from .geo import METERS_PER_FOOT, Coord
from .grid import GridPlan

WPML_NS = "http://www.dji.com/wpmz/1.0.6"
KML_NS = "http://www.opengis.net/kml/2.2"

# DJI drone enum values (subset). 67 = Mini 4 Pro per spec §14.2.
DRONE_ENUM = {"mini4pro": 67}


def _fmt(n: float, ndigits: int = 8) -> str:
    return f"{n:.{ndigits}f}".rstrip("0").rstrip(".")


def build_template_kml(
    ring: Sequence[Coord],
    *,
    drone_enum: int = 67,
    finish_action: str = "goHome",
    take_off_security_height_m: float = 20.0,
) -> str:
    """Build ``template.kml`` — mission config + the survey area polygon."""
    coord_str = " ".join(f"{_fmt(x)},{_fmt(y)},0" for x, y in ring)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="{KML_NS}" xmlns:wpml="{WPML_NS}">
  <Document>
    <wpml:author>GAS Property Mapping System</wpml:author>
    <wpml:missionConfig>
      <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
      <wpml:finishAction>{escape(finish_action)}</wpml:finishAction>
      <wpml:exitOnRCLost>goContinue</wpml:exitOnRCLost>
      <wpml:takeOffSecurityHeight>{_fmt(take_off_security_height_m, 2)}</wpml:takeOffSecurityHeight>
      <wpml:droneInfo>
        <wpml:droneEnumValue>{drone_enum}</wpml:droneEnumValue>
        <wpml:droneSubEnumValue>0</wpml:droneSubEnumValue>
      </wpml:droneInfo>
    </wpml:missionConfig>
    <Folder>
      <wpml:templateType>mapping2d</wpml:templateType>
      <wpml:templateId>0</wpml:templateId>
      <Placemark>
        <Polygon>
          <outerBoundaryIs>
            <LinearRing>
              <coordinates>{coord_str}</coordinates>
            </LinearRing>
          </outerBoundaryIs>
        </Polygon>
      </Placemark>
    </Folder>
  </Document>
</kml>
"""


def _waypoint_placemark(index: int, lng: float, lat: float, height_m: float, speed_mps: float) -> str:
    """One executable waypoint with a take-photo action."""
    return f"""      <Placemark>
        <Point>
          <coordinates>{_fmt(lng)},{_fmt(lat)}</coordinates>
        </Point>
        <wpml:index>{index}</wpml:index>
        <wpml:executeHeight>{_fmt(height_m, 2)}</wpml:executeHeight>
        <wpml:waypointSpeed>{_fmt(speed_mps, 2)}</wpml:waypointSpeed>
        <wpml:waypointHeadingParam>
          <wpml:waypointHeadingMode>followWayline</wpml:waypointHeadingMode>
        </wpml:waypointHeadingParam>
        <wpml:waypointTurnParam>
          <wpml:waypointTurnMode>toPointAndStopWithContinuityHeading</wpml:waypointTurnMode>
          <wpml:waypointTurnDampingDist>0</wpml:waypointTurnDampingDist>
        </wpml:waypointTurnParam>
        <wpml:useStraightLine>1</wpml:useStraightLine>
        <wpml:actionGroup>
          <wpml:actionGroupId>{index}</wpml:actionGroupId>
          <wpml:actionGroupStartIndex>{index}</wpml:actionGroupStartIndex>
          <wpml:actionGroupEndIndex>{index}</wpml:actionGroupEndIndex>
          <wpml:actionGroupMode>parallel</wpml:actionGroupMode>
          <wpml:actionTrigger>
            <wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>
          </wpml:actionTrigger>
          <wpml:action>
            <wpml:actionId>{index}</wpml:actionId>
            <wpml:actionActuatorFunc>takePhoto</wpml:actionActuatorFunc>
            <wpml:actionActuatorFuncParam>
              <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
            </wpml:actionActuatorFuncParam>
          </wpml:action>
        </wpml:actionGroup>
      </Placemark>"""


def build_waylines_wpml(
    plan: GridPlan,
    *,
    drone_enum: int = 67,
    finish_action: str = "goHome",
    auto_flight_speed_mps: float = 6.0,
    gimbal_pitch_deg: float = -90.0,  # 90° nadir, spec §6.1
) -> str:
    """Build ``waylines.wpml`` — the executable flight path."""
    placemarks: List[str] = []
    for i, wp in enumerate(plan.waypoints):
        height_m = wp.altitude_ft * METERS_PER_FOOT
        placemarks.append(
            _waypoint_placemark(i, wp.lng, wp.lat, height_m, auto_flight_speed_mps)
        )
    body = "\n".join(placemarks)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="{KML_NS}" xmlns:wpml="{WPML_NS}">
  <Document>
    <wpml:missionConfig>
      <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
      <wpml:finishAction>{escape(finish_action)}</wpml:finishAction>
      <wpml:exitOnRCLost>goContinue</wpml:exitOnRCLost>
      <wpml:globalTransitionalSpeed>{_fmt(auto_flight_speed_mps, 2)}</wpml:globalTransitionalSpeed>
      <wpml:droneInfo>
        <wpml:droneEnumValue>{drone_enum}</wpml:droneEnumValue>
        <wpml:droneSubEnumValue>0</wpml:droneSubEnumValue>
      </wpml:droneInfo>
    </wpml:missionConfig>
    <Folder>
      <wpml:templateId>0</wpml:templateId>
      <wpml:waylineId>0</wpml:waylineId>
      <wpml:executeHeightMode>relativeToStartPoint</wpml:executeHeightMode>
      <wpml:autoFlightSpeed>{_fmt(auto_flight_speed_mps, 2)}</wpml:autoFlightSpeed>
      <wpml:gimbalPitchMode>usePointSetting</wpml:gimbalPitchMode>
      <wpml:globalGimbalPitch>{_fmt(gimbal_pitch_deg, 1)}</wpml:globalGimbalPitch>
{body}
    </Folder>
  </Document>
</kml>
"""
