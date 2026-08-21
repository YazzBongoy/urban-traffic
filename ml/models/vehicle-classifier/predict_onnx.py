"""Inférence marque/modèle véhicule via le modèle ONNX Jordo23/vehicle-classifier.

ATTENTION : vehicle_classifier.onnx du dépôt HF référence un fichier de poids
externe (vehicle_classifier_20251213_172519.onnx.data) ABSENT du dépôt.
Ce script est donc NON FONCTIONNEL en l'état ; il deviendra opérationnel dès
qu'un ONNX complet sera fourni (ou exporté depuis vehicle_classifier.pth).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

MODEL_DIR = Path(__file__).resolve().parent
ONNX_PATH = MODEL_DIR / "vehicle_classifier.onnx"
CSV_PATH = MODEL_DIR / "class_mapping.csv"

IMG_SIZE = 380
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_session = None
_class_map: dict[int, dict[str, str]] = {}


def _load_class_map() -> None:
    if _class_map:
        return
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            _class_map[int(row["global_class_id"])] = {
                "class_name": row["class_name"],
                "make": row["make"],
                "model": row["model"],
            }


def _get_session():
    global _session
    if _session is not None:
        return _session
    import onnxruntime as ort

    missing = ONNX_PATH.with_name("vehicle_classifier_20251213_172519.onnx.data")
    if not missing.exists():
        raise RuntimeError(
            f"ONNX inutilisable : poids externes absents ({missing.name}). "
            "Le dépôt HF ne contient pas ce fichier ; utiliser vehicle_classifier.pth "
            "(conversion torch->onnx requise) ou obtenir un ONNX autonome."
        )
    _session = ort.InferenceSession(str(ONNX_PATH), providers=["CPUExecutionProvider"])
    return _session


def preprocess(image_path: str | Path) -> np.ndarray:
    from PIL import Image

    img = Image.open(image_path).convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - MEAN) / STD
    return arr.transpose(2, 0, 1)[np.newaxis, ...]


def predict(image_path: str | Path, top_k: int = 5) -> list[dict]:
    sess = _get_session()
    x = preprocess(image_path).astype(np.float32)
    input_name = sess.get_inputs()[0].name
    logits = sess.run(None, {input_name: x})[0][0]
    probs = np.exp(logits - logits.max())
    probs /= probs.sum()
    top_idx = np.argsort(probs)[::-1][:top_k]
    _load_class_map()
    results = []
    for idx in top_idx:
        info = _class_map.get(int(idx), {"class_name": "?", "make": "?", "model": "?"})
        results.append({**info, "confidence": float(probs[idx])})
    return results


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Classification marque/modèle véhicule (ONNX)")
    parser.add_argument("image", help="Chemin de l'image à classifier")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    try:
        results = predict(args.image, top_k=args.top_k)
    except (RuntimeError, OSError, ValueError) as e:
        print(f"ERREUR : {e}", file=sys.stderr)
        return 1

    for i, r in enumerate(results, 1):
        print(
            f"{i}. {r['class_name']}  (make={r['make']}, model={r['model']})  "
            f"{r['confidence'] * 100:.2f}%"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
