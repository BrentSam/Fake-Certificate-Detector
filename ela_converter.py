from __future__ import annotations

import argparse
import io
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
DEFAULT_LABELS = ("real", "fake")
RESAMPLE_FILTER = getattr(getattr(Image, "Resampling", Image), "LANCZOS")


def is_supported_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def make_ela_image(image_path: str | Path, quality: int = 90, size: int | None = 128) -> Image.Image:
    """Create an Error Level Analysis image from one input image."""
    image_path = Path(image_path)

    with Image.open(image_path) as original:
        original_rgb = original.convert("RGB")

    compressed_bytes = io.BytesIO()
    original_rgb.save(compressed_bytes, format="JPEG", quality=quality)
    compressed_bytes.seek(0)

    with Image.open(compressed_bytes) as compressed:
        compressed_rgb = compressed.convert("RGB")
        diff = ImageChops.difference(original_rgb, compressed_rgb)

    extrema = diff.getextrema()
    max_diff = max(channel_max for _channel_min, channel_max in extrema)
    scale = 255.0 / max_diff if max_diff else 1.0
    ela_image = ImageEnhance.Brightness(diff).enhance(scale)

    if size:
        ela_image = ela_image.resize((size, size), RESAMPLE_FILTER)

    return ela_image


def iter_label_images(input_root: Path, label: str) -> list[Path]:
    label_dir = input_root / label
    if not label_dir.exists():
        return []
    return sorted(path for path in label_dir.rglob("*") if is_supported_image(path))


def convert_dataset(
    input_root: str | Path = "dataset",
    output_root: str | Path = "ela_images",
    labels: tuple[str, ...] = DEFAULT_LABELS,
    quality: int = 90,
    size: int | None = 128,
    fail_fast: bool = False,
) -> dict[str, int]:
    """Convert labeled certificate images into labeled ELA images."""
    input_root = Path(input_root)
    output_root = Path(output_root)
    counts = {label: 0 for label in labels}

    for label in labels:
        label_input_dir = input_root / label
        label_output_dir = output_root / label
        label_output_dir.mkdir(parents=True, exist_ok=True)

        for source_path in iter_label_images(input_root, label):
            relative_path = source_path.relative_to(label_input_dir)
            target_path = (label_output_dir / relative_path).with_suffix(".jpg")
            target_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                ela_image = make_ela_image(source_path, quality=quality, size=size)
                ela_image.save(target_path, "JPEG")
                counts[label] += 1
            except (OSError, UnidentifiedImageError) as exc:
                message = f"Skipping unreadable image: {source_path} ({exc})"
                if fail_fast:
                    raise RuntimeError(message) from exc
                print(message)

    return counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert certificate images to ELA images.")
    parser.add_argument("--input", default="dataset", help="Dataset root containing real/ and fake/ folders.")
    parser.add_argument("--output", default="ela_images", help="Output root for ELA images.")
    parser.add_argument("--quality", type=int, default=90, help="JPEG recompression quality for ELA.")
    parser.add_argument("--size", type=int, default=128, help="Output image size in pixels. Use 0 to keep original size.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on the first unreadable image.")
    return parser


def main(argv: list[str] | None = None) -> dict[str, int]:
    args = build_parser().parse_args(argv)
    output_size = args.size if args.size > 0 else None
    counts = convert_dataset(
        input_root=args.input,
        output_root=args.output,
        quality=args.quality,
        size=output_size,
        fail_fast=args.fail_fast,
    )

    print("ELA conversion complete.")
    for label, count in counts.items():
        print(f"{label}: {count} image(s)")
    return counts


if __name__ == "__main__":
    main()
