"""Tests for Phase 4 pure logic (spec §12): auth decision + annotations."""
from dataclasses import dataclass

from app.services.auth_logic import decide_auth
from app.services import annotations as ann


# ---- auth decision ----
@dataclass
class FakeUser:
    username: str
    password_hash: str
    is_active: bool = True


def _verify(plain, hashed):
    # Stand-in for passlib: hash format is "hash:<plain>".
    return hashed == f"hash:{plain}"


def test_db_user_valid_password():
    u = FakeUser("devan", "hash:secret")
    assert decide_auth("devan", "secret", u, admin_username="admin",
                       admin_password="root", verify=_verify) is True


def test_db_user_wrong_password():
    u = FakeUser("devan", "hash:secret")
    assert decide_auth("devan", "nope", u, admin_username="admin",
                       admin_password="root", verify=_verify) is False


def test_inactive_user_rejected():
    u = FakeUser("devan", "hash:secret", is_active=False)
    assert decide_auth("devan", "secret", u, admin_username="admin",
                       admin_password="root", verify=_verify) is False


def test_bootstrap_admin_fallback_when_no_user():
    assert decide_auth("admin", "root", None, admin_username="admin",
                       admin_password="root", verify=_verify) is True
    assert decide_auth("admin", "bad", None, admin_username="admin",
                       admin_password="root", verify=_verify) is False


def test_unknown_user_no_fallback():
    assert decide_auth("ghost", "x", None, admin_username="admin",
                       admin_password="root", verify=_verify) is False


# ---- annotations ----
def _point(lng=-83.97, lat=35.75):
    return {"type": "Point", "coordinates": [lng, lat]}


def test_make_annotation_defaults_and_validation():
    f = ann.make_annotation("pond", _point())
    assert f["properties"]["feature_type"] == "pond"
    assert f["properties"]["source"] == "manual"
    assert f["properties"]["label"] == "Pond"
    assert "id" in f["properties"]
    # Unknown type falls back to "note".
    assert ann.make_annotation("dragon", _point())["properties"]["feature_type"] == "note"


def test_append_creates_collection_then_grows():
    fc = ann.append_annotation(None, ann.make_annotation("trees", _point()))
    assert len(fc["features"]) == 1
    fc = ann.append_annotation(fc, ann.make_annotation("fence", _point()))
    assert len(fc["features"]) == 2


def test_remove_annotation_by_id():
    a = ann.make_annotation("pond", _point())
    fc = ann.append_annotation(None, a)
    aid = a["properties"]["id"]
    fc = ann.remove_annotation(fc, aid)
    assert fc["features"] == []


def test_merge_features_combines_detected_and_manual():
    detected = {"type": "FeatureCollection", "features": [ann.make_annotation("structure", _point())]}
    manual = ann.append_annotation(None, ann.make_annotation("pond", _point()))
    merged = ann.merge_features(detected, manual)
    assert len(merged["features"]) == 2


def test_merge_handles_none():
    assert ann.merge_features(None, None)["features"] == []
