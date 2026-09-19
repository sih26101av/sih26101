"""
Certificate upload → EvidenceLog → admin review, end to end on in-memory SQLite
with the extractor stubbed (no Gemini / embedder):
documented (MEDIUM) on upload, verified (HIGH) after approval, gone after rejection.

    pytest tests/test_certificate_evidence.py
"""
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth.database import get_db
from auth.dependencies import get_current_user
from auth.models import UserAuth
from models.models import Base, EvidenceLog
from routers import competency
from services import app_state
from services.baseline_assembler import BaselineAssembler
from services.document_extractor import (
    CertificateExtractionResult, ExtractedCompetency, _validated, normalise_date,
)

COMP = "comp_python_stats_017"


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def db():
        s = Session()
        try:
            yield s
        finally:
            s.close()

    async def fake_extract(data, filename):
        return CertificateExtractionResult(
            is_valid_credential=b"junk" not in data, issuing_organization="Coursera", extractor="ocr+e5",
            extracted_competencies=[ExtractedCompetency(
                competency_id=COMP, competency_name="Python for Statistical Computing",
                extracted_level=4.0, issue_date="2025-08-15", justification="bootcamp")],
        )
    monkeypatch.setattr(competency.extractor, "extract", fake_extract)
    invalidated = []
    monkeypatch.setattr(app_state, "invalidate_user", invalidated.append)

    app = FastAPI()
    app.include_router(competency.router)
    who = {"user": UserAuth(username="usr_1", role="official")}
    app.dependency_overrides[get_current_user] = lambda: who["user"]
    app.dependency_overrides[get_db] = db
    c = TestClient(app)
    c.who, c.Session, c.invalidated = who, Session, invalidated
    return c


def _rows(client):
    with client.Session() as s:
        return [(r.userId, r.compId, r.evidenceType, r.grantedValue) for r in s.query(EvidenceLog).all()]


def _upload(client, body=b"%PDF-1.4 cert", name="../../etc/cert.pdf"):
    return client.post("/api/v1/competencies/upload-certificate", files={"file": (name, body, "application/pdf")})


def test_upload_writes_documented_evidence_and_dedupes(client):
    r = _upload(client)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "success" and body["certificate"]["verification"] == "documented"
    assert body["certificate"]["filename"] == "cert.pdf"            # path stripped
    assert _rows(client) == [("usr_1", COMP, "DOCUMENTED_CERT", 4.0)]
    assert client.invalidated == ["usr_1"]
    again = _upload(client).json()
    assert again["status"] == "duplicate" and len(_rows(client)) == 1
    assert [c["status"] for c in client.get("/api/v1/competencies/certificates").json()["certificates"]] == ["PENDING"]


def test_invalid_document_writes_nothing(client):
    r = _upload(client, body=b"junk")
    assert r.json()["status"] == "no_evidence" and _rows(client) == []


def test_bad_extension_rejected(client):
    assert _upload(client, name="cert.exe").status_code == 400


def test_admin_approve_turns_rows_verified(client):
    cid = _upload(client).json()["certificate"]["id"]
    assert client.get("/api/v1/competencies/certificates/review").status_code == 403     # learner
    client.who["user"] = UserAuth(username="admin", role="admin")
    queue = client.get("/api/v1/competencies/certificates/review").json()
    assert queue["pendingCount"] == 1 and queue["certificates"][0]["userId"] == "usr_1"
    r = client.post(f"/api/v1/competencies/certificates/{cid}/review", json={"decision": "approve"})
    assert r.status_code == 200 and r.json()["certificate"]["verification"] == "verified"
    assert _rows(client) == [("usr_1", COMP, "VERIFIED_CERT", 4.0)]
    assert client.post(f"/api/v1/competencies/certificates/{cid}/review",
                       json={"decision": "reject"}).status_code == 409


def test_admin_reject_removes_rows(client):
    cid = _upload(client).json()["certificate"]["id"]
    client.who["user"] = UserAuth(username="admin", role="admin")
    r = client.post(f"/api/v1/competencies/certificates/{cid}/review", json={"decision": "reject", "note": "forged"})
    assert r.json()["certificate"]["status"] == "REJECTED" and _rows(client) == []


def test_verified_cert_lifts_confidence_over_documented():
    profile = {"experienceYears": 0, "competencies": [{"id": COMP, "name": "Python", "type": "Technical",
                                                         "requiredLevel": 4}]}
    now = datetime(2026, 1, 1)
    row = {"comp_id": COMP, "granted_value": 4.0, "issue_date": datetime(2025, 8, 15)}
    asm = BaselineAssembler({})
    documented = asm.compute_for_user(profile, [], [{**row, "evidence_type": "DOCUMENTED_CERT"}], now=now)[COMP]
    verified = asm.compute_for_user(profile, [], [{**row, "evidence_type": "VERIFIED_CERT"}], now=now)[COMP]
    assert documented["confidence"] == "MEDIUM" and verified["confidence"] == "HIGH"


def test_llm_ids_are_checked_against_frac():
    res = _validated({"is_valid_credential": True, "extracted_competencies": [
        {"competency_id": "made_up", "competency_name": "Python for Statistical Computing", "extracted_level": 9},
        {"competency_id": "also_made_up", "competency_name": "Nonsense", "extracted_level": 3},
    ]}, "gemini")
    assert [(c.competency_id, c.extracted_level) for c in res.extracted_competencies] == [(COMP, 5.0)]


def test_normalise_date():
    assert normalise_date("Issued on 15/08/2023") == "2023-08-15"
    assert normalise_date("August 15, 2023") == "2023-08-15"
    assert normalise_date("2099-01-01") is None
