from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


IMAGE_SIZE = (1000, 700)
DEFAULT_COUNT_PER_CLASS = 50
DEFAULT_OUTPUT_ROOT = Path("dataset")
DEFAULT_LOG_PATH = Path("docs") / "synthetic_dataset_log.csv"
DEFAULT_SEED = 1337

REAL_PREFIX = "synthetic_real"
FAKE_PREFIX = "synthetic_fake"

EDIT_TYPES = (
    "name_change",
    "date_change",
    "issuer_change",
    "seal_shift",
    "signature_change",
    "award_text_change",
)

FIRST_NAMES = (
    "Aarav",
    "Ananya",
    "Diya",
    "Ishaan",
    "Kabir",
    "Meera",
    "Nisha",
    "Rohan",
    "Saanvi",
    "Vivaan",
)

LAST_NAMES = (
    "Agarwal",
    "Banerjee",
    "Gupta",
    "Iyer",
    "Kapoor",
    "Menon",
    "Nair",
    "Rao",
    "Sharma",
    "Verma",
)

ISSUERS = (
    "Northbridge Technologies",
    "BluePeak Analytics",
    "Crescent Labs",
    "Vertex Software Institute",
    "Aurora Digital Academy",
    "Pioneer Cloud Systems",
)

PROGRAMS = (
    "Data Analytics Internship",
    "Web Development Internship",
    "Machine Learning Internship",
    "Cybersecurity Internship",
    "Cloud Engineering Internship",
    "UI Engineering Internship",
)

SIGNERS = (
    "Program Director",
    "Training Coordinator",
    "Head of Operations",
    "Academic Mentor",
)

ACCENT_COLORS = (
    (25, 100, 126),
    (121, 80, 38),
    (86, 91, 159),
    (40, 128, 92),
    (148, 70, 70),
)


@dataclass(frozen=True)
class CertificateFields:
    holder_name: str
    issuer: str
    program: str
    signer_title: str
    start_date: str
    end_date: str
    serial: str
    accent: tuple[int, int, int]


@dataclass(frozen=True)
class DatasetRecord:
    filename: str
    class_label: str
    source_type: str
    edit_type: str
    base_image: str
    notes: str


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    windows_font_dir = Path("C:/Windows/Fonts")
    candidates = (
        windows_font_dir / ("arialbd.ttf" if bold else "arial.ttf"),
        windows_font_dir / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        windows_font_dir / ("calibrib.ttf" if bold else "calibri.ttf"),
    )

    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)

    return ImageFont.load_default()


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), text, font=font)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    left, _top, right, _bottom = text_bbox(draw, text, font)
    return right - left


def draw_centered(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    width: int = IMAGE_SIZE[0],
) -> None:
    x = (width - text_width(draw, text, font)) // 2
    draw.text((x, y), text, fill=fill, font=font)


def draw_signature(draw: ImageDraw.ImageDraw, x: int, y: int, accent: tuple[int, int, int], rng: random.Random) -> None:
    points = []
    for index in range(12):
        px = x + index * 16
        py = y + rng.randint(-12, 12)
        points.append((px, py))

    draw.line(points, fill=accent, width=3, joint="curve")
    draw.line((x - 10, y + 28, x + 205, y + 28), fill=(88, 88, 88), width=2)


def draw_seal(draw: ImageDraw.ImageDraw, center: tuple[int, int], accent: tuple[int, int, int], issuer: str) -> None:
    x, y = center
    radius = 58
    outer = (x - radius, y - radius, x + radius, y + radius)
    inner = (x - radius + 12, y - radius + 12, x + radius - 12, y + radius - 12)
    draw.ellipse(outer, outline=accent, width=5)
    draw.ellipse(inner, outline=accent, width=2)

    initials = "".join(word[0] for word in issuer.split()[:3]).upper()
    font = load_font(22, bold=True)
    draw_centered(draw, y - 14, initials, font, accent, width=x * 2)


