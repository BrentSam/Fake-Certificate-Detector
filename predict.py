from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from ela_converter import is_supported_image, make_ela_image
from train_model import DEFAULT_MODEL_PATH


def require_tensorflow():
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit(
            "TensorFlow is required for prediction. Install dependencies with: "
            "pip install -r requirements.txt"
        ) from exc
    tf.get_logger().setLevel("ERROR")
    return tf


def image_to_model_array(image_path: str | Path, quality: int = 90, size: int = 128) -> np.ndarray:
    image_path = Path(image_path)
    if not is_supported_image(image_path):
        raise SystemExit("Input image was not found or uses an unsupported image format.")

    ela_image = make_ela_image(image_path, quality=quality, size=size)
    array = np.asarray(ela_image, dtype=np.float32)
    return np.expand_dims(array, axis=0)


def predict_certificate(
    image_path: str | Path,
    model_path: str | Path = DEFAULT_MODEL_PATH,
    threshold: float = 0.5,
    quality: int = 90,
    size: int = 224,
    cert_type: str | None = None,
    min_confidence: float = 0.70,
) -> dict[str, float | str | bool | None]:
    tf = require_tensorflow()
    model_path = Path(model_path)

    if cert_type and model_path == Path(DEFAULT_MODEL_PATH):
        model_path = Path(f"model/{cert_type}_cnn.keras")

    if not model_path.exists():
        raise SystemExit(f"Model not found at {model_path}. Train the model before prediction.")

    model = tf.keras.models.load_model(model_path)
    image_array = image_to_model_array(image_path, quality=quality, size=size)
    fake_probability = float(model.predict(image_array, verbose=0).ravel()[0])
    is_fake = fake_probability >= threshold
    confidence = fake_probability if is_fake else 1.0 - fake_probability

    if confidence < min_confidence:
        return {
            "label": "Invalid Format",
            "fake_probability": fake_probability,
            "confidence": confidence,
            "cert_type": cert_type,
            "valid": False,
        }

    return {
        "label": "Fake Certificate" if is_fake else "Real Certificate",
        "fake_probability": fake_probability,
        "confidence": confidence,
        "cert_type": cert_type,
        "valid": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Predict whether one certificate image is real or fake.")
    parser.add_argument("image", help="Path to certificate image.")
    parser.add_argument("--cert-type", choices=["internship", "medical"], default=None, help="Type of certificate to predict.")
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH), help="Trained model path.")
    parser.add_argument("--threshold", type=float, default=0.5, help="Fake probability threshold.")
    parser.add_argument("--quality", type=int, default=90, help="JPEG recompression quality for ELA.")
    parser.add_argument("--size", type=int, default=224, help="Input size expected by the CNN.")
    return parser


def main(argv: list[str] | None = None) -> dict[str, float | str | bool | None]:
    args = build_parser().parse_args(argv)
    result = predict_certificate(
        image_path=args.image,
        model_path=args.model,
        threshold=args.threshold,
        quality=args.quality,
        size=args.size,
        cert_type=args.cert_type,
    )

    if not result.get("valid", True):
        print("Invalid Format: The uploaded image does not appear to be a certificate.")
        if result["cert_type"]:
            print(f"Certificate Type: {result['cert_type']}")
        return result

    print(result["label"])
    if result["cert_type"]:
        print(f"Certificate Type: {result['cert_type']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Fake probability: {result['fake_probability']:.2%}")
    return result


if __name__ == "__main__":
    main()
