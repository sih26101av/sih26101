"""
build_quiz() end to end with scripted providers (no network), plus the /upload and
/grade endpoints: cross-check drops, repair, failover, offline fallback, shuffling, caching.
"""

import asyncio
from collections import Counter

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ai.quiz import QuizBuildError, build_quiz
from ai.quiz import textutil as tu
from ai.quiz.verifier import gate
from tests.quiz_fakes import FakeProvider, chunk, load_doc, q, register

DOC = load_doc("national_accounts.txt")
CHUNKS = chunk(DOC)

GOOD = register(
    q("Which agency compiles the national accounts in India?",
      ["National Statistical Office (NSO)", "Reserve Bank of India", "Ministry of Finance", "NITI Aayog"], 0,
      "In India, the National Statistical Office (NSO) under the Ministry of Statistics and Programme "
      "Implementation compiles the national accounts following the System of National Accounts 2008 (SNA 2008)"),
    q("Why are intermediate goods excluded from GDP?",
      ["They are imported", "Their value is already embedded in the value of final goods",
       "They are not taxed", "They are produced by the government"], 1,
      "Intermediate goods are excluded from GDP because their value is already embedded in the value of final goods",
      bloom="understand"),
    q("If GVA at basic prices is 300, product taxes are 30 and product subsidies are 10, what is GDP?",
      ["320", "340", "300", "310"], 0,
      "GDP is obtained from GVA at basic prices by adding product taxes and subtracting product subsidies.", bloom="apply"),
    q("What is the base year of the current national accounts series in India?",
      ["2004-05", "2011-12", "1999-2000", "2017-18"], 1,
      "The current series of national accounts in India uses 2011-12 as the base year."),
    q("A country's net primary income from abroad is negative. How does its GNI compare with its GDP?",
      ["GNI is higher than GDP", "GNI equals GDP", "GNI is lower than GDP", "They cannot be compared"], 2,
      "When net primary income from abroad is negative, GNI is lower than GDP.", bloom="analyse"),
    q("How is Net Domestic Product obtained from GDP?",
      ["By adding net exports", "By subtracting the consumption of fixed capital",
       "By adding product subsidies", "By dividing by the deflator"], 1,
      "Net Domestic Product (NDP) is obtained by subtracting the consumption of fixed capital from GDP.", bloom="understand"),
)
HALLUCINATED = q("In which year did the NSO adopt SNA 2008 for India's accounts?",
                 ["2015", "2008", "2011", "2019"], 0,
                 "The NSO adopted SNA 2008 in the year 2015 after a review by the Planning Commission.")
EXTRA = register(
    q("When are Provisional Estimates for the financial year released?",
      ["At the end of May", "In the first week of January", "At the end of March", "In mid October"], 0,
      "Provisional Estimates for the financial year are released at the end of May, together with the quarterly "
      "estimate for the fourth quarter.", bloom="recall"),
)


@pytest.fixture(autouse=True)
def _lexical_vectors(monkeypatch):
    monkeypatch.setattr(tu, "vectorize", tu.tfidf_vectors)


def run(**kw):
    kw.setdefault("use_cache", False)
    return asyncio.run(build_quiz(DOC, CHUNKS, **kw))


def test_cross_model_happy_path():
    gen = FakeProvider("groq:gpt-oss", "gpt-oss", batches=[GOOD])
    chk = FakeProvider("groq:qwen", "qwen")
    res = run(n=5, difficulty="Medium", providers=[gen, chk])
    assert len(res.questions) == 5
    assert res.meta["generator"] == "groq:gpt-oss" and res.meta["checker"] == "groq:qwen"
    assert res.meta["verification"] == "cross-model"
    assert chk.purposes == ["check"] and gen.purposes == ["generate"]
    assert all(q.checked_by == "groq:qwen" for q in res.questions)


def test_hallucinated_question_dropped_by_gate():
    gen = FakeProvider("g", "gpt-oss", batches=[GOOD[:4] + [HALLUCINATED] + GOOD[4:]])
    res = run(n=5, providers=[gen, FakeProvider("c", "qwen")])
    assert all("Planning Commission" not in q.evidence for q in res.questions)
    assert res.meta["rejected"].get("evidence_not_in_source") == 1


