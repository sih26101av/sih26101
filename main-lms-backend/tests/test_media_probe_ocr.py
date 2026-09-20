"""services/media_quiz/probe — resolving RapidOCR's det/cls/rec sub-engines.

RapidOCR renamed these attributes between releases. The code used to hard-code one
layout, so on a server with a current wheel `text_density()` raised AttributeError
and *every* video upload 500'd, while audio (which never samples frames) was fine.
"""

import numpy as np
import pytest

from services.media_quiz import probe


class _Session:
    def __init__(self):
        self.session = object()


class _Part:
    """A det/cls sub-engine (session under .infer) or a rec one (under .session)."""

    def __init__(self, attr):
        setattr(self, attr, _Session())

    def __call__(self, img):
        h, w = img.shape[:2]
        box = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
        return [box], 0.01


def _engine(det_name, rec_name, cls_name="text_cls"):
    eng = type("FakeRapidOCR", (), {})()
    setattr(eng, det_name, _Part("infer"))
    setattr(eng, cls_name, _Part("infer"))
    setattr(eng, rec_name, _Part("session"))
    return eng


@pytest.mark.parametrize("det_name, rec_name", [
    ("text_det", "text_rec"),                  # rapidocr_onnxruntime >= 1.3.9
    ("text_detector", "text_recognizer"),      # older builds
])
def test_sub_engines_resolve_under_either_naming(det_name, rec_name):
    eng = _engine(det_name, rec_name)
    assert probe._detector(eng) is getattr(eng, det_name)
    assert probe._sub_engine(eng, "text_rec", "text_recognizer") is getattr(eng, rec_name)


def test_detector_is_none_when_the_layout_is_unknown():
    assert probe._detector(type("Opaque", (), {})()) is None


def test_limit_threads_survives_an_unknown_layout():
    probe._limit_threads(type("Opaque", (), {})())      # logs and keeps the stock pools


def test_text_density_reads_frames_through_the_detector(monkeypatch):
    monkeypatch.setattr(probe, "get_ocr", lambda: _engine("text_det", "text_rec"))
    frames = [np.zeros((90, 160, 3), dtype=np.uint8)]
    # The fake detector returns one box covering the whole frame — well past MIN_TEXT_AREA.
    assert probe.text_density(frames) == 1.0


def test_text_density_degrades_instead_of_raising(monkeypatch):
    monkeypatch.setattr(probe, "get_ocr", lambda: type("Opaque", (), {})())
    assert probe.text_density([np.zeros((90, 160, 3), dtype=np.uint8)]) == 0.0
