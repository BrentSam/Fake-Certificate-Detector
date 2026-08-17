from __future__ import annotations

import argparse
import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat


IMAGE_SIZE = (1000, 700)
DEFAULT_COUNT_PER_CLASS = 500
DEFAULT_OUTPUT_ROOT = Path("dataset_internship")
DEFAULT_LOG_PATH = Path("docs") / "internship_synthetic_dataset_log.csv"
DEFAULT_SEED = 1337

REAL_PREFIX = "internship_real"
FAKE_PREFIX = "internship_fake"

EDIT_TYPES = (
    "name_change",
    "date_change",
    "issuer_change",
    "seal_shift",
    "signature_change",
    "award_text_change",
    "serial_change",
    "body_text_change",
    "location_change",
)

FIRST_NAMES = (
    "Aarav", "Ananya", "Diya", "Ishaan", "Kabir", "Meera",
    "Nisha", "Rohan", "Saanvi", "Vivaan", "Olivia", "Noah",
    "Liam", "Emma", "Ava", "Sophia", "Lucas", "Mia",
    "Ethan", "Isabella", "Mason", "Harper", "James", "Evelyn",
)

LAST_NAMES = (
    "Agarwal", "Banerjee", "Gupta", "Iyer", "Kapoor", "Menon",
    "Nair", "Rao", "Sharma", "Verma", "Smith", "Johnson",
    "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson",
)

ISSUERS = (
    "Northbridge Technologies", "BluePeak Analytics", "Crescent Labs",
    "Vertex Software Institute", "Aurora Digital Academy", "Pioneer Cloud Systems",
    "Global Education Board", "Oxford Assessment Centre", "Cambridge Certification",
    "Stanford Online", "MIT Open Learning", "Harvard Extension School",
    "Udacity", "Coursera", "edX", "LinkedIn Learning",
)

PROGRAMS = (
    "Data Analytics Internship", "Web Development Internship",
    "Machine Learning Internship", "Cybersecurity Internship",
    "Cloud Engineering Internship", "UI Engineering Internship",
    "Artificial Intelligence Certificate", "Blockchain Development",
    "Data Science Professional", "Software Engineering Diploma",
    "Digital Marketing Specialist", "Project Management Professional",
)

AWARD_TITLES = (
    "Certificate of Achievement", "Certificate of Excellence",
    "Certificate of Completion", "Certificate of Participation",
    "Certificate of Appreciation", "Diploma of Graduation",
    "Professional Certification", "Honorary Award",
)

CERTIFICATE_BODY_LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Cras arcu metus, feugiat vitae ante ac, aliquet tempus ante. "
    "In euismod nibh eget lacinia imperdiet.",
    "In recognition of outstanding performance and dedication "
    "to the assigned program, demonstrating exemplary skills and commitment.",
    "This certificate is awarded for successfully completing all requirements "
    "and demonstrating proficiency in the subject matter with distinction.",
    "Acknowledged for exceptional contribution, technical competence, "
    "and consistent adherence to professional standards throughout the tenure.",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
    "Recognized for successfully meeting all prescribed criteria, "
    "including coursework, assessments, and practical assignments, with merit.",
)

SIGNERS = (
    "Program Director", "Training Coordinator", "Head of Operations",
    "Academic Mentor", "Chief Executive Officer", "Department Head",
    "Chairman", "Principal", "Dean of Studies", "Registrar",
)

ACCENT_COLORS = (
    (25, 100, 126), (121, 80, 38), (86, 91, 159), (40, 128, 92), (148, 70, 70),
    (60, 60, 60), (139, 90, 43), (70, 70, 90), (100, 50, 50), (50, 100, 80),
)