def random_fields(index: int, rng: random.Random) -> CertificateFields:
    start_year = rng.randint(2022, 2025)
    start_month = rng.randint(1, 9)
    duration_months = rng.randint(1, 5)
    end_month = min(start_month + duration_months, 12)

    return CertificateFields(
        holder_name=f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
        issuer=rng.choice(ISSUERS),
        program=rng.choice(PROGRAMS),
        signer_title=rng.choice(SIGNERS),
        start_date=f"{start_month:02d}/01/{start_year}",
        end_date=f"{end_month:02d}/28/{start_year}",
        serial=f"FCD-{start_year}-{index:04d}",
        accent=rng.choice(ACCENT_COLORS),
    )


def draw_certificate(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (252, 250, 244))
    draw = ImageDraw.Draw(image)

    accent = fields.accent
    title_font = load_font(46, bold=True)
    subtitle_font = load_font(21)
    body_font = load_font(24)
    body_bold = load_font(26, bold=True)
    name_font = load_font(43, bold=True)
    small_font = load_font(17)

    draw.rectangle((35, 35, 965, 665), outline=accent, width=6)
    draw.rectangle((56, 56, 944, 644), outline=(206, 188, 126), width=2)
    draw.line((90, 150, 910, 150), fill=accent, width=2)

    draw_centered(draw, 64, "CERTIFICATE OF INTERNSHIP", title_font, accent)
    draw_centered(draw, 122, fields.issuer.upper(), subtitle_font, (72, 72, 72))
    draw_centered(draw, 188, "This certifies that", body_font, (86, 86, 86))
    draw_centered(draw, 240, fields.holder_name, name_font, (30, 30, 30))
    draw_centered(draw, 310, "has successfully completed the", body_font, (86, 86, 86))
    draw_centered(draw, 355, fields.program, body_bold, accent)
    draw_centered(
        draw,
        410,
        f"from {fields.start_date} to {fields.end_date}",
        body_font,
        (86, 86, 86),
    )

    draw_signature(draw, 155, 542, accent, rng)
    draw.text((150, 586), fields.signer_title, fill=(72, 72, 72), font=small_font)
    draw.text((150, 610), fields.issuer, fill=(72, 72, 72), font=small_font)
    draw.text((690, 610), f"Certificate ID: {fields.serial}", fill=(72, 72, 72), font=small_font)
    draw_seal(draw, (800, 535), accent, fields.issuer)

    for _ in range(40):
        x1 = rng.randint(65, 935)
        y1 = rng.randint(170, 625)
        x2 = x1 + rng.randint(10, 28)
        y2 = y1 + rng.randint(0, 10)
        draw.line((x1, y1, x2, y2), fill=(246, 241, 226), width=1)

    return image.filter(ImageFilter.SMOOTH_MORE)


def patch_area(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], rng: random.Random) -> None:
    fill = (
        248 + rng.randint(-3, 2),
        246 + rng.randint(-3, 2),
        239 + rng.randint(-2, 3),
    )
    draw.rectangle(box, fill=fill)

    for _ in range(8):
        x1 = rng.randint(box[0], box[2])
        y1 = rng.randint(box[1], box[3])
        x2 = min(box[2], x1 + rng.randint(8, 24))
        draw.line((x1, y1, x2, y1), fill=(241, 236, 221), width=1)


