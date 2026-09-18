"""Scripted stand-ins for Groq/Gemini so the quiz pipeline can be tested offline."""

from __future__ import annotations

import os

from ai.quiz.providers import ProviderError

DOC_DIR = os.path.join(os.path.dirname(__file__), "data", "quiz_docs")


def load_doc(name: str) -> str:
    with open(os.path.join(DOC_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def chunk(text: str) -> list[str]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    return RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150, separators=["\n\n", "\n", ". ", " ", ""]
    ).split_text(text)


def q(question, options, answer, evidence, source_id="P1", bloom="recall", explanation="Stated in the document."):
    return {"source_id": source_id, "bloom_level": bloom, "question": question, "options": options,
            "correct_answer": answer, "evidence": evidence, "explanation": explanation}


class FakeProvider:
    """
    generate: returns the next batch from `batches` (a list of question lists) or raises.
    check:    answers each question from `verdicts` (question text → index); defaults to the
              key the generator used, i.e. agreement.
    """

    def __init__(self, name, family, batches=None, verdicts=None, fail=False, alive=True):
        self.name, self.family, self.model = name, family, name
        self.batches = list(batches or [])
        self.verdicts = verdicts or {}
        self.fail = fail
        self.alive = alive
        self.calls = 0
        self.purposes: list[str] = []
        self.keys: dict[str, int] = {}

    def available(self) -> bool:
        return self.alive

    async def complete_json(self, system, user, *, max_tokens, temperature=0.3, purpose="generate"):
        self.calls += 1
        self.purposes.append(purpose)
        if self.fail:
            self.alive = False
            raise ProviderError(f"{self.name}: HTTP 429 rate limited")
        if purpose == "generate":
            batch = self.batches.pop(0) if self.batches else []
            return {"questions": batch}
        import json

        items = json.loads(user[user.index("\n\n[") + 2:])
        answers = []
        for it in items:
            opts = [it["options"][str(i)] for i in range(len(it["options"]))]
            key = self.verdicts.get(it["question"])
            if key is None:
                key = KEYRING.get((it["question"], tuple(opts)), -1)
            answers.append({"id": it["id"], "answer": key, "reason": "fake"})
        return {"answers": answers}


# (question, options) → correct index, registered by tests for "agreeing" checkers.
KEYRING: dict[tuple, int] = {}


def register(*questions: dict) -> list[dict]:
    for item in questions:
        KEYRING[(item["question"], tuple(item["options"]))] = item["correct_answer"]
    return list(questions)
