from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fake Internship & Medical Certificate Detector")
    subparsers = parser.add_subparsers(dest="command", required=True)

    data_parser = subparsers.add_parser("sample-data", help="Generate a privacy-safe synthetic internship/medical dataset.")
    data_parser.add_argument("--cert-type", choices=["internship", "medical"], default="internship")
    data_parser.add_argument("--count", type=int, default=50)
    data_parser.add_argument("--output", default=None)
    data_parser.add_argument("--log", default=None)
    data_parser.add_argument("--seed", type=int, default=1337)
    data_parser.add_argument("--overwrite", action="store_true")

    medical_data_parser = subparsers.add_parser("sample-medical-data", help="Generate a privacy-safe synthetic medical dataset.")
    medical_data_parser.add_argument("--count", type=int, default=50)
    medical_data_parser.add_argument("--output", default="dataset_medical")
    medical_data_parser.add_argument("--log", default="docs/medical_synthetic_dataset_log.csv")
    medical_data_parser.add_argument("--seed", type=int, default=1337)
    medical_data_parser.add_argument("--overwrite", action="store_true")

    ela_parser = subparsers.add_parser("ela", help="Convert dataset images into ELA images.")
    ela_parser.add_argument("--cert-type", choices=["internship", "medical"], default=None)
    ela_parser.add_argument("--input", default="dataset")
    ela_parser.add_argument("--output", default="ela_images")
    ela_parser.add_argument("--quality", type=int, default=90)
    ela_parser.add_argument("--size", type=int, default=224)
    ela_parser.add_argument("--fail-fast", action="store_true")

    train_parser = subparsers.add_parser("train", help="Train the CNN classifier.")
    train_parser.add_argument("--cert-type", choices=["internship", "medical"], default=None)
    train_parser.add_argument("--data", default="ela_images")
    train_parser.add_argument("--model", default="model/certificate_cnn.keras")
    train_parser.add_argument("--epochs", type=int, default=25)
    train_parser.add_argument("--batch-size", type=int, default=32)
    train_parser.add_argument("--validation-split", type=float, default=0.2)
    train_parser.add_argument("--seed", type=int, default=1337)
    train_parser.add_argument("--threshold", type=float, default=0.5)
    train_parser.add_argument("--metrics-output", default="docs/training_metrics.json")
    train_parser.add_argument("--predictions-output", default="docs/validation_predictions.csv")
    train_parser.add_argument("--confusion-matrix-output", default="docs/confusion_matrix.csv")
    train_parser.add_argument("--fine-tune-epochs", type=int, default=10)

    predict_parser = subparsers.add_parser("predict", help="Predict one certificate image.")
    predict_parser.add_argument("image")
    predict_parser.add_argument("--cert-type", choices=["internship", "medical"], default=None)
    predict_parser.add_argument("--model", default="model/certificate_cnn.keras")
    predict_parser.add_argument("--threshold", type=float, default=0.5)
    predict_parser.add_argument("--quality", type=int, default=90)
    predict_parser.add_argument("--size", type=int, default=224)

    web_parser = subparsers.add_parser("web", help="Run the optional Flask upload UI.")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=5000)
    web_parser.add_argument("--model-internship", default="model/internship_cnn.keras")
    web_parser.add_argument("--model-medical", default="model/medical_cnn.keras")
    web_parser.add_argument("--debug", action="store_true")

    return parser


def main(argv: list[str] | None = None):
    args = build_parser().parse_args(argv)

    if args.command == "sample-data":
        if args.cert_type == "medical":
            from generate_medical_certificates import generate_dataset
            output = args.output or "dataset_medical"
            log = args.log or "docs/medical_synthetic_dataset_log.csv"
        else:
            from generate_synthetic_dataset import generate_dataset
            output = args.output or "dataset_internship"
            log = args.log or "docs/internship_synthetic_dataset_log.csv"

        summary = generate_dataset(
            count_per_class=args.count,
            output_root=output,
            log_path=log,
            seed=args.seed,
            overwrite=args.overwrite,
        )
        print("Synthetic dataset generation complete.")
        print(f"real: {summary['real']} image(s)")
        print(f"fake: {summary['fake']} image(s)")
        print(f"log: {summary['log']}")
        return summary

    if args.command == "sample-medical-data":
        from generate_medical_certificates import generate_dataset
        summary = generate_dataset(
            count_per_class=args.count,
            output_root=args.output,
            log_path=args.log,
            seed=args.seed,
            overwrite=args.overwrite,
        )
        print("Synthetic medical dataset generation complete.")
        print(f"real: {summary['real']} image(s)")
        print(f"fake: {summary['fake']} image(s)")
        print(f"log: {summary['log']}")
        return summary

    if args.command == "ela":
        from ela_converter import convert_dataset

        input_dir = args.input
        output_dir = args.output
        if args.cert_type:
            if input_dir == "dataset":
                input_dir = f"dataset_{args.cert_type}"
            if output_dir == "ela_images":
                output_dir = f"ela_images_{args.cert_type}"

        size = args.size if args.size > 0 else None
        counts = convert_dataset(input_dir, output_dir, quality=args.quality, size=size, fail_fast=args.fail_fast)
        print("ELA conversion complete.")
        for label, count in counts.items():
            print(f"{label}: {count} image(s)")
        return counts

    if args.command == "train":
        from train_model import run_training

        cert_type = args.cert_type
        data_dir = args.data
        model_path = args.model
        metrics_output = args.metrics_output
        predictions_output = args.predictions_output
        confusion_matrix_output = args.confusion_matrix_output

        if cert_type:
            if data_dir == "ela_images":
                data_dir = f"ela_images_{cert_type}"
            if model_path == "model/certificate_cnn.keras":
                model_path = f"model/{cert_type}_cnn.keras"
            if metrics_output == "docs/training_metrics.json":
                metrics_output = f"docs/{cert_type}_training_metrics.json"
            if predictions_output == "docs/validation_predictions.csv":
                predictions_output = f"docs/{cert_type}_validation_predictions.csv"
            if confusion_matrix_output == "docs/confusion_matrix.csv":
                confusion_matrix_output = f"docs/{cert_type}_confusion_matrix.csv"

        return run_training(
            data_dir=data_dir,
            model_path=model_path,
            epochs=args.epochs,
            batch_size=args.batch_size,
            validation_split=args.validation_split,
            seed=args.seed,
            threshold=args.threshold,
            metrics_output=metrics_output,
            predictions_output=predictions_output,
            confusion_matrix_output=confusion_matrix_output,
            fine_tune_epochs=args.fine_tune_epochs,
        )

    if args.command == "predict":
        from predict import predict_certificate

        model_path = args.model
        if args.cert_type and model_path == "model/certificate_cnn.keras":
            model_path = f"model/{args.cert_type}_cnn.keras"

        result = predict_certificate(
            image_path=args.image,
            model_path=model_path,
            threshold=args.threshold,
            quality=args.quality,
            size=args.size,
            cert_type=args.cert_type
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

    if args.command == "web":
        from app.web_app import create_app

        app = create_app(model_paths={
            "internship": args.model_internship,
            "medical": args.model_medical
        })
        app.run(host=args.host, port=args.port, debug=args.debug)
        return None

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
