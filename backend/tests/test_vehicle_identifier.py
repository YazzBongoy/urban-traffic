"""Vehicle make/model classifier: class mapping integrity + inference smoke test."""

import sys
from pathlib import Path

import pytest

ML_DIR = Path(__file__).resolve().parents[2] / "ml"
sys.path.insert(0, str(ML_DIR))

from vehicle_identifier import (  # noqa: E402
    CHECKPOINT_PTH,
    NUM_CLASSES,
    ORIGINAL_ONNX,
    STANDALONE_ONNX,
    VehicleIdentifier,
    _load_class_map,
)

MODEL_AVAILABLE = STANDALONE_ONNX.exists() or ORIGINAL_ONNX.exists() or CHECKPOINT_PTH.exists()


def test_load_class_map():
    class_map = _load_class_map()
    assert len(class_map) == NUM_CLASSES == 8949
    for info in class_map.values():
        assert {"make", "model", "year"} <= set(info)
        assert isinstance(info["make"], str) and info["make"]
        assert isinstance(info["model"], str) and info["model"]


@pytest.mark.skipif(not MODEL_AVAILABLE, reason="modèle binaire (onnx/pth) absent")
def test_identify_smoke_on_synthetic_image():
    from io import BytesIO

    from PIL import Image

    buffer = BytesIO()
    Image.new("RGB", (380, 380), color=(120, 120, 120)).save(buffer, format="JPEG")
    identifier = VehicleIdentifier(top_k=5)
    result = identifier.identify(buffer.getvalue())
    assert set(result) >= {"make", "model", "year", "class_name", "confidence", "top5"}
    assert len(result["top5"]) == 5
    confidences = [p["confidence"] for p in result["top5"]]
    assert confidences == sorted(confidences, reverse=True)
    assert sum(confidences) <= 1.0 + 1e-6
