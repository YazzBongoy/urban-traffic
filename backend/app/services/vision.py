"""Pont entre l'API et le pipeline vision (iot/video_processor/pipeline.py).

Chargement par chemin de fichier pour éviter de faire du paquet `iot`
une dépendance installable du backend.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

_PIPELINE_PATH = Path(__file__).resolve().parents[3] / "iot" / "video_processor" / "pipeline.py"
_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        spec = importlib.util.spec_from_file_location("ut_video_pipeline", _PIPELINE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Pipeline introuvable : {_PIPELINE_PATH}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _pipeline = module
    return _pipeline


def models_available() -> bool:
    return _PIPELINE_PATH.exists() and _get_pipeline().models_available()


def analyze_image(image_bytes: bytes, identify: bool = True) -> dict[str, Any]:
    return _get_pipeline().analyze_image(image_bytes, identify=identify)
