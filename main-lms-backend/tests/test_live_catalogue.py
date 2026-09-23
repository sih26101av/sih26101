"""
Live iGOT catalogue: record normalisation, competencies_v6 parsing and the
KCM → FRAC crosswalk.

Everything here runs offline against the shapes the real portal returns (the
fixtures below are trimmed copies of genuine responses), with the same
deterministic bag-of-words stub embedder test_pathway.py uses, so no model
download and no network call:  pytest tests/test_live_catalogue.py
"""
import asyncio
import hashlib
import json

import numpy as np
import pytest

import services.kcm_crosswalk as kx
import services.recommendation_service as rs
from adapters.live_igot_adapter import LiveIgotAdapter, normalise_course

_DIM = 256


class _StubEmbedder:
    """Hashed bag-of-words → L2-normalised vector. Shared words ⇒ positive cosine."""

    def encode(self, texts, kind=None, batch_size=None, normalize_embeddings=True,
               show_progress_bar=False):
        out = np.zeros((len(texts), _DIM), dtype="float32")
        for row, text in enumerate(texts):
            for word in text.lower().replace(".", " ").split():
                out[row, int(hashlib.md5(word.encode()).hexdigest(), 16) % _DIM] += 1.0
            norm = np.linalg.norm(out[row])
            if norm:
                out[row] /= norm
        return out


def _v6(theme_ref, theme_name, area="Domain"):
    """One competencies_v6 tag, in the shape /api/content/v1/search returns."""
    return {
        "competencyAreaName": area,
        "competencyAreaRefId": "COMAREA-000002",
        "competencyThemeRefId": theme_ref,
        "competencyThemeName": theme_name,
        "competencyThemeType": "theme",
        "competencySubThemeRefId": theme_ref.replace("THEME", "SUBTHEME"),
        "competencySubThemeName": theme_name,
    }


# A trimmed but faithful upstream record.
LIVE_RECORD = {
    "identifier": "do_11372292543392153611",
    "name": "  PM WANI  ",
    "description": "Policy, technology and implementation of the PM-WANI scheme.",
    "duration": "20517",
    "leafNodesCount": 30,
    "avgRating": 4.4,
    "totalNoOfRating": 118,
    "primaryCategory": "Course",
    "difficultyLevel": "Beginner",
    "language": ["English"],
    "keywords": ["wifi", "broadband"],
    "organisation": ["NTIPRIT"],
    "source": "NTIPRIT",
    "channel": "0133783095823810560",
    "competencies_v6": [_v6("COMTHEME-000225", "Data Analytics")],
}


# ── Normalisation ─────────────────────────────────────────────────────────────

def test_normalise_keeps_the_fields_the_engine_parses():
    out = normalise_course(LIVE_RECORD)
    assert out["identifier"] == "do_11372292543392153611"
    assert out["name"] == "PM WANI"                 # upstream pads names with spaces
    assert out["duration"] == "20517"               # seconds-as-string, as the parser expects
    assert out["rating"] == 4.4 and out["rating_count"] == 118
    assert out["organisation"] == ["NTIPRIT"]
    assert out["competencies_v6"][0]["competencyThemeRefId"] == "COMTHEME-000225"


def test_normalise_omits_the_two_fields_igot_does_not_publish():
    """
    enrollment_count and completion_rate are learner-behaviour aggregates that
    live behind the Kong 401. Inventing a value for them would quietly feed the
    ranker's quality composite a number nobody measured.
    """
    out = normalise_course(LIVE_RECORD)
    assert "enrollment_count" not in out
    assert "completion_rate" not in out


def test_normalise_accepts_competencies_v6_as_a_json_string():
    raw = dict(LIVE_RECORD, competencies_v6=json.dumps(LIVE_RECORD["competencies_v6"]))
    assert normalise_course(raw)["competencies_v6"][0]["competencyThemeName"] == "Data Analytics"