def tamper_certificate(real_image_path: Path, fields: CertificateFields, edit_type: str, rng: random.Random) -> Image.Image:
    image = Image.open(real_image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    accent = tuple(max(0, value - 22) for value in fields.accent)

    if edit_type == "name_change":
        patch_area(draw, (250, 232, 750, 296), rng)
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        draw_centered(draw, 244 + rng.randint(-2, 3), name, load_font(42, bold=True), (35, 35, 35))

    elif edit_type == "date_change":
        patch_area(draw, (280, 402, 720, 452), rng)
        new_year = rng.randint(2021, 2026)
        draw_centered(
            draw,
            411 + rng.randint(-2, 2),
            f"from 01/01/{new_year} to 09/30/{new_year}",
            load_font(24),
            (82, 82, 82),
        )

    elif edit_type == "issuer_change":
        patch_area(draw, (110, 116, 890, 150), rng)
        fake_issuer = rng.choice([issuer for issuer in ISSUERS if issuer != fields.issuer])
        draw_centered(draw, 122, fake_issuer.upper(), load_font(21), (72, 72, 72))

    elif edit_type == "seal_shift":
        patch_area(draw, (730, 465, 875, 605), rng)
        draw_seal(draw, (820 + rng.randint(-8, 12), 522 + rng.randint(-8, 14)), accent, fields.issuer)

    elif edit_type == "signature_change":
        patch_area(draw, (130, 510, 380, 580), rng)
        draw_signature(draw, 150 + rng.randint(-5, 8), 548 + rng.randint(-6, 8), accent, rng)

    elif edit_type == "award_text_change":
        patch_area(draw, (240, 344, 760, 394), rng)
        changed_program = rng.choice([program for program in PROGRAMS if program != fields.program])
        draw_centered(draw, 356 + rng.randint(-2, 3), changed_program, load_font(26, bold=True), accent)

    else:
        raise ValueError(f"Unsupported edit type: {edit_type}")

    return image


def ensure_clean_synthetic_targets(output_root: Path, overwrite: bool) -> None:
    existing = []
    for label in ("real", "fake"):
        label_dir = output_root / label
        if label_dir.exists():
            existing.extend(label_dir.glob("synthetic_*.jpg"))

    if existing and not overwrite:
        raise FileExistsError(
            "Synthetic dataset files already exist. Re-run with --overwrite to replace only synthetic_*.jpg files."
        )

    if overwrite:
        for path in existing:
            path.unlink()


def write_log(records: list[DatasetRecord], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", newline="", encoding="utf-8") as log_file:
        writer = csv.DictWriter(
            log_file,
            fieldnames=("filename", "class_label", "source_type", "edit_type", "base_image", "notes"),
        )
        writer.writeheader()
        for record in records:
            writer.writerow(record.__dict__)


def generate_dataset(
    count_per_class: int = DEFAULT_COUNT_PER_CLASS,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    log_path: str | Path = DEFAULT_LOG_PATH,
    seed: int = DEFAULT_SEED,
    overwrite: bool = False,
) -> dict[str, int | str]:
    if count_per_class < 1:
        raise ValueError("count_per_class must be at least 1.")

    output_root = Path(output_root)
    log_path = Path(log_path)
    real_dir = output_root / "real"
    fake_dir = output_root / "fake"
    real_dir.mkdir(parents=True, exist_ok=True)
    fake_dir.mkdir(parents=True, exist_ok=True)
    ensure_clean_synthetic_targets(output_root, overwrite=overwrite)

    rng = random.Random(seed)
    records: list[DatasetRecord] = []

    for index in range(1, count_per_class + 1):
        fields = random_fields(index, rng)
        real_name = f"{REAL_PREFIX}_{index:04d}.jpg"
        fake_name = f"{FAKE_PREFIX}_{index:04d}.jpg"
        real_path = real_dir / real_name
        fake_path = fake_dir / fake_name

        real_image = draw_certificate(fields, rng)
        real_image.save(real_path, format="JPEG", quality=95, subsampling=0)
        records.append(
            DatasetRecord(
                filename=str(real_path.as_posix()),
                class_label="real",
                source_type="synthetic_certificate",
                edit_type="none",
                base_image="",
                notes="Generated privacy-safe certificate image.",
            )
        )

        edit_type = EDIT_TYPES[(index - 1) % len(EDIT_TYPES)]
        fake_image = tamper_certificate(real_path, fields, edit_type, rng)
        fake_image.save(fake_path, format="JPEG", quality=92, subsampling=0)
        records.append(
            DatasetRecord(
                filename=str(fake_path.as_posix()),
                class_label="fake",
                source_type="synthetic_certificate_edit",
                edit_type=edit_type,
                base_image=str(real_path.as_posix()),
                notes="Generated by locally editing a synthetic base certificate.",
            )
        )

    write_log(records, log_path)
    return {"real": count_per_class, "fake": count_per_class, "log": str(log_path)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a privacy-safe synthetic certificate dataset.")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT_PER_CLASS, help="Images per class to generate.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_ROOT), help="Dataset root with real/ and fake/ folders.")
    parser.add_argument("--log", default=str(DEFAULT_LOG_PATH), help="CSV dataset log path.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for reproducible images.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing synthetic_*.jpg files under the selected dataset root.",
    )
    return parser


def main(argv: list[str] | None = None) -> dict[str, int | str]:
    args = build_parser().parse_args(argv)
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


if __name__ == "__main__":
    main()
