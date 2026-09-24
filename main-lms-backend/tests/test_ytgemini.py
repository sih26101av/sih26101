"""services/media_quiz/ytgemini — the Gemini tier that reads a public YouTube link.

It exists for hosts YouTube walls by IP (the Oracle VM), so it is judged on two things:
it must not trust an answer the model made up, and it must not waste the latency it is
there to save. No network: the HTTP call is replaced.
"""

import httpx
import pytest

from services.media_quiz import ytgemini as yg


class _Resp:
    def __init__(self, status, payload):
        self.status_code = status
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


def _answer(text, modality="VIDEO", finish="STOP"):
    return {"candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": finish}],
            "usageMetadata": {"promptTokensDetails": [{"modality": "TEXT", "tokenCount": 50},
                                                      {"modality": modality, "tokenCount": 5000}]}}


@pytest.fixture(autouse=True)
def _key(monkeypatch):
    monkeypatch.setattr(yg, "_key", lambda: "k" * 39)
    monkeypatch.setattr(yg, "MODE", "auto")
    monkeypatch.setattr(yg, "_models", lambda: ["m1", "m2"])
    yg._dead_models.clear()


def test_answer_without_video_tokens_is_refused(monkeypatch):
    # A model that never received the video spends only TEXT tokens; its "transcript"
    # is invented and must not become evidence.
    monkeypatch.setattr(httpx.Client, "post",
                        lambda self, *a, **k: _Resp(200, _answer('{"speech":[["00:01","00:04","made up"]]}', "TEXT")))
    with pytest.raises(yg._WindowError, match="without receiving the video"):
        yg._call(httpx.Client(), "u", 0, 300)


def test_bad_request_is_not_retried_on_other_models(monkeypatch):
    calls = []

    def post(self, url, **k):
        calls.append(url)
        return _Resp(400, {"error": {"message": "video is private"}})

    monkeypatch.setattr(httpx.Client, "post", post)
    with pytest.raises(yg._WindowError, match="private"):
        yg._call(httpx.Client(), "u", 0, 300)
    assert len(calls) == 1


def test_truncated_json_is_salvaged_row_by_row():
    raw = '{"lang":"hi","speech":[["00:01","00:04","पहला वाक्य"],["00:05","00:09","second \\"quoted\\""],["00:10","00:1'
    meta, speech, screen = yg._rows(raw)
    assert meta["lang"] == "hi"
    assert [r[2] for r in speech] == ["पहला वाक्य", 'second "quoted"']
    assert screen == []


def test_cues_shift_clip_time_and_drop_out_of_window_and_noise():
    # Answered in clip-relative time → shifted back to full-video time.
    cues = yg._cues([["00:01", "00:04", "a"], ["00:10", "00:12", "[Music]"]], 600, 900)
    assert [(c.start, c.text) for c in cues] == [(601.0, "a")]
    # Full-video time, one row outside the window.
    cues = yg._cues([["10:01", "10:05", "in"], ["16:10", "16:12", "out"]], 600, 900)
    assert [c.text for c in cues] == ["in"]


def test_repetition_loop_is_collapsed():
    rows = [["00:01", "00:03", "So the P term"], ["00:03", "00:05", "reacts."]] * 50
    rows.append(["00:09", "00:12", "Now the D term."])
    assert [c.text for c in yg._cues(rows, 0, 300)] == ["So the P term", "reacts.", "Now the D term."]


def test_plan_covers_short_videos_and_samples_long_ones(monkeypatch):
    monkeypatch.setattr(yg, "WINDOW_S", 300.0)
    monkeypatch.setattr(yg, "MAX_COVER_S", 1200.0)
    assert yg.plan(700) == [(0.0, 300.0), (300.0, 600.0), (600.0, 700)]
    long = yg.plan(3 * 3600)
    assert len(long) == 4 and long[0][0] == 0.0 and long[-1][1] == 3 * 3600


def test_unknown_length_stops_after_the_wave_where_speech_ends(monkeypatch):
    monkeypatch.setattr(yg, "WINDOW_S", 300.0)
    monkeypatch.setattr(yg, "PARALLEL", 3)
    monkeypatch.setattr(yg, "MAX_COVER_S", 3600.0)
    asked = []

    def call(client, url, a, b, speculative=False):
        asked.append(a)
        assert speculative
        if a >= 600:                       # the video is 7.5 min long
            raise yg._WindowError("past the end", 500)
        end = min(b, 450) - 1
        return "m1", {"lang": "en"}, [[yg._fmt(a + 1), yg._fmt(end), f"speech at {a}"]], []

    monkeypatch.setattr(yg, "_call", call)
    trace = {}
    res = yg.fetch("abcdefghijk", None, trace)
    assert sorted(asked) == [0.0, 300.0, 600.0]      # one wave, never a second
    assert res.windows_ok == 2 and res.lang == "en"
    assert res.duration == pytest.approx(449.0)
    assert trace["errors"] == []                     # a past-the-end window is expected


def test_disabled_without_key(monkeypatch):
    monkeypatch.setattr(yg, "_key", lambda: "")
    assert yg.fetch("abcdefghijk") is None
    assert yg.diagnosis("abcdefghijk")["enabled"] is False
