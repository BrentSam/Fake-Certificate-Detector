from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path


IMAGE_SIZE = (128, 128)
CLASS_NAMES = ["real", "fake"]
DEFAULT_MODEL_PATH = Path("model") / "certificate_cnn.keras"
DEFAULT_METRICS_PATH = Path("docs") / "training_metrics.json"
DEFAULT_PREDICTIONS_PATH = Path("docs") / "validation_predictions.csv"
DEFAULT_CONFUSION_MATRIX_PATH = Path("docs") / "confusion_matrix.csv"

os.environ.setdefault("MPLCONFIGDIR", str((Path.cwd() / ".matplotlib-cache").resolve()))
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")


def require_tensorflow():
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit(
            "TensorFlow is required for training. Install dependencies with: "
            "pip install -r requirements.txt"
        ) from exc
    tf.get_logger().setLevel("ERROR")
    return tf


def build_cnn_model(tf, image_size: tuple[int, int] = IMAGE_SIZE):
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(image_size[0], image_size[1], 3)),
            tf.keras.layers.Rescaling(1.0 / 255),
            tf.keras.layers.Conv2D(32, (3, 3), activation="relu"),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(128, (3, 3), activation="relu"),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )
    return model


def load_datasets(tf, data_dir: str | Path, batch_size: int, validation_split: float, seed: int):
    data_dir = Path(data_dir)
    if not (data_dir / "real").exists() or not (data_dir / "fake").exists():
        raise SystemExit("Expected ela_images/real and ela_images/fake folders before training.")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="binary",
        class_names=CLASS_NAMES,
        validation_split=validation_split,
        subset="training",
        seed=seed,
        shuffle=True,
        image_size=IMAGE_SIZE,
        batch_size=batch_size,
    )
    validation_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="binary",
        class_names=CLASS_NAMES,
        validation_split=validation_split,
        subset="validation",
        seed=seed,
        shuffle=True,
        image_size=IMAGE_SIZE,
        batch_size=batch_size,
    )
    validation_file_paths = list(getattr(validation_ds, "file_paths", []))

    autotune = tf.data.AUTOTUNE
    return (
        train_ds.cache().shuffle(500, seed=seed).prefetch(buffer_size=autotune),
        validation_ds.cache().prefetch(buffer_size=autotune),
        validation_file_paths,
    )


def collect_validation_predictions(model, validation_ds) -> tuple[list[int], list[float]]:
    y_true = []
    probabilities_all = []

    for images, labels in validation_ds:
        probabilities = model.predict(images, verbose=0).ravel()
        y_true.extend(int(value) for value in labels.numpy().ravel())
        probabilities_all.extend(float(value) for value in probabilities)

    return y_true, probabilities_all


def calculate_binary_metrics(
    y_true: list[int],
    probabilities: list[float],
    threshold: float = 0.5,
) -> dict[str, object]:
    if len(y_true) != len(probabilities):
        raise ValueError("y_true and probabilities must have the same length.")

    y_pred = [int(value >= threshold) for value in probabilities]
    true_positive = sum(1 for actual, predicted in zip(y_true, y_pred) if actual == 1 and predicted == 1)
    true_negative = sum(1 for actual, predicted in zip(y_true, y_pred) if actual == 0 and predicted == 0)
    false_positive = sum(1 for actual, predicted in zip(y_true, y_pred) if actual == 0 and predicted == 1)
    false_negative = sum(1 for actual, predicted in zip(y_true, y_pred) if actual == 1 and predicted == 0)

    total = len(y_true)
    accuracy = (true_positive + true_negative) / total if total else 0.0
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1_score = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "class_mapping": {"real": 0, "fake": 1},
        "threshold": threshold,
        "samples": total,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "confusion_matrix": {
            "true_negative": true_negative,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "true_positive": true_positive,
        },
    }


