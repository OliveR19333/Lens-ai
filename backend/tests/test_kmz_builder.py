"""Tests for the DJI WPML 2.0 KMZ builder (spec §6.2)."""
import io
import zipfile

import pytest

from app.services.mission import MissionParams, build_mission_kmz


def test_kmz_has_correct_archive_layout(square_parcel):
    result = build_mission_kmz(square_parcel)
    with zipfile.ZipFile(io.BytesIO(result.kmz_bytes)) as zf:
        names = set(zf.namelist())
    assert "wpmz/template.kml" in names
    assert "wpmz/waylines.wpml" in names


def test_waylines_contain_mini4pro_drone_enum(square_parcel):
    result = build_mission_kmz(square_parcel)
    # droneEnumValue 67 = Mini 4 Pro (spec §14.2)
    assert "<wpml:droneEnumValue>67</wpml:droneEnumValue>" in result.waylines_wpml
    assert "<wpml:droneEnumValue>67</wpml:droneEnumValue>" in result.template_kml


def test_waylines_contain_core_mission_config_fields(square_parcel):
    result = build_mission_kmz(square_parcel)
    wpml = result.waylines_wpml
    assert "<wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>" in wpml
    assert "<wpml:finishAction>goHome</wpml:finishAction>" in wpml
    assert "<wpml:exitOnRCLost>goContinue</wpml:exitOnRCLost>" in wpml


def test_every_waypoint_has_a_take_photo_action(square_parcel):
    result = build_mission_kmz(square_parcel)
    n = len(result.plan.waypoints)
    assert result.waylines_wpml.count("<wpml:actionActuatorFunc>takePhoto</wpml:actionActuatorFunc>") == n
    assert result.waylines_wpml.count("<Placemark>") == n


def test_template_kml_is_well_formed_xml(square_parcel):
    import xml.dom.minidom as minidom

    result = build_mission_kmz(square_parcel)
    # Raises on malformed XML.
    minidom.parseString(result.template_kml)
    minidom.parseString(result.waylines_wpml)


def test_altitude_out_of_range_rejected(square_parcel):
    with pytest.raises(ValueError):
        build_mission_kmz(square_parcel, MissionParams(altitude_ft=250))
    with pytest.raises(ValueError):
        build_mission_kmz(square_parcel, MissionParams(altitude_ft=50))


def test_summary_reports_consistent_counts(square_parcel):
    result = build_mission_kmz(square_parcel)
    s = result.summary()
    assert s["waypoints"] == len(result.plan.waypoints)
    assert s["kmz_size_bytes"] == len(result.kmz_bytes)
    assert s["estimated_photos"] == s["waypoints"]
