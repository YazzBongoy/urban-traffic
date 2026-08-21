#!/usr/bin/env python3
"""Reconnaissance marque/modèle/année de véhicules (EfficientNet-B4, 8949 classes).

Source : Jordo23/vehicle-classifier (MIT), entraîné sur VMMRdb.
Runtime principal : onnxruntime (modèle autonome vehicle_classifier_full.onnx).
Fallback : torch+timm si seul vehicle_classifier.pth est disponible.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

import numpy as np

MODEL_DIR = Path(__file__).resolve().parent / "models" / "vehicle-classifier"
STANDALONE_ONNX = MODEL_DIR / "vehicle_classifier_full.onnx"
ORIGINAL_ONNX = MODEL_DIR / "vehicle_classifier.onnx"
CHECKPOINT_PTH = MODEL_DIR / "vehicle_classifier.pth"
CLASS_MAPPING_CSV = MODEL_DIR / "class_mapping.csv"

IMG_SIZE = 380
NUM_CLASSES = 8949
INPUT_NAME = "input"
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_CLASS_MAP: dict[int, dict[str, Any]] | None = None


def _load_class_map() -> dict[int, dict[str, Any]]:
    global _CLASS_MAP
    if _CLASS_MAP is None:
        mapping: dict[int, dict[str, Any]] = {}
        with open(CLASS_MAPPING_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cid = int(row["global_class_id"])
                class_name = row["class_name"]
                parts = class_name.rsplit(" ", 1)
                year = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else None
                mapping[cid] = {
                    "class_name": class_name,
                    "make": row["make"],
                    "model": row["model"],
                    "year": year,
                }
        _CLASS_MAP = mapping
    return _CLASS_MAP


def preprocess(image: str | Path | bytes) -> np.ndarray:
    from PIL import Image

    if isinstance(image, bytes):
        img = Image.open(io.BytesIO(image))
    else:
        img = Image.open(image)
    img = img.convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - MEAN) / STD
    return arr.transpose(2, 0, 1)[np.newaxis].astype(np.float32)


def _softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - logits.max()
    e = np.exp(z)
    return e / e.sum()


def export_standalone_onnx(output_path: Path | None = None) -> Path:
    """Exporte le checkpoint .pth vers un ONNX autonome (poids embarqués).

    Nécessite torch et timm ; opération hors-ligne à n'exécuter qu'une fois.
    """
    import timm
    import torch

    out = output_path or STANDALONE_ONNX
    checkpoint = torch.load(CHECKPOINT_PTH, map_location="cpu", weights_only=False)
    model = timm.create_model("efficientnet_b4", pretrained=False, num_classes=NUM_CLASSES)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)
    torch.onnx.export(
        model,
        dummy,
        str(out),
        input_names=[INPUT_NAME],
        output_names=["logits"],
        dynamic_axes={INPUT_NAME: {0: "batch"}, "logits": {0: "batch"}},
        dynamo=False,
    )
    return out


class VehicleIdentifier:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.class_map = _load_class_map()
        self._session = None
        self._torch_model = None

    @property
    def backend(self) -> str:
        if self._session is not None:
            return "onnxruntime"
        if self._torch_model is not None:
            return "torch"
        return "uninitialized"

    def _get_session(self):
        if self._session is None:
            import onnxruntime as ort

            candidates = [p for p in (STANDALONE_ONNX, ORIGINAL_ONNX) if p.exists()]
            errors = []
            for path in candidates:
                try:
                    self._session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
                    break
                except (RuntimeError, OSError, ValueError) as e:
                    errors.append(f"{path.name}: {e}")
            if self._session is None:
                raise RuntimeError("Aucun modèle ONNX chargeable (" + "; ".join(errors) + ")")
        return self._session

    def _get_torch_model(self):
        if self._torch_model is None:
            import timm
            import torch

            checkpoint = torch.load(CHECKPOINT_PTH, map_location="cpu", weights_only=False)
            model = timm.create_model("efficientnet_b4", pretrained=False, num_classes=NUM_CLASSES)
            model.load_state_dict(checkpoint["model_state"])
            model.eval()
            self._torch_model = model
        return self._torch_model

    def _infer_logits(self, x: np.ndarray) -> np.ndarray:
        try:
            sess = self._get_session()
            input_name = sess.get_inputs()[0].name
            return sess.run(None, {input_name: x})[0][0]
        except (RuntimeError, OSError, ValueError):
            import torch

            model = self._get_torch_model()
            with torch.no_grad():
                return model(torch.from_numpy(x)).numpy()[0]

    def identify(self, image: str | Path | bytes) -> dict[str, Any]:
        x = preprocess(image)
        probs = _softmax(self._infer_logits(x))
        order = np.argsort(probs)[::-1][: max(1, self.top_k)]
        top5 = []
        for idx in order:
            info = self.class_map.get(int(idx))
            if info is None:
                continue
            top5.append({**info, "confidence": round(float(probs[idx]), 4)})
        if not top5:
            raise RuntimeError("Prédiction vide : indices hors class_mapping.csv")
        best = top5[0]
        return {
            "make": best["make"],
            "model": best["model"],
            "year": best["year"],
            "class_name": best["class_name"],
            "confidence": best["confidence"],
            "top5": top5,
        }


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Identification marque/modèle véhicule")
    parser.add_argument("image", help="Chemin de l'image ou '-' pour stdin (bytes)")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    data: str | bytes
    data = sys.stdin.buffer.read() if args.image == "-" else args.image

    identifier = VehicleIdentifier(top_k=args.top_k)
    result = identifier.identify(data)
    print(f"backend      : {identifier.backend}")
    print(f"prediction   : {result['class_name']} ({result['confidence'] * 100:.2f}%)")
    print("top-5 :")
    for i, p in enumerate(result["top5"], 1):
        print(f"  {i}. {p['class_name']}  {p['confidence'] * 100:.2f}%")