def write_metrics_json(metrics: dict[str, object], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def write_confusion_matrix_csv(metrics: dict[str, object], output_path: str | Path) -> None:
    confusion = metrics["confusion_matrix"]
    if not isinstance(confusion, dict):
        raise ValueError("metrics must include a confusion_matrix dictionary.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["actual\\predicted", "real", "fake"])
        writer.writerow(["real", confusion["true_negative"], confusion["false_positive"]])
        writer.writerow(["fake", confusion["false_negative"], confusion["true_positive"]])


def write_validation_predictions_csv(
    y_true: list[int],
    probabilities: list[float],
    output_path: str | Path,
    validation_paths: list[str] | None = None,
    threshold: float = 0.5,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    validation_paths = validation_paths or []

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=("image_path", "actual_label", "predicted_label", "fake_probability", "is_correct"),
        )
        writer.writeheader()
        for index, (actual, probability) in enumerate(zip(y_true, probabilities)):
            predicted = int(probability >= threshold)
            writer.writerow(
                {
                    "image_path": validation_paths[index] if index < len(validation_paths) else "",
                    "actual_label": CLASS_NAMES[actual],
                    "predicted_label": CLASS_NAMES[predicted],
                    "fake_probability": f"{probability:.6f}",
                    "is_correct": str(actual == predicted).lower(),
                }
            )


def print_evaluation_report(
    model,
    validation_ds,
    validation_paths: list[str] | None = None,
    threshold: float = 0.5,
    metrics_output: str | Path | None = DEFAULT_METRICS_PATH,
    predictions_output: str | Path | None = DEFAULT_PREDICTIONS_PATH,
    confusion_matrix_output: str | Path | None = DEFAULT_CONFUSION_MATRIX_PATH,
) -> dict[str, object]:
    y_true, probabilities = collect_validation_predictions(model, validation_ds)
    y_pred = [int(value >= threshold) for value in probabilities]
    metrics = calculate_binary_metrics(y_true, probabilities, threshold=threshold)

    try:
        from sklearn.metrics import classification_report, confusion_matrix
    except ImportError:
        print("Class mapping: real=0, fake=1")
        print(f"Validation accuracy: {metrics['accuracy']:.4f}")
        print(f"Validation precision: {metrics['precision']:.4f}")
        print(f"Validation recall: {metrics['recall']:.4f}")
        print(f"Validation F1-score: {metrics['f1_score']:.4f}")
        print("Confusion matrix:")
        confusion = metrics["confusion_matrix"]
        print(f"[[{confusion['true_negative']} {confusion['false_positive']}]")
        print(f" [{confusion['false_negative']} {confusion['true_positive']}]]")
    else:
        print("Class mapping: real=0, fake=1")
        print(classification_report(y_true, y_pred, labels=[0, 1], target_names=CLASS_NAMES, zero_division=0))
        print("Confusion matrix:")
        print(confusion_matrix(y_true, y_pred, labels=[0, 1]))

    if metrics_output:
        write_metrics_json(metrics, metrics_output)
        print(f"Saved metrics to {metrics_output}")
    if predictions_output:
        write_validation_predictions_csv(y_true, probabilities, predictions_output, validation_paths, threshold)
        print(f"Saved validation predictions to {predictions_output}")
    if confusion_matrix_output:
        write_confusion_matrix_csv(metrics, confusion_matrix_output)
        print(f"Saved confusion matrix to {confusion_matrix_output}")

    return metrics


def run_training(
    data_dir: str | Path = "ela_images",
    model_path: str | Path = DEFAULT_MODEL_PATH,
    epochs: int = 10,
    batch_size: int = 16,
    validation_split: float = 0.2,
    seed: int = 1337,
    threshold: float = 0.5,
    metrics_output: str | Path | None = DEFAULT_METRICS_PATH,
    predictions_output: str | Path | None = DEFAULT_PREDICTIONS_PATH,
    confusion_matrix_output: str | Path | None = DEFAULT_CONFUSION_MATRIX_PATH,
):
    tf = require_tensorflow()
    train_ds, validation_ds, validation_paths = load_datasets(tf, data_dir, batch_size, validation_split, seed)
    model = build_cnn_model(tf)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
        )
    ]

    history = model.fit(train_ds, validation_data=validation_ds, epochs=epochs, callbacks=callbacks)
    metrics = print_evaluation_report(
        model,
        validation_ds,
        validation_paths=validation_paths,
        threshold=threshold,
        metrics_output=metrics_output,
        predictions_output=predictions_output,
        confusion_matrix_output=confusion_matrix_output,
    )

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)
    print(f"Saved model to {model_path}")
    return {"history": history.history, "metrics": metrics, "model_path": str(model_path)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train the certificate ELA CNN classifier.")
    parser.add_argument("--data", default="ela_images", help="ELA image dataset root.")
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH), help="Output model path.")
    parser.add_argument("--epochs", type=int, default=10, help="Training epochs.")
    parser.add_argument("--batch-size", type=int, default=16, help="Training batch size.")
    parser.add_argument("--validation-split", type=float, default=0.2, help="Fraction of images used for validation.")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed.")
    parser.add_argument("--threshold", type=float, default=0.5, help="Fake probability threshold for validation metrics.")
    parser.add_argument("--metrics-output", default=str(DEFAULT_METRICS_PATH), help="JSON metrics output path.")
    parser.add_argument(
        "--predictions-output",
        default=str(DEFAULT_PREDICTIONS_PATH),
        help="CSV validation prediction output path.",
    )
    parser.add_argument(
        "--confusion-matrix-output",
        default=str(DEFAULT_CONFUSION_MATRIX_PATH),
        help="CSV confusion matrix output path.",
    )
    return parser


def main(argv: list[str] | None = None):
    args = build_parser().parse_args(argv)
    return run_training(
        data_dir=args.data,
        model_path=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_split=args.validation_split,
        seed=args.seed,
        threshold=args.threshold,
        metrics_output=args.metrics_output,
        predictions_output=args.predictions_output,
        confusion_matrix_output=args.confusion_matrix_output,
    )


if __name__ == "__main__":
    main()