def test_normalise_survives_a_record_with_nothing_in_it():
    out = normalise_course({})
    assert out["competencies_v6"] == [] and out["duration"] == "0"
    assert out["rating"] is None and out["rating_count"] is None


# ── Gated endpoints fail loudly ───────────────────────────────────────────────

@pytest.mark.parametrize("method, arg", [
    ("fetch_user_by_id", "usr_1"), ("fetch_user_enrollments", "usr_1"),
    ("fetch_user_history", "usr_1"), ("fetch_user_roster", None),
])
def test_per_user_reads_refuse_rather_than_return_empty(method, arg):
    """A wiring mistake must not look like "this official has no enrolments"."""
    adapter = LiveIgotAdapter()
    call = getattr(adapter, method)
    with pytest.raises(NotImplementedError):
        asyncio.run(call(arg) if arg is not None else call())


# ── competencies_v6 → the engine ──────────────────────────────────────────────

def _frac(cid, name, desc):
    return {"id": cid, "name": name, "description": desc, "competencyType": "Domain",
            "children": [{"level": n, "description": f"{name} level {n}"} for n in range(1, 6)]}


def _engine(tmp_path, monkeypatch, catalog, frac):
    monkeypatch.setattr(rs, "get_embedder", lambda role=None: _StubEmbedder())
    cat_p, frac_p = tmp_path / "catalog.json", tmp_path / "frac.json"
    cat_p.write_text(json.dumps(catalog), encoding="utf-8")
    frac_p.write_text(json.dumps(frac), encoding="utf-8")
    return rs.HybridRecommendationEngine(str(cat_p), str(frac_p))


FRAC = [_frac("comp_data", "Data Visualization", "charts dashboards visual analytics"),
        _frac("comp_price", "Price Index", "price index numbers inflation")]


def test_v6_tags_index_under_their_crosswalked_frac_id(tmp_path, monkeypatch):
    tag = _v6("COMTHEME-000225", "Data Storytelling")
    tag["fracId"] = "comp_data"                     # as apply_crosswalk stamps it
    catalog = [{"identifier": "c1", "name": "dashboards", "description": "dashboards",
                "duration": "3600", "competencies_v6": [tag]}]
    engine = _engine(tmp_path, monkeypatch, catalog, FRAC)
    assert engine.course_comp_levels()["c1"] == {"comp_data": None}


def test_v6_without_a_crosswalk_keeps_its_kcm_id(tmp_path, monkeypatch):
    """Unmapped is not the same as untagged: the course is still indexed, just
    under a key no FRAC gap asks for, which is exactly what we want."""
    catalog = [{"identifier": "c1", "name": "lifts", "description": "escalator maintenance",
                "duration": "3600", "competencies_v6": [_v6("COMTHEME-000999", "Escalator Maintenance")]}]
    engine = _engine(tmp_path, monkeypatch, catalog, FRAC)
    assert list(engine.course_comp_levels()["c1"]) == ["COMTHEME-000999"]


def test_v3_still_wins_when_a_course_carries_both(tmp_path, monkeypatch):
    """Mock data and the minority of live courses that kept CID tags must behave
    exactly as before this change."""
    catalog = [{"identifier": "c1", "name": "prices", "description": "prices",
                "duration": "3600",
                "competencies_v3": json.dumps([{"id": "comp_price", "name": "Price Index",
                                                "competencyLevel": "Level 3"}]),
                "competencies_v6": [dict(_v6("COMTHEME-000225", "Data"), fracId="comp_data")]}]
    engine = _engine(tmp_path, monkeypatch, catalog, FRAC)
    assert engine.course_comp_levels()["c1"] == {"comp_price": 3}


# ── Crosswalk ─────────────────────────────────────────────────────────────────