FONT_POOL = (
    ("arial", "arialbd"),
    ("calibri", "calibrib"),
    ("cambria", "cambriab"),
    ("georgia", "georgiab"),
    ("times", "timesbd"),
    ("segoeui", "segoeuib"),
    ("verdana", "verdanab"),
    ("consola", "consolab"),
    ("cour", "courbd"),
    ("palatino linotype", "pala"),
    ("garamond", "gara"),
    ("book antiqua", "bkant"),
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
    award_title: str = "Certificate of Internship"
    body_text: str = ""
    single_date: str = ""
    location: str = ""


@dataclass(frozen=True)
class DatasetRecord:
    filename: str
    class_label: str
    source_type: str
    edit_type: str
    base_image: str
    notes: str


def load_font(size: int, bold: bool = False, rng: random.Random | None = None) -> ImageFont.ImageFont:
    windows_font_dir = Path("C:/Windows/Fonts")
    families = FONT_POOL
    family = rng.choice(families) if rng is not None else families[0]
    target = family[1] if bold else family[0]
    candidates = [
        windows_font_dir / f"{target}.ttf",
        windows_font_dir / f"{target}.ttc",
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    for fallback_family in families:
        for fallback_target in (fallback_family[1] if bold else fallback_family[0],):
            for ext in (".ttf", ".ttc"):
                p = windows_font_dir / f"{fallback_target}{ext}"
                if p.exists():
                    return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), text, font=font)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    left, _top, right, _bottom = text_bbox(draw, text, font)
    return right - left


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + " " + word if current else word
        if text_width(draw, test, font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [text]


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
    length = rng.randint(8, 20)
    thickness = rng.randint(2, 4)
    curvature = rng.randint(8, 24)
    spacing = rng.randint(14, 22)
    points = []
    for i in range(length):
        px = x + i * spacing
        py = y + rng.randint(-curvature, curvature)
        points.append((px, py))
    draw.line(points, fill=accent, width=thickness, joint="curve")
    line_y = y + max(curvature, 20)
    draw.line((x - 10, line_y, x + length * spacing + 10, line_y), fill=(88, 88, 88), width=2)


def draw_seal_circular(draw: ImageDraw.ImageDraw, center: tuple[int, int], accent: tuple[int, int, int], issuer: str, rng: random.Random) -> None:
    x, y = center
    radius = rng.choice([48, 58, 68])
    outer = (x - radius, y - radius, x + radius, y + radius)
    inner = (x - radius + 10, y - radius + 10, x + radius - 10, y + radius - 10)
    draw.ellipse(outer, outline=accent, width=rng.choice([4, 5, 6]))
    draw.ellipse(inner, outline=accent, width=2)
    initials = "".join(word[0] for word in issuer.split()[:3]).upper()
    font = load_font(rng.choice([18, 20, 22]), bold=True, rng=rng)
    draw_centered(draw, y - 10, initials, font, accent, width=x * 2)


def draw_seal_rectangular(draw: ImageDraw.ImageDraw, center: tuple[int, int], accent: tuple[int, int, int], issuer: str, rng: random.Random) -> None:
    x, y = center
    w = rng.choice([90, 110, 130])
    h = rng.choice([50, 60, 70])
    rect = (x - w // 2, y - h // 2, x + w // 2, y + h // 2)
    draw.rectangle(rect, outline=accent, width=rng.choice([3, 4, 5]))
    margin = 6
    inner = (rect[0] + margin, rect[1] + margin, rect[2] - margin, rect[3] - margin)
    draw.rectangle(inner, outline=accent, width=2)
    initials = "".join(word[0] for word in issuer.split()[:3]).upper()
    font = load_font(rng.choice([16, 18, 20]), bold=True, rng=rng)
    draw_centered(draw, y - 8, initials, font, accent, width=x * 2)


def draw_seal_star(draw: ImageDraw.ImageDraw, center: tuple[int, int], accent: tuple[int, int, int], issuer: str, rng: random.Random) -> None:
    x, y = center
    outer_r = rng.choice([45, 55, 65])
    inner_r = outer_r // 2
    points = 5
    star_points = []
    for i in range(points * 2):
        angle = math.pi / 2 + i * math.pi / points
        r = outer_r if i % 2 == 0 else inner_r
        px = x + r * math.cos(angle)
        py = y - r * math.sin(angle)
        star_points.append((px, py))
    draw.polygon(star_points, outline=accent, fill=None)
    draw.line(star_points + [star_points[0]], fill=accent, width=rng.choice([3, 4]))
    initials = "".join(word[0] for word in issuer.split()[:3]).upper()
    font = load_font(rng.choice([16, 18]), bold=True, rng=rng)
    draw_centered(draw, y - 8, initials, font, accent, width=x * 2)


def draw_seal(draw: ImageDraw.ImageDraw, center: tuple[int, int], accent: tuple[int, int, int], issuer: str, rng: random.Random) -> None:
    style = rng.choice(["circular", "rectangular", "star"])
    if style == "circular":
        draw_seal_circular(draw, center, accent, issuer, rng)
    elif style == "rectangular":
        draw_seal_rectangular(draw, center, accent, issuer, rng)
    else:
        draw_seal_star(draw, center, accent, issuer, rng)


def random_fields(index: int, rng: random.Random) -> CertificateFields:
    start_year = rng.randint(2020, 2025)
    start_month = rng.randint(1, 9)
    duration_months = rng.randint(1, 5)
    end_month = min(start_month + duration_months, 12)
    single_day = rng.randint(1, 28)
    single_month = rng.randint(1, 12)
    locations = (
        "New York, USA", "London, UK", "Toronto, Canada", "Sydney, Australia",
        "Singapore", "Dubai, UAE", "Berlin, Germany", "Paris, France",
        "Mumbai, India", "Tokyo, Japan", "Bangalore, India", "San Francisco, USA",
    )
    return CertificateFields(
        holder_name=f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
        issuer=rng.choice(ISSUERS),
        program=rng.choice(PROGRAMS),
        signer_title=rng.choice(SIGNERS),
        start_date=f"{start_month:02d}/01/{start_year}",
        end_date=f"{end_month:02d}/28/{start_year}",
        serial=f"FCD-{start_year}-{index:04d}",
        accent=rng.choice(ACCENT_COLORS),
        award_title=rng.choice(AWARD_TITLES),
        body_text=rng.choice(CERTIFICATE_BODY_LOREM),
        single_date=f"{single_day:02d}/{single_month:02d}/{start_year}",
        location=rng.choice(locations),
    )


def apply_background(image: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(image)
    w, h = IMAGE_SIZE
    mode = rng.choice(["gradient", "crosshatch", "noise", "flat"])
    if mode == "gradient":
        base = (252, 250, 244)
        direction = rng.choice(["v", "h"])
        size = w if direction == "v" else h
        for i in range(size):
            factor = i / size
            color = (
                int(base[0] + factor * rng.randint(-12, 12)),
                int(base[1] + factor * rng.randint(-12, 12)),
                int(base[2] + factor * rng.randint(-12, 12)),
            )
            if direction == "v":
                draw.line([(i, 0), (i, h)], fill=color, width=1)
            else:
                draw.line([(0, i), (w, i)], fill=color, width=1)
    elif mode == "crosshatch":
        for i in range(0, w, 50):
            draw.line([(i, 0), (i, h)], fill=(245, 243, 238), width=1)
        for i in range(0, h, 50):
            draw.line([(0, i), (w, i)], fill=(245, 243, 238), width=1)
        for i in range(-h, w, 80):
            draw.line([(i, 0), (i + h, h)], fill=(248, 246, 242), width=1)
    elif mode == "noise":
        for _ in range(3000):
            x = rng.randint(0, w - 1)
            y = rng.randint(0, h - 1)
            c = (
                250 + rng.randint(-6, 6),
                248 + rng.randint(-6, 6),
                242 + rng.randint(-6, 6),
            )
            draw.point((x, y), fill=c)
    else:
        draw.rectangle((0, 0, w, h), fill=(252, 250, 244))


def draw_certificate_classic_bordered(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (252, 250, 244))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    title_font = load_font(46, bold=True, rng=rng)
    subtitle_font = load_font(21, rng=rng)
    body_font = load_font(24, rng=rng)
    body_bold = load_font(26, bold=True, rng=rng)
    name_font = load_font(43, bold=True, rng=rng)
    small_font = load_font(17, rng=rng)
    draw.rectangle((35, 35, 965, 665), outline=accent, width=6)
    draw.rectangle((56, 56, 944, 644), outline=(206, 188, 126), width=2)
    draw.line((90, 150, 910, 150), fill=accent, width=2)
    draw_centered(draw, 64, "CERTIFICATE OF INTERNSHIP", title_font, accent)
    draw_centered(draw, 122, fields.issuer.upper(), subtitle_font, (72, 72, 72))
    draw_centered(draw, 188, "This certifies that", body_font, (86, 86, 86))
    draw_centered(draw, 240, fields.holder_name, name_font, (30, 30, 30))
    draw_centered(draw, 310, "has successfully completed the", body_font, (86, 86, 86))
    draw_centered(draw, 355, fields.program, body_bold, accent)
    draw_centered(draw, 410, f"from {fields.start_date} to {fields.end_date}", body_font, (86, 86, 86))
    draw_signature(draw, 155, 542, accent, rng)
    draw.text((150, 586), fields.signer_title, fill=(72, 72, 72), font=small_font)
    draw.text((150, 610), fields.issuer, fill=(72, 72, 72), font=small_font)
    draw.text((690, 610), f"Certificate ID: {fields.serial}", fill=(72, 72, 72), font=small_font)
    draw_seal(draw, (800, 535), accent, fields.issuer, rng)
    return image


def draw_certificate_modern_header_left(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (252, 250, 244))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    draw.rectangle((40, 0, 80, IMAGE_SIZE[1]), fill=accent)
    title_font = load_font(42, bold=True, rng=rng)
    subtitle_font = load_font(20, rng=rng)
    body_font = load_font(22, rng=rng)
    body_bold = load_font(24, bold=True, rng=rng)
    name_font = load_font(40, bold=True, rng=rng)
    small_font = load_font(16, rng=rng)
    draw.text((110, 70), "Certificate of Internship", fill=accent, font=title_font)
    draw.text((110, 125), fields.issuer.upper(), fill=(72, 72, 72), font=subtitle_font)
    draw_centered(draw, 200, "This certifies that", body_font, (86, 86, 86))
    draw_centered(draw, 260, fields.holder_name, name_font, (30, 30, 30))
    draw_centered(draw, 330, fields.program, body_bold, accent)
    draw_centered(draw, 400, f"{fields.start_date}  –  {fields.end_date}", body_font, (86, 86, 86))
    draw_signature(draw, 150, 540, accent, rng)
    draw.text((150, 584), fields.signer_title, fill=(72, 72, 72), font=small_font)
    draw.text((150, 606), fields.issuer, fill=(72, 72, 72), font=small_font)
    draw.text((680, 650), f"ID: {fields.serial}", fill=(72, 72, 72), font=small_font)
    draw_seal(draw, (800, 540), accent, fields.issuer, rng)
    return image


def draw_certificate_minimal_centered(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (252, 250, 244))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    title_font = load_font(48, bold=True, rng=rng)
    subtitle_font = load_font(20, rng=rng)
    body_font = load_font(22, rng=rng)
    name_font = load_font(44, bold=True, rng=rng)
    program_font = load_font(26, bold=True, rng=rng)
    small_font = load_font(16, rng=rng)
    draw_centered(draw, 90, "Certificate of Internship", title_font, accent)
    draw_centered(draw, 150, fields.issuer.upper(), subtitle_font, (100, 100, 100))
    draw_centered(draw, 220, "This certifies that", body_font, (110, 110, 110))
    draw_centered(draw, 280, fields.holder_name, name_font, (30, 30, 30))
    draw_centered(draw, 360, fields.program, program_font, accent)
    draw_centered(draw, 430, f"{fields.start_date}  –  {fields.end_date}", body_font, (110, 110, 110))
    draw_signature(draw, 200, 540, accent, rng)
    draw.text((200, 584), fields.signer_title, fill=(80, 80, 80), font=small_font)
    draw.text((200, 606), fields.issuer, fill=(80, 80, 80), font=small_font)
    draw.text((680, 650), f"Certificate ID: {fields.serial}", fill=(80, 80, 80), font=small_font)
    draw_seal(draw, (800, 540), accent, fields.issuer, rng)
    return image


def draw_certificate_formal_watermark(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (252, 250, 244))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    for y in range(0, IMAGE_SIZE[1], 35):
        draw.line((0, y, IMAGE_SIZE[0], y), fill=(245, 243, 238), width=1)
    draw.rectangle((30, 30, 970, 670), outline=accent, width=4)
    draw.rectangle((50, 50, 950, 650), outline=(180, 160, 120), width=2)
    title_font = load_font(44, bold=True, rng=rng)
    subtitle_font = load_font(20, rng=rng)
    body_font = load_font(23, rng=rng)
    name_font = load_font(42, bold=True, rng=rng)
    program_font = load_font(25, bold=True, rng=rng)
    small_font = load_font(16, rng=rng)
    draw_centered(draw, 75, "CERTIFICATE OF INTERNSHIP", title_font, accent)
    draw_centered(draw, 135, fields.issuer.upper(), subtitle_font, (72, 72, 72))
    draw_centered(draw, 210, "This certifies that", body_font, (86, 86, 86))
    draw_centered(draw, 270, fields.holder_name, name_font, (30, 30, 30))
    draw_centered(draw, 350, fields.program, program_font, accent)
    draw_centered(draw, 420, f"from {fields.start_date} to {fields.end_date}", body_font, (86, 86, 86))
    draw_signature(draw, 180, 540, accent, rng)
    draw.text((180, 584), fields.signer_title, fill=(72, 72, 72), font=small_font)
    draw.text((180, 606), fields.issuer, fill=(72, 72, 72), font=small_font)
    draw.text((680, 640), f"Certificate ID: {fields.serial}", fill=(72, 72, 72), font=small_font)
    draw_seal(draw, (800, 540), accent, fields.issuer, rng)
    return image


def draw_certificate_formal_watermark(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (252, 250, 244))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    for y in range(0, IMAGE_SIZE[1], 35):
        draw.line((0, y, IMAGE_SIZE[0], y), fill=(245, 243, 238), width=1)
    draw.rectangle((30, 30, 970, 670), outline=accent, width=4)
    draw.rectangle((50, 50, 950, 650), outline=(180, 160, 120), width=2)
    title_font = load_font(44, bold=True, rng=rng)
    subtitle_font = load_font(20, rng=rng)
    body_font = load_font(23, rng=rng)
    name_font = load_font(42, bold=True, rng=rng)
    program_font = load_font(25, bold=True, rng=rng)
    small_font = load_font(16, rng=rng)
    draw_centered(draw, 75, "CERTIFICATE OF INTERNSHIP", title_font, accent)
    draw_centered(draw, 135, fields.issuer.upper(), subtitle_font, (72, 72, 72))
    draw_centered(draw, 210, "This certifies that", body_font, (86, 86, 86))
    draw_centered(draw, 270, fields.holder_name, name_font, (30, 30, 30))
    draw_centered(draw, 350, fields.program, program_font, accent)
    draw_centered(draw, 420, f"from {fields.start_date} to {fields.end_date}", body_font, (86, 86, 86))
    draw_signature(draw, 180, 540, accent, rng)
    draw.text((180, 584), fields.signer_title, fill=(72, 72, 72), font=small_font)
    draw.text((180, 606), fields.issuer, fill=(72, 72, 72), font=small_font)
    draw.text((680, 640), f"Certificate ID: {fields.serial}", fill=(72, 72, 72), font=small_font)
    draw_seal(draw, (800, 540), accent, fields.issuer, rng)
    return image


def _draw_ornate_corner(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: tuple[int, int, int]) -> None:
    for i in range(size):
        draw.line([(x + i, y), (x + i, y + size - i)], fill=color, width=1)
        draw.line([(x, y + i), (x + size - i, y + i)], fill=color, width=1)


def _draw_ornate_border(draw: ImageDraw.ImageDraw, color: tuple[int, int, int]) -> None:
    w, h = IMAGE_SIZE
    margin = 30
    draw.rectangle((margin, margin, w - margin, h - margin), outline=color, width=3)
    draw.rectangle((margin + 10, margin + 10, w - margin - 10, h - margin - 10), outline=color, width=1)
    corner_size = 45
    _draw_ornate_corner(draw, margin, margin, corner_size, color)
    _draw_ornate_corner(draw, w - margin - corner_size, margin, corner_size, color)
    _draw_ornate_corner(draw, margin, h - margin - corner_size, corner_size, color)
    _draw_ornate_corner(draw, w - margin - corner_size, h - margin - corner_size, corner_size, color)


def draw_certificate_achievement_ornate(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (248, 246, 242))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    _draw_ornate_border(draw, accent)
    title_font = load_font(48, bold=True, rng=rng)
    subtitle_font = load_font(18, rng=rng)
    small_caps_font = load_font(16, rng=rng)
    name_font = load_font(46, bold=True, rng=rng)
    body_font = load_font(19, rng=rng)
    small_font = load_font(15, rng=rng)
    award_title = fields.award_title if fields.award_title else "Certificate of Achievement"
    draw_centered(draw, 80, award_title.upper(), title_font, (45, 45, 45))
    draw_centered(draw, 140, "THE FOLLOWING AWARD IS GIVEN TO", small_caps_font, (120, 120, 120))
    draw_centered(draw, 220, fields.holder_name, name_font, (30, 30, 30))
    draw.line((150, 280, 850, 280), fill=(180, 180, 180), width=1)
    body_lines = _wrap_text(draw, fields.body_text, body_font, 700)
    y = 310
    for line in body_lines:
        draw_centered(draw, y, line, body_font, (90, 90, 90))
        y += 28
    draw_centered(draw, 460, fields.program, small_caps_font, accent)
    if fields.single_date:
        draw_centered(draw, 500, fields.single_date, small_font, (110, 110, 110))
    draw_signature(draw, 170, 560, accent, rng)
    draw.text((170, 600), fields.signer_title, fill=(80, 80, 80), font=small_font)
    draw.text((170, 620), fields.issuer, fill=(80, 80, 80), font=small_font)
    draw.text((660, 620), f"ID: {fields.serial}", fill=(80, 80, 80), font=small_font)
    draw_seal(draw, (820, 580), accent, fields.issuer, rng)
    return image


def draw_certificate_diploma_classic(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (252, 248, 240))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    draw.rectangle((40, 40, 960, 660), outline=accent, width=5)
    draw.rectangle((55, 55, 945, 645), outline=(190, 170, 130), width=2)
    for y in range(55, 645, 20):
        draw.line((55, y, 945, y), fill=(245, 242, 236), width=1)
    title_font = load_font(40, bold=True, rng=rng)
    header_font = load_font(22, rng=rng)
    name_font = load_font(44, bold=True, rng=rng)
    body_font = load_font(20, rng=rng)
    small_font = load_font(16, rng=rng)
    draw_centered(draw, 85, "DIPLOMA", title_font, accent)
    draw_centered(draw, 140, fields.issuer.upper(), header_font, (72, 72, 72))
    draw_centered(draw, 200, "Hereby Confers Upon", body_font, (100, 100, 100))
    draw_centered(draw, 265, fields.holder_name, name_font, (30, 30, 30))
    draw_centered(draw, 340, f"The Degree of {fields.program}", body_font, accent)
    draw_centered(draw, 400, f"Awarded on {fields.single_date}", body_font, (90, 90, 90))
    draw_centered(draw, 450, f"Location: {fields.location}", small_font, (110, 110, 110))
    draw_signature(draw, 160, 540, accent, rng)
    draw.text((160, 584), fields.signer_title, fill=(72, 72, 72), font=small_font)
    draw.text((160, 606), "Chairman, Board of Trustees", fill=(72, 72, 72), font=small_font)
    draw.text((660, 606), f"Serial: {fields.serial}", fill=(72, 72, 72), font=small_font)
    draw_seal(draw, (830, 560), accent, fields.issuer, rng)
    return image


def draw_certificate_participation_modern(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (245, 245, 250))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    draw.rectangle((0, 0, 80, IMAGE_SIZE[1]), fill=accent)
    draw.rectangle((920, 0, 1000, IMAGE_SIZE[1]), fill=accent)
    title_font = load_font(38, bold=True, rng=rng)
    subtitle_font = load_font(20, rng=rng)
    name_font = load_font(42, bold=True, rng=rng)
    body_font = load_font(20, rng=rng)
    small_font = load_font(16, rng=rng)
    award_title = fields.award_title if fields.award_title else "Certificate of Participation"
    draw.text((120, 90), award_title.upper(), fill=accent, font=title_font)
    draw.text((120, 150), fields.issuer, fill=(72, 72, 72), font=subtitle_font)
    draw_centered(draw, 240, "Presented to", body_font, (100, 100, 100))
    draw_centered(draw, 300, fields.holder_name, name_font, (30, 30, 30))
    body_lines = _wrap_text(draw, fields.body_text, body_font, 760)
    y = 370
    for line in body_lines[:3]:
        draw_centered(draw, y, line, body_font, (90, 90, 90))
        y += 26
    draw_centered(draw, 470, fields.program, subtitle_font, accent)
    draw_signature(draw, 180, 540, accent, rng)
    draw.text((180, 584), fields.signer_title, fill=(80, 80, 80), font=small_font)
    draw.text((640, 584), f"Ref: {fields.serial}", fill=(80, 80, 80), font=small_font)
    draw_seal(draw, (820, 560), accent, fields.issuer, rng)
    return image


def draw_certificate_appreciation_floral(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (255, 252, 248))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    for y in range(0, IMAGE_SIZE[1], 25):
        draw.line((0, y, IMAGE_SIZE[0], y), fill=(250, 248, 244), width=1)
    for x in range(0, IMAGE_SIZE[0], 25):
        draw.line((x, 0, x, IMAGE_SIZE[1]), fill=(250, 248, 244), width=1)
    draw.rectangle((35, 35, 965, 665), outline=accent, width=4)
    draw.rectangle((48, 48, 952, 652), outline=(200, 180, 140), width=1)
    title_font = load_font(42, bold=True, rng=rng)
    subtitle_font = load_font(20, rng=rng)
    name_font = load_font(44, bold=True, rng=rng)
    body_font = load_font(21, rng=rng)
    small_font = load_font(16, rng=rng)
    award_title = fields.award_title if fields.award_title else "Certificate of Appreciation"
    draw_centered(draw, 90, award_title.upper(), title_font, accent)
    draw_centered(draw, 150, fields.issuer.upper(), subtitle_font, (72, 72, 72))
    draw_centered(draw, 230, "Is Proudly Presented To", body_font, (100, 100, 100))
    draw_centered(draw, 290, fields.holder_name, name_font, (30, 30, 30))
    body_lines = _wrap_text(draw, fields.body_text, body_font, 720)
    y = 340
    for line in body_lines[:3]:
        draw_centered(draw, y, line, body_font, (90, 90, 90))
        y += 28
    draw_centered(draw, 450, f"Program: {fields.program}", subtitle_font, accent)
    draw_centered(draw, 490, f"Date: {fields.single_date}", small_font, (110, 110, 110))
    draw_signature(draw, 170, 540, accent, rng)
    draw.text((170, 584), fields.signer_title, fill=(80, 80, 80), font=small_font)
    draw.text((170, 606), fields.issuer, fill=(80, 80, 80), font=small_font)
    draw.text((660, 606), f"ID: {fields.serial}", fill=(80, 80, 80), font=small_font)
    draw_seal(draw, (830, 570), accent, fields.issuer, rng)
    return image


def draw_certificate_completion_minimal_dark(fields: CertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (245, 245, 245))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    dark_accent = tuple(max(0, c - 40) for c in accent)
    draw.rectangle((30, 30, 970, 670), outline=dark_accent, width=5)
    draw.rectangle((50, 50, 950, 650), outline=(140, 140, 140), width=1)
    title_font = load_font(46, bold=True, rng=rng)
    subtitle_font = load_font(20, rng=rng)
    name_font = load_font(44, bold=True, rng=rng)
    body_font = load_font(20, rng=rng)
    small_font = load_font(16, rng=rng)
    award_title = fields.award_title if fields.award_title else "Certificate of Completion"
    draw_centered(draw, 85, award_title.upper(), title_font, dark_accent)
    draw_centered(draw, 150, fields.issuer.upper(), subtitle_font, (80, 80, 80))
    draw_centered(draw, 230, "This Certifies That", body_font, (100, 100, 100))
    draw_centered(draw, 290, fields.holder_name, name_font, (35, 35, 35))
    body_lines = _wrap_text(draw, fields.body_text, body_font, 740)
    y = 350
    for line in body_lines[:3]:
        draw_centered(draw, y, line, body_font, (90, 90, 90))
        y += 26
    draw_centered(draw, 450, f"Completed: {fields.program}", subtitle_font, dark_accent)
    if fields.single_date:
        draw_centered(draw, 490, f"Date of Completion: {fields.single_date}", small_font, (110, 110, 110))
    draw_signature(draw, 170, 540, dark_accent, rng)
    draw.text((170, 584), fields.signer_title, fill=(80, 80, 80), font=small_font)
    draw.text((170, 606), fields.issuer, fill=(80, 80, 80), font=small_font)
    draw.text((660, 606), f"Cert ID: {fields.serial}", fill=(80, 80, 80), font=small_font)
    draw_seal(draw, (830, 570), dark_accent, fields.issuer, rng)
    return image


def draw_certificate(fields: CertificateFields, rng: random.Random) -> Image.Image:
    template = rng.choice([
        draw_certificate_classic_bordered,
        draw_certificate_modern_header_left,
        draw_certificate_minimal_centered,
        draw_certificate_formal_watermark,
        draw_certificate_achievement_ornate,
        draw_certificate_diploma_classic,
        draw_certificate_participation_modern,
        draw_certificate_appreciation_floral,
        draw_certificate_completion_minimal_dark,
    ])
    return template(fields, rng)


def patch_area(image: Image.Image, draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], rng: random.Random) -> None:
    x0, y0, x1, y1 = box
    crop = image.crop(box)
    stat = ImageStat.Stat(crop)
    mean = [int(c) for c in stat.mean[:3]]
    draw.rectangle(box, fill=tuple(mean))
    for _ in range(rng.randint(20, 50)):
        lx0 = rng.randint(x0, x1)
        ly0 = rng.randint(y0, y1)
        lx1 = min(x1, lx0 + rng.randint(10, 50))
        ly1 = ly0 + rng.randint(-3, 3)
        noise = (
            mean[0] + rng.randint(-10, 10),
            mean[1] + rng.randint(-10, 10),
            mean[2] + rng.randint(-10, 10),
        )
        draw.line((lx0, ly0, lx1, ly1), fill=noise, width=1)


def tamper_certificate(real_image_path: Path, fields: CertificateFields, edit_type: str, rng: random.Random) -> Image.Image:
    image = Image.open(real_image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    accent = tuple(max(0, value - 22) for value in fields.accent)
    if edit_type == "name_change":
        patch_area(image, draw, (250, 232, 750, 296), rng)
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        draw_centered(draw, 244 + rng.randint(-2, 3), name, load_font(42, bold=True, rng=rng), (35, 35, 35))
    elif edit_type == "date_change":
        patch_area(image, draw, (280, 402, 720, 452), rng)
        new_year = rng.randint(2021, 2026)
        draw_centered(draw, 411 + rng.randint(-2, 2), f"from 01/01/{new_year} to 09/30/{new_year}", load_font(24, rng=rng), (82, 82, 82))
    elif edit_type == "issuer_change":
        patch_area(image, draw, (110, 116, 890, 150), rng)
        fake_issuer = rng.choice([issuer for issuer in ISSUERS if issuer != fields.issuer])
        draw_centered(draw, 122, fake_issuer.upper(), load_font(21, rng=rng), (72, 72, 72))
    elif edit_type == "seal_shift":
        patch_area(image, draw, (730, 465, 875, 605), rng)
        draw_seal(draw, (820 + rng.randint(-8, 12), 522 + rng.randint(-8, 14)), accent, fields.issuer, rng)
    elif edit_type == "signature_change":
        patch_area(image, draw, (130, 510, 380, 580), rng)
        draw_signature(draw, 150 + rng.randint(-5, 8), 548 + rng.randint(-6, 8), accent, rng)
    elif edit_type == "award_text_change":
        box = (240, 344, 760, 394)
        patch_area(image, draw, box, rng)
        changed_program = rng.choice([program for program in PROGRAMS if program != fields.program])
        draw_centered(draw, 356 + rng.randint(-2, 3), changed_program, load_font(26, bold=True, rng=rng), accent)
    elif edit_type == "serial_change":
        patch_area(image, draw, (660, 606, 900, 640), rng)
        fake_serial = f"FCD-{rng.randint(2018, 2027)}-{rng.randint(1, 9999):04d}"
        draw.text((660 + rng.randint(-3, 3), 610), f"Cert ID: {fake_serial}", fill=(80, 80, 80), font=load_font(16, rng=rng))
    elif edit_type == "body_text_change":
        patch_area(image, draw, (150, 310, 850, 430), rng)
        fake_body = rng.choice(CERTIFICATE_BODY_LOREM)
        fake_lines = _wrap_text(draw, fake_body, load_font(19, rng=rng), 700)
        y = 320 + rng.randint(-3, 3)
        for line in fake_lines[:3]:
            draw_centered(draw, y, line, load_font(19, rng=rng), (90, 90, 90))
            y += 28
    elif edit_type == "location_change":
        patch_area(image, draw, (350, 440, 650, 470), rng)
        fake_locations = (
            "Remote / Online", "Virtual Classroom", "Unknown Location",
            "Self-Paced Learning", "Home Study Program",
        )
        draw_centered(draw, 450 + rng.randint(-2, 2), f"Location: {rng.choice(fake_locations)}", load_font(16, rng=rng), (110, 110, 110))
    else:
        raise ValueError(f"Unsupported edit type: {edit_type}")
    return image


def _tamper_certificate_multi(image: Image.Image, fields: CertificateFields, rng: random.Random) -> tuple[Image.Image, str]:
    num_edits = rng.randint(2, 4)
    chosen = rng.sample(EDIT_TYPES, k=num_edits)
    tamper_boxes = []
    for edit_type in chosen:
        draw = ImageDraw.Draw(image)
        accent = tuple(max(0, value - 22) for value in fields.accent)
        if edit_type == "name_change":
            box = (240, 232, 760, 300)
            patch_area(image, draw, box, rng)
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            draw_centered(draw, 244 + rng.randint(-2, 3), name, load_font(42, bold=True, rng=rng), (35, 35, 35))
            tamper_boxes.append(box)
        elif edit_type == "date_change":
            box = (280, 400, 720, 456)
            patch_area(image, draw, box, rng)
            new_year = rng.randint(2021, 2026)
            draw_centered(draw, 411 + rng.randint(-2, 2), f"from 01/01/{new_year} to 09/30/{new_year}", load_font(24, rng=rng), (82, 82, 82))
            tamper_boxes.append(box)
        elif edit_type == "issuer_change":
            box = (100, 110, 900, 155)
            patch_area(image, draw, box, rng)
            fake_issuer = rng.choice([issuer for issuer in ISSUERS if issuer != fields.issuer])
            draw_centered(draw, 122, fake_issuer.upper(), load_font(21, rng=rng), (72, 72, 72))
            tamper_boxes.append(box)
        elif edit_type == "seal_shift":
            box = (730, 465, 875, 605)
            patch_area(image, draw, box, rng)
            draw_seal(draw, (820 + rng.randint(-8, 12), 522 + rng.randint(-8, 14)), accent, fields.issuer, rng)
            tamper_boxes.append(box)
        elif edit_type == "signature_change":
            box = (130, 510, 400, 590)
            patch_area(image, draw, box, rng)
            draw_signature(draw, 150 + rng.randint(-5, 8), 548 + rng.randint(-6, 8), accent, rng)
            tamper_boxes.append(box)
        elif edit_type == "award_text_change":
            box = (240, 344, 760, 400)
            patch_area(image, draw, box, rng)
            changed_program = rng.choice([program for program in PROGRAMS if program != fields.program])
            draw_centered(draw, 356 + rng.randint(-2, 3), changed_program, load_font(26, bold=True, rng=rng), accent)
            tamper_boxes.append(box)
        elif edit_type == "serial_change":
            box = (660, 606, 900, 640)
            patch_area(image, draw, box, rng)
            fake_serial = f"FCD-{rng.randint(2018, 2027)}-{rng.randint(1, 9999):04d}"
            draw.text((660 + rng.randint(-3, 3), 610), f"Cert ID: {fake_serial}", fill=(80, 80, 80), font=load_font(16, rng=rng))
            tamper_boxes.append(box)
        elif edit_type == "body_text_change":
            box = (150, 310, 850, 430)
            patch_area(image, draw, box, rng)
            fake_body = rng.choice(CERTIFICATE_BODY_LOREM)
            fake_lines = _wrap_text(draw, fake_body, load_font(19, rng=rng), 700)
            y = 320 + rng.randint(-3, 3)
            for line in fake_lines[:3]:
                draw_centered(draw, y, line, load_font(19, rng=rng), (90, 90, 90))
                y += 28
            tamper_boxes.append(box)
        elif edit_type == "location_change":
            box = (350, 440, 650, 470)
            patch_area(image, draw, box, rng)
            fake_locations = (
                "Remote / Online", "Virtual Classroom", "Unknown Location",
                "Self-Paced Learning", "Home Study Program",
            )
            draw_centered(draw, 450 + rng.randint(-2, 2), f"Location: {rng.choice(fake_locations)}", load_font(16, rng=rng), (110, 110, 110))
            tamper_boxes.append(box)
        else:
            raise ValueError(f"Unsupported edit type: {edit_type}")
    if tamper_boxes and rng.random() < 0.7:
        x0 = max(0, min(b[0] for b in tamper_boxes) - 20)
        y0 = max(0, min(b[1] for b in tamper_boxes) - 20)
        x1 = min(IMAGE_SIZE[0], max(b[2] for b in tamper_boxes) + 20)
        y1 = min(IMAGE_SIZE[1], max(b[3] for b in tamper_boxes) + 20)
        region = image.crop((x0, y0, x1, y1))
        if rng.random() < 0.5:
            region = region.filter(ImageFilter.GaussianBlur(radius=0.6))
        else:
            region = region.filter(ImageFilter.SHARPEN)
        image.paste(region, (x0, y0))
    edit_summary = "+".join(chosen)
    return image, edit_summary


def add_realism(image: Image.Image, rng: random.Random) -> Image.Image:
    angle = rng.uniform(-1.0, 1.0)
    bg = (252, 250, 244)
    rotated = image.rotate(angle, resample=Image.BILINEAR, expand=False, fillcolor=bg)
    pixels = rotated.load()
    w, h = rotated.size
    step = 3
    strength = 4
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b = pixels[x, y]
            v = rng.randint(-strength, strength)
            c = (max(0, min(255, r + v)), max(0, min(255, g + v)), max(0, min(255, b + v)))
            for dy in range(step):
                for dx in range(step):
                    nx, ny = x + dx, y + dy
                    if nx < w and ny < h:
                        pixels[nx, ny] = c
    return rotated.filter(ImageFilter.GaussianBlur(radius=0.8))


def ensure_clean_synthetic_targets(output_root: Path, overwrite: bool) -> None:
    existing = []
    for label in ("real", "fake"):
        label_dir = output_root / label
        if label_dir.exists():
            existing.extend(label_dir.glob("internship_*.jpg"))
    if existing and not overwrite:
        raise FileExistsError(
            "Synthetic internship dataset files already exist. Re-run with --overwrite to replace only internship_*.jpg files."
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


def draw_forged_certificate(fields: CertificateFields, rng: random.Random) -> Image.Image:
    """Draw a professional-looking fake certificate with subtle forensic artifacts.

    The certificate looks visually real but contains forensic inconsistencies
    that ELA can detect: different compression levels, resized pasted elements,
    mismatched noise patterns, and visible seams at paste boundaries.
    """
    import io

    # Start with a real-looking certificate template
    image = draw_certificate(fields, rng)
    pristine = image.copy()

    # Artifact 1: Seal copied from a "different source" with different compression
    if rng.random() < 0.8:
        seal_box = (750, 480, 900, 620)
        seal_region = image.crop(seal_box)
        seal_buffer = io.BytesIO()
        seal_region.save(seal_buffer, format="JPEG", quality=rng.randint(30, 65))
        seal_buffer.seek(0)
        with Image.open(seal_buffer) as compressed_seal:
            image.paste(compressed_seal.convert("RGB"), seal_box[:2])

    # Artifact 2: Signature area resized up/down creating interpolation artifacts
    if rng.random() < 0.8:
        sig_box = (130, 510, 380, 580)
        sig_region = image.crop(sig_box)
        # Resize up then down to create visible artifacts
        scale = rng.choice([1.5, 2.0, 0.5])
        sig_resized = sig_region.resize((int(sig_region.width * scale), int(sig_region.height * scale)), Image.NEAREST)
        sig_resized = sig_resized.resize((sig_region.width, sig_region.height), Image.BILINEAR)
        image.paste(sig_resized, sig_box[:2])

    # Artifact 3: Name text region with different noise/compression pattern
    if rng.random() < 0.7:
        name_box = (200, 220, 800, 300)
        name_region = image.crop(name_box)
        name_buffer = io.BytesIO()
        name_region.save(name_buffer, format="JPEG", quality=rng.randint(40, 65))
        name_buffer.seek(0)
        with Image.open(name_buffer) as compressed_name:
            image.paste(compressed_name.convert("RGB"), name_box[:2])

    # Artifact 4: Apply different JPEG compression to left and right halves
    if rng.random() < 0.6:
        mid_x = rng.randint(480, 520)
        left_half = image.crop((0, 0, mid_x, IMAGE_SIZE[1]))
        right_half = image.crop((mid_x, 0, IMAGE_SIZE[0], IMAGE_SIZE[1]))
        left_buffer = io.BytesIO()
        right_buffer = io.BytesIO()
        left_half.save(left_buffer, format="JPEG", quality=rng.randint(40, 65))
        right_half.save(right_buffer, format="JPEG", quality=rng.randint(85, 98))
        left_buffer.seek(0)
        right_buffer.seek(0)
        with Image.open(left_buffer) as l, Image.open(right_buffer) as r:
            image.paste(l.convert("RGB"), (0, 0))
            image.paste(r.convert("RGB"), (mid_x, 0))

    # Artifact 5: Date region with different quality
    if rng.random() < 0.7:
        date_box = (250, 400, 750, 460)
        date_region = image.crop(date_box)
        date_buffer = io.BytesIO()
        date_region.save(date_buffer, format="JPEG", quality=rng.randint(35, 60))
        date_buffer.seek(0)
        with Image.open(date_buffer) as compressed_date:
            image.paste(compressed_date.convert("RGB"), date_box[:2])

    # Artifact 6: Bottom strip (signatures + seal area) with lower quality
    if rng.random() < 0.7:
        bottom_box = (100, 500, 900, 660)
        bottom_region = image.crop(bottom_box)
        bottom_buffer = io.BytesIO()
        bottom_region.save(bottom_buffer, format="JPEG", quality=rng.randint(40, 65))
        bottom_buffer.seek(0)
        with Image.open(bottom_buffer) as compressed_bottom:
            image.paste(compressed_bottom.convert("RGB"), bottom_box[:2])

    # Artifact 7: Add a very subtle seam line at random boundary
    if rng.random() < 0.5:
        draw = ImageDraw.Draw(image)
        seam_x = rng.randint(300, 700)
        draw.line([(seam_x, 40), (seam_x, 660)], fill=(248, 246, 242), width=rng.choice([1, 2]))

    # Artifact 8: Internship specific - Seal double-pasting (ghosting)
    if rng.random() < 0.5:
        seal_box = (760, 490, 890, 610)
        seal_region = image.crop(seal_box)
        # Paste with a small offset
        dx = rng.randint(3, 8)
        dy = rng.randint(3, 8)
        image.paste(seal_region, (seal_box[0] + dx, seal_box[1] + dy))

    # Artifact 9: Internship specific - Period date mismatch text overlay (e.g. wrong dates drawn on top)
    if rng.random() < 0.4:
        draw = ImageDraw.Draw(image)
        # Draw mismatched date range in a different, obvious font on top of the date box to create local seam
        mismatched_font = load_font(22, rng=rng)
        bad_date_str = f"from 06/01/2026 to 02/15/2021"  # impossible backwards date
        draw_centered(draw, 411 + rng.randint(-1, 1), bad_date_str, mismatched_font, (50, 50, 50))

    return image


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
        pristine = real_image.copy()
        real_image = add_realism(real_image, rng)
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

        # Split fake generation: 50% edited real, 50% completely forged from scratch
        if index % 2 == 1:
            fake_image, edit_types = _tamper_certificate_multi(pristine, fields, rng)
            fake_image = add_realism(fake_image, rng)
            import io
            buf = io.BytesIO()
            buf_quality = rng.randint(50, 70)
            fake_image.save(buf, format="JPEG", quality=buf_quality, subsampling=0)
            buf.seek(0)
            fake_image = Image.open(buf).convert("RGB")
            quality = rng.randint(55, 80)
            fake_image.save(fake_path, format="JPEG", quality=quality, subsampling=0)
            records.append(
                DatasetRecord(
                    filename=str(fake_path.as_posix()),
                    class_label="fake",
                    source_type="synthetic_certificate_edit",
                    edit_type=edit_types,
                    base_image=str(real_path.as_posix()),
                    notes="Generated by locally editing a synthetic base certificate.",
                )
            )
        else:
            forged_image = draw_forged_certificate(fields, rng)
            forged_image = add_realism(forged_image, rng)
            import io
            buf = io.BytesIO()
            buf_quality = rng.randint(50, 70)
            forged_image.save(buf, format="JPEG", quality=buf_quality, subsampling=0)
            buf.seek(0)
            forged_image = Image.open(buf).convert("RGB")
            quality = rng.randint(55, 80)
            forged_image.save(fake_path, format="JPEG", quality=quality, subsampling=0)
            records.append(
                DatasetRecord(
                    filename=str(fake_path.as_posix()),
                    class_label="fake",
                    source_type="synthetic_certificate_forged",
                    edit_type="fully_forged",
                    base_image="",
                    notes="Generated as a completely forged certificate with subtle inconsistencies.",
                )
            )

    write_log(records, log_path)
    return {"real": count_per_class, "fake": count_per_class, "log": str(log_path)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a privacy-safe synthetic internship certificate dataset.")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT_PER_CLASS, help="Images per class to generate.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_ROOT), help="Dataset root with real/ and fake/ folders.")
    parser.add_argument("--log", default=str(DEFAULT_LOG_PATH), help="CSV dataset log path.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for reproducible images.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing internship_*.jpg files under the selected dataset root.",
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
