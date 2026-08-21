"""Pipeline d'analyse vidéo : détection véhicules (YOLOv8n) + identification marque/modèle (VMMRdb).

Phase 2 — Système Vidéo. Les poids ne sont pas versionnés :
  ml/models/yolov8n/yolov8n.onnx          (~12 Mo)
  ml/models/vehicle-classifier/*.onnx     (~134 Mo, voir export_standalone_onnx)
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

VEHICLE_CLASS_IDS = {2, 3, 5, 7}

_detector = None
_identifier = None


def _get_detector():
    global _detector
    if _detector is None:
        from ml.models.yolov8n.predict_yolo import YoloV8Detector

        _detector = YoloV8Detector()
    return _detector


def _get_identifier():
    global _identifier
    if _identifier is None:
        from ml.vehicle_identifier import VehicleIdentifier

        _identifier = VehicleIdentifier(top_k=3)
    return _identifier


def models_available() -> bool:
    yolo = REPO_ROOT / "ml" / "models" / "yolov8n" / "yolov8n.onnx"
    classifier_dir = REPO_ROOT / "ml" / "models" / "vehicle-classifier"
    has_classifier = any(
        (classifier_dir / name).exists()
        for name in ("vehicle_classifier_full.onnx", "vehicle_classifier.pth")
    )
    return yolo.exists() and has_classifier and (classifier_dir / "class_mapping.csv").exists()


def analyze_image(image_bytes: bytes, identify: bool = True) -> dict[str, Any]:
    """Détecte les véhicules dans une image et identifie marque/modèle de chaque crop."""
    detector = _get_detector()
    detections = [d for d in detector.detect(image_bytes) if d["class_id"] in VEHICLE_CLASS_IDS]

    results: list[dict[str, Any]] = []
    for det in detections:
        entry: dict[str, Any] = {
            "vehicle_type": det["class_name"],
            "detection_confidence": round(float(det["confidence"]), 4),
            "bbox_xyxy": [round(v, 1) for v in det["bbox_xyxy"]],
            "identification": None,
        }
        if identify and det["class_id"] == 2:
            crop = _crop_to_jpeg(image_bytes, det["bbox_xyxy"])
            if crop is not None:
                try:
                    ident = _get_identifier().identify(crop)
                    entry["identification"] = {
                        "make": ident["make"],
                        "model": ident["model"],
                        "year": ident.get("year"),
                        "confidence": ident["confidence"],
                        "top3": [
                            {"class_name": t["class_name"], "confidence": t["confidence"]}
                            for t in ident.get("top5", [])[:3]
                        ],
                    }
                except (RuntimeError, OSError, ValueError):
                    entry["identification"] = None
        results.append(entry)

    return {"detections": results, "count": len(results)}


def _crop_to_jpeg(image_bytes: bytes, bbox_xyxy: list[float]) -> bytes | None:
    from PIL import Image

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            x1, y1, x2, y2 = (int(round(v)) for v in bbox_xyxy)
            x1, y1 = max(0, x1), max(0, y1)
            crop = img.convert("RGB").crop((x1, y1, x2, y2))
            if crop.width < 20 or crop.height < 20:
                return None
            buf = io.BytesIO()
            crop.save(buf, format="JPEG", quality=90)
            return buf.getvalue()
    except OSError:
        return None