def test_disagreeing_checker_drops_question_and_repair_tops_up():
    wrong = GOOD[2]
    gen = FakeProvider("g", "gpt-oss", batches=[GOOD[:5], EXTRA])
    chk = FakeProvider("c", "qwen", verdicts={wrong["question"]: 3})
    res = run(n=5, providers=[gen, chk])
    stems = [q.question for q in res.questions]
    assert wrong["question"] not in stems
    assert EXTRA[0]["question"] in stems  # repair round filled the gap
    assert res.meta["rejected"]["cross_check_disagree"] == 1
    assert gen.purposes == ["generate", "generate"]


def test_checker_answering_minus_one_marks_ambiguous():
    gen = FakeProvider("g", "gpt-oss", batches=[GOOD])
    chk = FakeProvider("c", "qwen", verdicts={GOOD[0]["question"]: -1})
    res = run(n=5, providers=[gen, chk])
    assert res.meta["rejected"]["ambiguous"] == 1
    assert GOOD[0]["question"] not in [q.question for q in res.questions]


def test_rate_limited_generator_fails_over_to_next_family():
    dead = FakeProvider("groq:gpt-oss", "gpt-oss", fail=True)
    gen2 = FakeProvider("groq:qwen", "qwen", batches=[GOOD])
    chk2 = FakeProvider("gemini", "gemini")
    res = run(n=5, providers=[dead, gen2, chk2])
    assert res.meta["generator"] == "groq:qwen" and res.meta["checker"] == "gemini"
    assert any("429" in e for e in res.meta["provider_errors"])
    assert len(res.questions) == 5


def test_single_provider_self_checks():
    only = FakeProvider("g", "gpt-oss", batches=[GOOD])
    res = run(n=5, providers=[only])
    assert res.meta["verification"] == "self"
    assert only.purposes == ["generate", "check"]


def test_no_checker_reachable_keeps_only_gate_verifiable_questions():
    gen = FakeProvider("g", "gpt-oss", batches=[GOOD, []])
    chk = FakeProvider("c", "qwen", fail=True)
    res = run(n=5, providers=[gen, chk])
    assert res.meta["verification"] == "gate-only"
    llm = [q for q in res.questions if q.engine != "offline"]
    assert llm and all(q.bloom_level in ("recall", "understand") for q in llm)


def test_all_providers_down_uses_offline_engine():
    res = run(n=5, providers=[FakeProvider("g", "gpt-oss", fail=True), FakeProvider("c", "qwen", fail=True)])
    assert res.meta["verification"] == "offline"
    assert len(res.questions) >= 3 and all(q.engine == "offline" for q in res.questions)


def test_no_providers_configured_uses_offline_engine():
    res = run(n=5, providers=[])
    assert res.meta["generator"] == "offline"


def test_answer_positions_are_balanced():
    counts = Counter()
    for seed in range(8):
        gen = FakeProvider("g", "gpt-oss", batches=[GOOD])
        res = run(n=5, providers=[gen, FakeProvider("c", "qwen")], seed=seed)
        counts.update(q.correct_answer for q in res.questions)
        for item in res.questions:  # shuffling must keep the key pointing at the right text
            original = next(g for g in GOOD if g["question"] == item.question)
            assert item.options[item.correct_answer] == original["options"][original["correct_answer"]]
    assert set(counts) == {0, 1, 2, 3} and max(counts.values()) <= 2 * min(counts.values())


def test_hard_prefers_reasoning_questions():
    res = run(n=3, difficulty="Hard", providers=[FakeProvider("g", "gpt-oss", batches=[GOOD]), FakeProvider("c", "qwen")])
    assert sum(q.bloom_level in ("apply", "analyse") for q in res.questions) >= 2


