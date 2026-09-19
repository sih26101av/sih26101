"""English and Hinglish replies must match the pre-catalogue output, except deliberate fixes."""

import asyncio
import json
import os
import random

import pytest

from services.chat_messages import render
from services.chat_messages.context import ReplyContext
from tests.fixtures import sample_request

SNAPSHOT = json.load(open(os.path.join(os.path.dirname(__file__), "data", "reply_snapshot_before.json"), encoding="utf-8"))

RENAMED = {"navigation_quiz": "navigation_ai_quiz", "general": "fallback"}
OLD_TO_VARIANT = {"en": "en", "hi": "hi_latn"}

INTENTIONAL_HANDLER_CHANGES = {
    "bot_identity": "claimed '50+ languages'; now names the 8 supported ones",
    "ui_action_request": "said it cannot change theme/language; the router now performs those actions",
    "navigation_quiz": "pointed to a Dashboard card that no longer exists; now the Assessment Studio sidebar section",
}

INTENTIONAL_ENDPOINT_CHANGES = {
    "dashboard|switch to light mode and change language to hindi": "compound command only switched language (intercept order bug)",
    "home|take me to features": "replied 'not sure' because navigation_features had no handler",
    "home|scroll to contact section": "scroll replies now describe the section",
}

handler_cases = [
    key for key in SNAPSHOT["handler"]
    if key.split("|")[2] not in INTENTIONAL_HANDLER_CHANGES
]


@pytest.mark.parametrize("snapshot_key", handler_cases)
def test_handler_reply_unchanged(snapshot_key):
    page, old_lang, old_intent = snapshot_key.split("|")
    message = "change the theme to dark" if old_intent == "ui_action_request" else "x"
    ctx = ReplyContext.from_request(sample_request(message, page))
    random.seed(1234)
    assert render(RENAMED.get(old_intent, old_intent), OLD_TO_VARIANT[old_lang], ctx) == SNAPSHOT["handler"][snapshot_key]


endpoint_cases = [key for key in SNAPSHOT["endpoint"] if key not in INTENTIONAL_ENDPOINT_CHANGES]


@pytest.mark.parametrize("snapshot_key", endpoint_cases)
def test_endpoint_reply_unchanged(snapshot_key):
    from routers.chatbot import chat

    page, message = snapshot_key.split("|", 1)
    random.seed(1234)
    response = asyncio.run(chat(sample_request(message, page))).model_dump()
    assert response == SNAPSHOT["endpoint"][snapshot_key]
