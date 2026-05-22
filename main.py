from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fake Internship Certificate Detector")
    subparsers = parser.add_subparsers(dest="command", required=True)

    data_parser = subparsers.add_parser("sample-data", help="Generate a privacy-safe synthetic dataset.")
    data_parser.add_argument("--count", type=int, default=50)
    data_parser.add_argument("--output", default="dataset")
    data_parser.add_argument("--log", default="docs/synthetic_dataset_log.csv")
    data_parser.add_argument("--seed", type=int, default=1337)
    data_parser.add_argument("--overwrite", action="store_true")

    ela_parser = subparsers.add_parser("ela", help="Convert dataset images into ELA images.")
    ela_parser.add_argument("--input", default="dataset")
    ela_parser.add_argument("--output", default="ela_images")
    ela_parser.add_argument("--quality", type=int, default=90)
    ela_parser.add_argument("--size", type=int, default=128)
    ela_parser.add_argument("--fail-fast", action="store_true")

    train_parser = subparsers.add_parser("train", help="Train the CNN classifier.")
    train_parser.add_argument("--data", default="ela_images")
    train_parser.add_argument("--model", default="model/certificate_cnn.keras")
    train_parser.add_argument("--epochs", type=int, default=10)
    train_parser.add_argument("--batch-size", type=int, default=16)
    train_parser.add_argument("--validation-split", type=float, default=0.2)
    train_parser.add_argument("--seed", type=int, default=1337)
    train_parser.add_argument("--threshold", type=float, default=0.5)
    train_parser.add_argument("--metrics-output", default="docs/training_metrics.json")
    train_parser.add_argument("--predictions-output", default="docs/validation_predictions.csv")
    train_parser.add_argument("--confusion-matrix-output", default="docs/confusion_matrix.csv")

    predict_parser = subparsers.add_parser("predict", help="Predict one certificate image.")
    predict_parser.add_argument("image")
    predict_parser.add_argument("--model", default="model/certificate_cnn.keras")
    predict_parser.add_argument("--threshold", type=float, default=0.5)
    predict_parser.add_argument("--quality", type=int, default=90)
    predict_parser.add_argument("--size", type=int, default=128)

    web_parser = subparsers.add_parser("web", help="Run the optional Flask upload UI.")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=5000)
    web_parser.add_argument("--model", default="model/certificate_cnn.keras")
    web_parser.add_argument("--debug", action="store_true")

    return parser


def main(argv: list[str] | None = None):
    args = build_parser().parse_args(argv)

    if args.command == "sample-data":
        from generate_synthetic_dataset import generate_dataset

        summary = generate_dataset(
            count_per_class=args.count,
            output_root=args.output,
            log_path=args.log,
            seed=args.seed,
            overwrite=args.overwrite,
        )
        print("Synthetic dataset generation complete.")
        print(f"real: {summary['real']} image(s)")
        print(f"fake: {summary['fake']} image(s)")
        print(f"log: {summary['log']}")
        return summary

    if args.command == "ela":
        from ela_converter import convert_dataset

        size = args.size if args.size > 0 else None
        counts = convert_dataset(args.input, args.output, quality=args.quality, size=size, fail_fast=args.fail_fast)
        print("ELA conversion complete.")
        for label, count in counts.items():
            print(f"{label}: {count} image(s)")
        return counts

    if args.command == "train":
        from train_model import run_training

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

    if args.command == "predict":
        from predict import predict_certificate

        result = predict_certificate(args.image, args.model, args.threshold, args.quality, args.size)
        print(result["label"])
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Fake probability: {result['fake_probability']:.2%}")
        return result

    if args.command == "web":
        from app.web_app import create_app

        app = create_app(model_path=args.model)
        app.run(host=args.host, port=args.port, debug=args.debug)
        return None

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