def test_crosswalk_maps_a_real_match_and_rejects_an_unrelated_theme(monkeypatch):
    monkeypatch.setattr("ai.embedder.get_embedder", lambda role=None: _StubEmbedder())
    monkeypatch.setattr("ai.embedder.encode_cached",
                        lambda role, texts, kind=None, batch_size=64, embedder=None:
                        _StubEmbedder().encode(texts))
    terms = [{"refId": "COMTHEME-1", "name": "Price Index", "description": "price index numbers inflation"},
             {"refId": "COMTHEME-2", "name": "Escalator Maintenance", "description": "lift escalator repair"}]
    out = kx.build_crosswalk(terms, FRAC, embedder=_StubEmbedder())
    mapped = {m["kcmRefId"]: m["fracId"] for m in out["mappings"]}
    assert mapped.get("COMTHEME-1") == "comp_price"
    assert "COMTHEME-2" not in mapped


def test_threshold_never_drops_below_the_calibrated_floor():
    """
    The percentile alone is not a safe bar. With a FRAC set whose members are
    mutually near-orthogonal the 99th percentile is tiny, and without the floor
    every unrelated KCM theme would map onto whatever is least unlike it.
    """
    orthogonal = np.eye(8, dtype="float32")
    assert kx._derive_threshold(orthogonal) == kx._ABS_FLOOR
    assert kx._derive_threshold(np.ones((1, 4), dtype="float32")) == kx._ABS_FLOOR


def test_apply_crosswalk_stamps_frac_ids_in_place_and_leaves_the_rest():
    catalog = [{"identifier": "c1", "competencies_v6": [_v6("COMTHEME-1", "Price Index"),
                                                        _v6("COMTHEME-9", "Unmapped")]},
               {"identifier": "c2", "competencies_v6": [_v6("COMTHEME-9", "Unmapped")]},
               {"identifier": "c3", "competencies_v6": []}]
    touched = kx.apply_crosswalk(catalog, {"COMTHEME-1": "comp_price"})
    assert touched == 1
    assert catalog[0]["competencies_v6"][0]["fracId"] == "comp_price"
    assert "fracId" not in catalog[0]["competencies_v6"][1]
    assert "fracId" not in catalog[1]["competencies_v6"][0]


def test_apply_crosswalk_with_no_mapping_is_a_no_op():
    catalog = [{"identifier": "c1", "competencies_v6": [_v6("COMTHEME-1", "Price Index")]}]
    assert kx.apply_crosswalk(catalog, {}) == 0
    assert "fracId" not in catalog[0]["competencies_v6"][0]


def test_load_crosswalk_returns_empty_when_the_file_is_missing(tmp_path):
    assert kx.load_crosswalk(str(tmp_path / "nope.json")) == {}


# ── Linking out to the real portal ────────────────────────────────────────────

def test_course_url_format_matches_the_portal():
    from adapters.live_igot_adapter import course_url
    assert course_url("do_11372292543392153611", base_url="https://portal.igotkarmayogi.gov.in") == \
        "https://portal.igotkarmayogi.gov.in/app/toc/do_11372292543392153611/overview"


def test_a_link_is_only_offered_for_a_course_the_live_catalogue_served(monkeypatch):
    """
    The mock generator mints ids in iGOT's own `do_<digits>` shape and none of
    them are real courses, so a pattern match would put a 404 behind every
    synthetic enrolment's "Continue" button. Membership is the only safe test.
    """
    import services.catalogue_source as cs
    monkeypatch.setattr(cs, "_live_ids", frozenset({"do_real_1"}))
    monkeypatch.setattr(cs, "_resolved", "live-api")

    assert cs.live_course_url("do_real_1").endswith("/app/toc/do_real_1/overview")
    assert cs.live_course_url("do_11372675153046877291") is None   # mock-minted id
    assert cs.live_course_url(None) is None
    assert cs.live_course_url("") is None


def test_no_links_at_all_in_mock_mode(monkeypatch):
    import services.catalogue_source as cs
    monkeypatch.setattr(cs, "_live_ids", frozenset())
    monkeypatch.setattr(cs, "_resolved", "mock")
    assert cs.is_live() is False
    assert cs.live_course_url("do_anything") is None
