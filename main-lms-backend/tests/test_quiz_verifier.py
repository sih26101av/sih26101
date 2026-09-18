"""The deterministic grounding gate: hallucinated or malformed questions must be rejected."""

import pytest

from ai.quiz import textutil as tu
from ai.quiz.passages import Passage, select_passages
from ai.quiz.verifier import coerce, dedupe, gate
from tests.quiz_fakes import chunk, load_doc, q

P1 = Passage(
    id="P1",
    order=0,
    location="Page 3",
    text=(
        "The current series of national accounts in India uses 2011-12 as the base year. "
        "The previous series used 2004-05 as the base year. A base year should be a normal year, "
        "free from abnormal events such as droughts, floods or major economic shocks. "
        "The implicit price deflator is obtained by dividing GDP at current prices by GDP at "
        "constant prices and multiplying by 100."
    ),
)
P2 = Passage(
    id="P2",
    order=1,
    text="The NSO releases the First Advance Estimates of annual GDP around the first week of January, "
         "before the Union Budget is presented.",
)
PASSAGES = {"P1": P1, "P2": P2}
BASE_YEAR_EVIDENCE = "The current series of national accounts in India uses 2011-12 as the base year."


@pytest.fixture(autouse=True)
def _lexical_vectors(monkeypatch):
    monkeypatch.setattr(tu, "vectorize", tu.tfidf_vectors)


def _check(item):
    cand = coerce(item, engine="test")
    return gate(cand, PASSAGES), cand


def test_good_recall_question_passes_and_gets_location():
    reasons, cand = _check(q("What is the base year of the current national accounts series in India?",
                             ["2004-05", "2011-12", "2015-16", "1999-2000"], 1, BASE_YEAR_EVIDENCE))
    assert reasons == []
    assert cand.location == "Page 3"


def test_good_apply_question_with_computed_answer_passes():
    reasons, _ = _check(q("If GDP at current prices is 560 and at constant prices is 500, what is the implicit price deflator?",
                          ["112", "89", "106", "120"], 0,
                          "The implicit price deflator is obtained by dividing GDP at current prices by GDP at "
                          "constant prices and multiplying by 100.", bloom="apply"))
    assert reasons == []


def test_fabricated_evidence_quote_rejected():
    reasons, _ = _check(q("What is the base year of the current series?", ["2011-12", "2004-05", "2017-18", "1993-94"], 0,
                          "The current series uses 2011-12 as base year, chosen by the Planning Commission in 2015."))
    assert "evidence_not_in_source" in reasons


def test_fabricated_fact_rejected():
    # Evidence is genuine but the keyed answer (a figure) is not in the document.
    reasons, _ = _check(q("What is the base year of the current national accounts series?",
                          ["2017-18", "2004-05", "2001-02", "1993-94"], 0, BASE_YEAR_EVIDENCE))
    assert "number_not_in_source" in reasons


def test_wrong_key_rejected():
    reasons, _ = _check(q("When does the NSO release the First Advance Estimates of annual GDP?",
                          ["At the end of May", "around the first week of January", "In March", "In October"], 0,
                          P2.text, source_id="P2"))
    assert reasons and reasons[0] in {"wrong_key", "answer_not_in_source"}


def test_duplicate_options_rejected():
    reasons, _ = _check(q("What is the base year of the current series?", ["2011-12", "2011-12", "2004-05", "1993-94"], 0,
                          BASE_YEAR_EVIDENCE))
    assert "duplicate_options" in reasons


@pytest.mark.parametrize("bad", ["All of the above", "None of the above", "Both A and B"])
def test_banned_catch_all_options_rejected(bad):
    reasons, _ = _check(q("What is the base year of the current series?", ["2011-12", "2004-05", "1993-94", bad], 0,
                          BASE_YEAR_EVIDENCE))
    assert "banned_option" in reasons


def test_three_options_rejected():
    reasons, _ = _check(q("What is the base year of the current series?", ["2011-12", "2004-05", "1993-94"], 0,
                          BASE_YEAR_EVIDENCE))
    assert "bad_options" in reasons


def test_answer_leaked_in_stem_rejected():
    reasons, _ = _check(q("Before the Union Budget is presented, when are the First Advance Estimates released?",
                          ["around the first week of January", "end of May", "mid March", "early October"], 0,
                          P2.text, source_id="P2"))
    assert reasons == []
    reasons, _ = _check(q("The First Advance Estimates come out around the first week of January; when are they released?",
                          ["around the first week of January", "end of May", "mid March", "early October"], 0,
                          P2.text, source_id="P2"))
    assert "answer_in_stem" in reasons


def test_invented_figure_in_stem_rejected_for_recall():
    reasons, _ = _check(q("Which base year replaced the 1999-2000 series in 2015?", ["2011-12", "2004-05", "1993-94", "2017-18"], 0,
                          BASE_YEAR_EVIDENCE))
    assert "stem_number_not_in_source" in reasons


def test_miscited_source_is_repaired():
    reasons, cand = _check(q("What is the base year of the current series?", ["2011-12", "2004-05", "1993-94", "2017-18"], 0,
                             BASE_YEAR_EVIDENCE, source_id="P2"))
    assert reasons == [] and cand.source_id == "P1"


def test_letter_answer_and_passage_wording_are_normalised():
    cand = coerce({"question": "According to the passage, what is the base year?",
                   "options": ["A) 2011-12", "B) 2004-05", "C) 1993-94", "D) 2017-18"],
                   "answer": "A", "evidence": BASE_YEAR_EVIDENCE, "source_id": "P1"}, engine="t")
    assert cand.correct_answer == 0 and cand.options[0] == "2011-12"
    assert "passage" not in cand.question and "document" in cand.question


def test_dedupe_drops_same_fact_twice():
    a = coerce(q("What is the base year of the current national accounts series?", ["2011-12", "2004-05", "1993-94", "2017-18"], 0,
                 BASE_YEAR_EVIDENCE), "t")
    b = coerce(q("What is the base year of the current series of national accounts?", ["2011-12", "2004-05", "1999-00", "2017-18"], 0,
                 BASE_YEAR_EVIDENCE), "t")
    kept, dropped = dedupe([a, b])
    assert len(kept) == 1 and dropped == 1


def test_passage_selection_skips_toc_and_references():
    text = load_doc("toc_heavy.txt")
    passages = select_passages(text, chunk(text), k=8)
    assert passages
    joined = " ".join(p.text for p in passages)
    assert "......" not in joined and "doi:" not in joined and "household" in joined


def test_passage_selection_labels_pages():
    text = load_doc("national_accounts.txt")
    passages = select_passages(text, chunk(text), k=8)
    assert [p.id for p in passages] == [f"P{i}" for i in range(1, len(passages) + 1)]
    assert all(p.location and p.location.startswith("Page") for p in passages)


def test_thin_document_has_no_passages():
    text = load_doc("thin.txt")
    assert select_passages(text, chunk(text)) == []