def test_cache_hit_makes_no_calls():
    gen = FakeProvider("g", "gpt-oss", batches=[GOOD])
    chk = FakeProvider("c", "qwen")
    first = asyncio.run(build_quiz(DOC, CHUNKS, n=5, difficulty="Easy", providers=[gen, chk], use_cache=True))
    calls = gen.calls + chk.calls
    second = asyncio.run(build_quiz(DOC, CHUNKS, n=5, difficulty="Easy", providers=[gen, chk], use_cache=True))
    assert gen.calls + chk.calls == calls and second.meta["cached"] is True
    assert [q.question for q in first.questions] == [q.question for q in second.questions]


def test_thin_document_raises():
    text = load_doc("thin.txt")
    with pytest.raises(QuizBuildError):
        asyncio.run(build_quiz(text, chunk(text), providers=[], use_cache=False))


# ── Offline engine quality on every fixture ──────────────────────────────────

@pytest.mark.parametrize("name", ["national_accounts.txt", "price_indices.txt", "sampling_surveys.txt", "time_series.txt"])
def test_offline_questions_are_grounded(name):
    from ai.quiz.passages import select_passages

    text = load_doc(name)
    res = asyncio.run(build_quiz(text, chunk(text), n=5, providers=[], use_cache=False, seed=1))
    passages = {p.id: p for p in select_passages(text, chunk(text), k=8)}
    assert len(res.questions) >= 4
    for item in res.questions:
        assert gate(item, passages) == []
        assert item.evidence in " ".join(text.split())
        assert item.answer_text in text
        assert all(opt in text for opt in item.options if not any(ch.isdigit() for ch in opt))
    assert len({q.question for q in res.questions}) == len(res.questions)


# ── Endpoints ────────────────────────────────────────────────────────────────

@pytest.fixture()
def client(monkeypatch):
    import routers.rag as rag
    from auth.dependencies import get_current_user
    from models.models import Base

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(rag, "SessionLocal", sessionmaker(bind=engine))

    async def fake_build(text, chunks, n=5, difficulty="Medium", **kw):
        fake_build.difficulty = difficulty
        return await build_quiz(text, chunks, n=n, difficulty=difficulty, use_cache=False,
                                providers=[FakeProvider("g", "gpt-oss", batches=[GOOD]), FakeProvider("c", "qwen")])

    monkeypatch.setattr(rag, "build_quiz", fake_build)
    app = FastAPI()
    app.include_router(rag.router, prefix="/api/v1/rag")
    app.dependency_overrides[get_current_user] = lambda: type("U", (), {"username": "usr_test0001"})()
    c = TestClient(app)
    c.fake_build = fake_build
    return c


def test_upload_hides_answer_key_and_honours_difficulty(client):
    resp = client.post("/api/v1/rag/upload", files={"file": ("na.txt", DOC.encode(), "text/plain")},
                       data={"difficulty": "Hard"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert client.fake_build.difficulty == "Hard"
    assert len(body["questions"]) == 5
    for item in body["questions"]:
        assert set(item) == {"question", "options", "bloom_level"}
    assert body["generation"]["verification"] == "cross-model"


def test_upload_thin_document_is_422(client):
    resp = client.post("/api/v1/rag/upload", files={"file": ("thin.txt", load_doc("thin.txt").encode(), "text/plain")})
    assert resp.status_code == 422


def test_grade_returns_review_with_evidence(client):
    import routers.rag as rag

    quiz_id = client.post("/api/v1/rag/upload", files={"file": ("na.txt", DOC.encode(), "text/plain")}).json()["quiz_id"]
    stored = rag.QUIZ_STORE[quiz_id]["questions"]
    wrong = [(q.correct_answer + 1) % 4 for q in stored]
    resp = client.post("/api/v1/rag/grade", json={"quiz_id": quiz_id, "answers": wrong})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["score"] == 0 and body["passed"] is False
    assert len(body["review"]) == len(stored)
    for row, q in zip(body["review"], stored):
        assert row["correct_answer"] == q.correct_answer and row["is_correct"] is False
        assert row["evidence"] and row["evidence"] in " ".join(DOC.split())
