// DJI WPML 2.0 XML builders — browser port of app/services/mission/wpml.py.
import { METERS_PER_FOOT } from './geo'

export const WPML_NS = 'http://www.dji.com/wpmz/1.0.6'
export const KML_NS = 'http://www.opengis.net/kml/2.2'
export const DRONE_ENUM = { mini4pro: 67 } // Mini 4 Pro (spec §14.2)

function fmt(n, ndigits = 8) {
  let s = Number(n).toFixed(ndigits)
  if (s.indexOf('.') >= 0) s = s.replace(/0+$/, '').replace(/\.$/, '')
  return s
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

export function buildTemplateKml(ring, { droneEnum = 67, finishAction = 'goHome', takeOffSecurityHeightM = 20 } = {}) {
  const coordStr = ring.map(([x, y]) => `${fmt(x)},${fmt(y)},0`).join(' ')
  return `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="${KML_NS}" xmlns:wpml="${WPML_NS}">
  <Document>
    <wpml:author>TNC GAS Mapping</wpml:author>
    <wpml:missionConfig>
      <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
      <wpml:finishAction>${esc(finishAction)}</wpml:finishAction>
      <wpml:exitOnRCLost>goContinue</wpml:exitOnRCLost>
      <wpml:takeOffSecurityHeight>${fmt(takeOffSecurityHeightM, 2)}</wpml:takeOffSecurityHeight>
      <wpml:droneInfo>
        <wpml:droneEnumValue>${droneEnum}</wpml:droneEnumValue>
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
              <coordinates>${coordStr}</coordinates>
            </LinearRing>
          </outerBoundaryIs>
        </Polygon>
      </Placemark>
    </Folder>
  </Document>
</kml>
`
}

function placemark(index, lng, lat, heightM, speedMps) {
  return `      <Placemark>
        <Point>
          <coordinates>${fmt(lng)},${fmt(lat)}</coordinates>
        </Point>
        <wpml:index>${index}</wpml:index>
        <wpml:executeHeight>${fmt(heightM, 2)}</wpml:executeHeight>
        <wpml:waypointSpeed>${fmt(speedMps, 2)}</wpml:waypointSpeed>
        <wpml:waypointHeadingParam>
          <wpml:waypointHeadingMode>followWayline</wpml:waypointHeadingMode>
        </wpml:waypointHeadingParam>
        <wpml:waypointTurnParam>
          <wpml:waypointTurnMode>toPointAndStopWithContinuityHeading</wpml:waypointTurnMode>
          <wpml:waypointTurnDampingDist>0</wpml:waypointTurnDampingDist>
        </wpml:waypointTurnParam>
        <wpml:useStraightLine>1</wpml:useStraightLine>
        <wpml:actionGroup>
          <wpml:actionGroupId>${index}</wpml:actionGroupId>
          <wpml:actionGroupStartIndex>${index}</wpml:actionGroupStartIndex>
          <wpml:actionGroupEndIndex>${index}</wpml:actionGroupEndIndex>
          <wpml:actionGroupMode>parallel</wpml:actionGroupMode>
          <wpml:actionTrigger>
            <wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>
          </wpml:actionTrigger>
          <wpml:action>
            <wpml:actionId>${index}</wpml:actionId>
            <wpml:actionActuatorFunc>takePhoto</wpml:actionActuatorFunc>
            <wpml:actionActuatorFuncParam>
              <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
            </wpml:actionActuatorFuncParam>
          </wpml:action>
        </wpml:actionGroup>
      </Placemark>`
}

export function buildWaylinesWpml(plan, { droneEnum = 67, finishAction = 'goHome', autoFlightSpeedMps = 6, gimbalPitchDeg = -90 } = {}) {
  const body = plan.waypoints
    .map((wp, i) => placemark(i, wp.lng, wp.lat, wp.altitudeFt * METERS_PER_FOOT, autoFlightSpeedMps))
    .join('\n')
  return `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="${KML_NS}" xmlns:wpml="${WPML_NS}">
  <Document>
    <wpml:missionConfig>
      <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
      <wpml:finishAction>${esc(finishAction)}</wpml:finishAction>
      <wpml:exitOnRCLost>goContinue</wpml:exitOnRCLost>
      <wpml:globalTransitionalSpeed>${fmt(autoFlightSpeedMps, 2)}</wpml:globalTransitionalSpeed>
      <wpml:droneInfo>
        <wpml:droneEnumValue>${droneEnum}</wpml:droneEnumValue>
        <wpml:droneSubEnumValue>0</wpml:droneSubEnumValue>
      </wpml:droneInfo>
    </wpml:missionConfig>
    <Folder>
      <wpml:templateId>0</wpml:templateId>
      <wpml:waylineId>0</wpml:waylineId>
      <wpml:executeHeightMode>relativeToStartPoint</wpml:executeHeightMode>
      <wpml:autoFlightSpeed>${fmt(autoFlightSpeedMps, 2)}</wpml:autoFlightSpeed>
      <wpml:gimbalPitchMode>usePointSetting</wpml:gimbalPitchMode>
      <wpml:globalGimbalPitch>${fmt(gimbalPitchDeg, 1)}</wpml:globalGimbalPitch>
${body}
    </Folder>
  </Document>
</kml>
`
}
