from __future__ import annotations

import argparse
import csv
import math
import random
import io
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

IMAGE_SIZE = (1000, 700)
DEFAULT_COUNT_PER_CLASS = 500
DEFAULT_OUTPUT_ROOT = Path("dataset_medical")
DEFAULT_LOG_PATH = Path("docs") / "medical_synthetic_dataset_log.csv"
DEFAULT_SEED = 1337

REAL_PREFIX = "medical_real"
FAKE_PREFIX = "medical_fake"

EDIT_TYPES = (
    "patient_name_change",
    "date_change",
    "doctor_name_change",
    "registration_number_change",
    "hospital_name_change",
    "diagnosis_change",
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

HOSPITALS = (
    "City General Hospital", "Apollo Medical Centre", "St. Mary's Clinic",
    "Metro Health Hospital", "Grace Memorial Hospital", "Evergreen Medical Clinic",
    "Pinecrest Health Centre", "Summit Valley Hospital", "Mercy Family Practice",
    "Trinity Health Clinic", "National University Hospital", "Johns Hopkins Medicine",
)

DOCTORS = (
    "Dr. Robert Chen, MD", "Dr. Sarah Jenkins, MD", "Dr. Amit Patel, MD",
    "Dr. Emily Watson, MD", "Dr. David Kim, MD", "Dr. Lisa Ray, MD",
    "Dr. James Carter, MD", "Dr. Maria Lopez, MD", "Dr. Michael Chang, MD",
    "Dr. Rachel Green, MD", "Dr. John Doe, MD", "Dr. Jane Smith, MD",
)

DIAGNOSES = (
    "Acute Gastroenteritis", "Upper Respiratory Tract Infection", "Viral Fever",
    "Acute Tonsillitis", "Lower Back Pain", "Severe Migraine",
    "Physical Exhaustion", "Hypertension", "Sprained Ankle",
    "Acute Bronchitis", "Post-viral Fatigue", "Fit for Duty",
    "Medical Leave Recommendation", "General Fitness Certificate",
)

DIAGNOSIS_BODIES = (
    "The patient is diagnosed with Upper Respiratory Tract Infection and is advised bed rest.",
    "The patient presented with symptoms of Acute Gastroenteritis and is unfit for duty.",
    "Diagnosed with Viral Fever. Recommended isolation and rest for the duration.",
    "The patient has been diagnosed with Acute Tonsillitis and is undergoing treatment.",
    "Sustained a Sprained Ankle. Advised to avoid strenuous physical activity.",
    "The patient is suffering from Severe Migraine and is unable to attend work.",
    "Upon examination, the patient is found Fit for Duty and in good general health.",
    "Certified that the patient is medically fit to resume normal activities.",
)

ACCENT_COLORS = (
    (25, 100, 126), (40, 128, 92), (86, 91, 159), (148, 70, 70), (60, 60, 60),
    (139, 90, 43), (70, 70, 90), (100, 50, 50), (50, 100, 80),
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
class MedicalCertificateFields:
    patient_name: str
    doctor_name: str
    hospital: str
    diagnosis: str
    date_of_issue: str
    registration_number: str
    accent: tuple[int, int, int]
    body_text: str = ""


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
    length = rng.randint(8, 18)
    thickness = rng.randint(2, 4)
    curvature = rng.randint(6, 18)
    spacing = rng.randint(12, 18)
    points = []
    for i in range(length):
        px = x + i * spacing
        py = y + rng.randint(-curvature, curvature)
        points.append((px, py))
    draw.line(points, fill=accent, width=thickness, joint="curve")
    line_y = y + 25
    draw.line((x - 10, line_y, x + length * spacing + 10, line_y), fill=(100, 100, 100), width=1)


def draw_seal_circular(draw: ImageDraw.ImageDraw, center: tuple[int, int], accent: tuple[int, int, int], hospital: str, rng: random.Random) -> None:
    x, y = center
    radius = rng.choice([45, 52, 60])
    outer = (x - radius, y - radius, x + radius, y + radius)
    inner = (x - radius + 8, y - radius + 8, x + radius - 8, y + radius - 8)
    draw.ellipse(outer, outline=accent, width=rng.choice([3, 4, 5]))
    draw.ellipse(inner, outline=accent, width=1)
    initials = "".join(word[0] for word in hospital.split()[:3]).upper()
    font = load_font(rng.choice([16, 18]), bold=True, rng=rng)
    draw_centered(draw, y - 9, initials, font, accent, width=x * 2)


def draw_seal(draw: ImageDraw.ImageDraw, center: tuple[int, int], accent: tuple[int, int, int], hospital: str, rng: random.Random) -> None:
    draw_seal_circular(draw, center, accent, hospital, rng)


def random_fields(index: int, rng: random.Random) -> MedicalCertificateFields:
    year = rng.randint(2023, 2026)
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    hosp = rng.choice(HOSPITALS)
    doc = rng.choice(DOCTORS)
    diag = rng.choice(DIAGNOSES)
    body = rng.choice(DIAGNOSIS_BODIES)
    
    # Prefix registration formats
    reg_prefix = rng.choice(["MC", "REG", "MED", "LIC"])
    reg_num = f"{reg_prefix}-{year}-{rng.randint(1000, 9999)}"
    
    return MedicalCertificateFields(
        patient_name=f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
        doctor_name=doc,
        hospital=hosp,
        diagnosis=diag,
        date_of_issue=f"{day:02d}/{month:02d}/{year}",
        registration_number=reg_num,
        accent=rng.choice(ACCENT_COLORS),
        body_text=body,
    )


def apply_background(image: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(image)
    w, h = IMAGE_SIZE
    mode = rng.choice(["gradient", "crosshatch", "noise", "flat"])
    if mode == "gradient":
        base = (250, 252, 250)
        direction = rng.choice(["v", "h"])
        size = w if direction == "v" else h
        for i in range(size):
            factor = i / size
            color = (
                int(base[0] + factor * rng.randint(-8, 8)),
                int(base[1] + factor * rng.randint(-8, 8)),
                int(base[2] + factor * rng.randint(-8, 8)),
            )
            if direction == "v":
                draw.line([(i, 0), (i, h)], fill=color, width=1)
            else:
                draw.line([(0, i), (w, i)], fill=color, width=1)
    elif mode == "crosshatch":
        for i in range(0, w, 60):
            draw.line([(i, 0), (i, h)], fill=(244, 246, 244), width=1)
        for i in range(0, h, 60):
            draw.line([(0, i), (w, i)], fill=(244, 246, 244), width=1)
    elif mode == "noise":
        for _ in range(2500):
            x = rng.randint(0, w - 1)
            y = rng.randint(0, h - 1)
            c = (
                248 + rng.randint(-5, 5),
                250 + rng.randint(-5, 5),
                248 + rng.randint(-5, 5),
            )
            draw.point((x, y), fill=c)
    else:
        draw.rectangle((0, 0, w, h), fill=(250, 252, 250))


# Template 1: Hospital Letterhead
def draw_certificate_hospital_letterhead(fields: MedicalCertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (250, 252, 250))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    
    font_hosp = load_font(28, bold=True, rng=rng)
    font_title = load_font(36, bold=True, rng=rng)
    font_body = load_font(20, rng=rng)
    font_body_bold = load_font(21, bold=True, rng=rng)
    font_small = load_font(15, rng=rng)
    
    # Outer Border
    draw.rectangle((40, 40, 960, 660), outline=accent, width=4)
    draw.rectangle((52, 52, 948, 648), outline=(200, 200, 200), width=1)
    
    # Header Hospital Name
    draw_centered(draw, 70, fields.hospital.upper(), font_hosp, accent)
    draw_centered(draw, 110, "100 Medical Plaza, Health City  |  Tel: (555) 0199", font_small, (100, 100, 100))
    draw.line((100, 140, 900, 140), fill=accent, width=2)
    
    # Title
    draw_centered(draw, 160, "OFFICIAL MEDICAL CERTIFICATE", font_title, (40, 40, 40))
    
    # Body
    draw.text((120, 240), "This is to certify that the patient", fill=(80, 80, 80), font=font_body)
    draw.text((120, 265), fields.patient_name, fill=(20, 20, 20), font=font_body_bold)
    
    draw.text((120, 315), "was examined at this facility and is diagnosed with:", fill=(80, 80, 80), font=font_body)
    draw.text((120, 340), fields.diagnosis, fill=accent, font=font_body_bold)
    
    body_lines = _wrap_text(draw, fields.body_text, font_body, 760)
    y = 390
    for line in body_lines[:2]:
        draw.text((120, y), line, fill=(80, 80, 80), font=font_body)
        y += 26
        
    draw.text((120, 450), f"Date of Examination & Issue: {fields.date_of_issue}", fill=(100, 100, 100), font=font_body)
    
    # Footer
    draw_signature(draw, 150, 540, accent, rng)
    draw.text((150, 580), fields.doctor_name, fill=(50, 50, 50), font=font_body_bold)
    draw.text((150, 605), f"Reg No: {fields.registration_number}", fill=(100, 100, 100), font=font_small)
    
    draw_seal(draw, (800, 540), accent, fields.hospital, rng)
    return image


# Template 2: Clinic Prescription style
def draw_certificate_clinic_prescription(fields: MedicalCertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (250, 252, 250))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    
    font_hosp = load_font(26, bold=True, rng=rng)
    font_title = load_font(34, bold=True, rng=rng)
    font_body = load_font(19, rng=rng)
    font_body_bold = load_font(20, bold=True, rng=rng)
    font_small = load_font(14, rng=rng)
    
    # Left vertical colored strip
    draw.rectangle((0, 0, 50, IMAGE_SIZE[1]), fill=accent)
    
    # Header Clinic Name
    draw.text((100, 65), fields.hospital, fill=accent, font=font_hosp)
    draw.text((100, 100), "Family Medicine & Urgent Care Clinic", fill=(120, 120, 120), font=font_small)
    draw.line((100, 130, 900, 130), fill=(200, 200, 200), width=1)
    
    # Title & Rx Symbol
    draw.text((100, 150), "Rx", fill=accent, font=load_font(38, bold=True, rng=rng))
    draw_centered(draw, 160, "MEDICAL EXEMPTION CERTIFICATE", font_title, (50, 50, 50))
    
    # Body
    draw.text((150, 240), "PATIENT:", fill=(100, 100, 100), font=font_small)
    draw.text((150, 260), fields.patient_name, fill=(20, 20, 20), font=font_body_bold)
    
    draw.text((150, 315), "DIAGNOSIS & CLINICAL FINDINGS:", fill=(100, 100, 100), font=font_small)
    draw.text((150, 335), fields.diagnosis, fill=(20, 20, 20), font=font_body_bold)
    
    draw.text((150, 375), "RECOMMENDATION & REMARKS:", fill=(100, 100, 100), font=font_small)
    body_lines = _wrap_text(draw, fields.body_text, font_body, 700)
    y = 395
    for line in body_lines[:2]:
        draw.text((150, y), line, fill=(80, 80, 80), font=font_body)
        y += 24
        
    draw.text((150, 455), f"Date of Issue: {fields.date_of_issue}", fill=(100, 100, 100), font=font_body)
    
    # Footer
    draw_signature(draw, 180, 540, accent, rng)
    draw.text((180, 580), fields.doctor_name, fill=(50, 50, 50), font=font_body_bold)
    draw.text((180, 605), f"Reg No: {fields.registration_number}", fill=(100, 100, 100), font=font_small)
    
    draw_seal(draw, (820, 540), accent, fields.hospital, rng)
    return image


# Template 3: Government Health Certificate
def draw_certificate_government_health(fields: MedicalCertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (250, 252, 250))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    
    font_hosp = load_font(25, bold=True, rng=rng)
    font_title = load_font(34, bold=True, rng=rng)
    font_body = load_font(19, rng=rng)
    font_body_bold = load_font(20, bold=True, rng=rng)
    font_small = load_font(14, rng=rng)
    
    # Ornate Border Style
    draw.rectangle((30, 30, 970, 670), outline=accent, width=3)
    draw.rectangle((45, 45, 955, 655), outline=(180, 180, 180), width=1)
    
    # Department Header
    draw_centered(draw, 65, "DEPARTMENT OF HEALTH & HUMAN SERVICES", font_hosp, (60, 60, 60))
    draw_centered(draw, 95, fields.hospital.upper(), font_small, accent)
    draw.line((150, 125, 850, 125), fill=accent, width=1)
    
    # Title
    draw_centered(draw, 155, "CERTIFICATE OF MEDICAL FITNESS", font_title, accent)
    
    # Body
    draw.text((120, 235), "This is to certify that we have carefully examined:", fill=(80, 80, 80), font=font_body)
    draw.text((120, 260), fields.patient_name.upper(), fill=(20, 20, 20), font=font_body_bold)
    
    draw.text((120, 310), "Medical Assessment / Diagnosis:", fill=(80, 80, 80), font=font_body)
    draw.text((120, 335), fields.diagnosis, fill=(20, 20, 20), font=font_body_bold)
    
    body_lines = _wrap_text(draw, fields.body_text, font_body, 760)
    y = 385
    for line in body_lines[:2]:
        draw.text((120, y), line, fill=(80, 80, 80), font=font_body)
        y += 25
        
    draw.text((120, 450), f"Certified Date: {fields.date_of_issue}", fill=(100, 100, 100), font=font_body)
    
    # Footer
    draw_signature(draw, 150, 540, accent, rng)
    draw.text((150, 580), fields.doctor_name, fill=(50, 50, 50), font=font_body_bold)
    draw.text((150, 605), f"Medical Board Reg: {fields.registration_number}", fill=(100, 100, 100), font=font_small)
    
    draw_seal(draw, (800, 540), accent, fields.hospital, rng)
    return image


# Template 4: Private Practice
def draw_certificate_private_practice(fields: MedicalCertificateFields, rng: random.Random) -> Image.Image:
    image = Image.new("RGB", IMAGE_SIZE, (250, 252, 250))
    apply_background(image, rng)
    draw = ImageDraw.Draw(image)
    accent = fields.accent
    
    font_hosp = load_font(27, bold=True, rng=rng)
    font_title = load_font(34, bold=True, rng=rng)
    font_body = load_font(20, rng=rng)
    font_body_bold = load_font(21, bold=True, rng=rng)
    font_small = load_font(14, rng=rng)
    
    # Minimalist border with accent corners
    draw.rectangle((40, 40, 960, 660), outline=(220, 220, 220), width=2)
    draw.line((40, 40, 140, 40), fill=accent, width=4)
    draw.line((40, 40, 40, 140), fill=accent, width=4)
    draw.line((960, 660, 860, 660), fill=accent, width=4)
    draw.line((960, 660, 960, 560), fill=accent, width=4)
    
    # Header Private Clinic
    draw.text((100, 70), fields.doctor_name, fill=accent, font=font_hosp)
    draw.text((100, 105), f"Private Practice  |  Licensed Practitioner Reg: {fields.registration_number}", fill=(110, 110, 110), font=font_small)
    draw.line((100, 135, 900, 135), fill=(220, 220, 220), width=1)
    
    # Title
    draw_centered(draw, 165, "MEDICAL SICK LEAVE CERTIFICATE", font_title, (45, 45, 45))
    
    # Body
    draw.text((120, 240), "This document serves to certify that my patient", fill=(80, 80, 80), font=font_body)
    draw.text((120, 265), fields.patient_name, fill=(20, 20, 20), font=font_body_bold)
    
    draw.text((120, 315), "is diagnosed with and treated for:", fill=(80, 80, 80), font=font_body)
    draw.text((120, 340), fields.diagnosis, fill=accent, font=font_body_bold)
    
    body_lines = _wrap_text(draw, fields.body_text, font_body, 760)
    y = 390
    for line in body_lines[:2]:
        draw.text((120, y), line, fill=(80, 80, 80), font=font_body)
        y += 26
        
    draw.text((120, 455), f"Issued at {fields.hospital} on {fields.date_of_issue}", fill=(100, 100, 100), font=font_small)
    
    # Footer
    draw_signature(draw, 150, 540, accent, rng)
    draw.text((150, 580), fields.doctor_name, fill=(50, 50, 50), font=font_body_bold)
    draw.text((150, 605), "Attending Physician Signature", fill=(120, 120, 120), font=font_small)
    
    draw_seal(draw, (800, 540), accent, fields.hospital, rng)
    return image


def draw_certificate(fields: MedicalCertificateFields, rng: random.Random) -> Image.Image:
    template = rng.choice([
        draw_certificate_hospital_letterhead,
        draw_certificate_clinic_prescription,
        draw_certificate_government_health,
        draw_certificate_private_practice,
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
            mean[0] + rng.randint(-8, 8),
            mean[1] + rng.randint(-8, 8),
            mean[2] + rng.randint(-8, 8),
        )
        draw.line((lx0, ly0, lx1, ly1), fill=noise, width=1)


def tamper_certificate(real_image_path: Path, fields: MedicalCertificateFields, edit_type: str, rng: random.Random) -> Image.Image:
    image = Image.open(real_image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    accent = tuple(max(0, value - 20) for value in fields.accent)
    
    if edit_type == "patient_name_change":
        # Bounding box roughly matching name region
        box = (120, 255, 750, 305)
        patch_area(image, draw, box, rng)
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        draw.text((120, 260 + rng.randint(-2, 2)), name, fill=(20, 20, 20), font=load_font(21, bold=True, rng=rng))
    elif edit_type == "date_change":
        # Bounding box roughly matching date region
        box = (120, 440, 800, 480)
        patch_area(image, draw, box, rng)
        new_year = rng.randint(2023, 2026)
        new_month = rng.randint(1, 12)
        new_day = rng.randint(1, 28)
        draw.text((120, 450 + rng.randint(-2, 2)), f"Date of Examination & Issue: {new_day:02d}/{new_month:02d}/{new_year}", fill=(100, 100, 100), font=load_font(20, rng=rng))
    elif edit_type == "doctor_name_change":
        # Bounding box roughly matching doctor name region
        box = (140, 570, 500, 610)
        patch_area(image, draw, box, rng)
        new_doc = rng.choice([doc for doc in DOCTORS if doc != fields.doctor_name])
        draw.text((150, 580 + rng.randint(-2, 2)), new_doc, fill=(50, 50, 50), font=load_font(21, bold=True, rng=rng))
    elif edit_type == "registration_number_change":
        # Bounding box roughly matching registration number region
        box = (140, 600, 500, 635)
        patch_area(image, draw, box, rng)
        reg_prefix = rng.choice(["MC", "REG", "MED", "LIC"])
        fake_reg = f"{reg_prefix}-{rng.randint(2023, 2026)}-{rng.randint(1000, 9999)}"
        draw.text((150, 605), f"Reg No: {fake_reg}", fill=(100, 100, 100), font=load_font(15, rng=rng))
    elif edit_type == "hospital_name_change":
        # Bounding box roughly matching hospital name at top
        box = (100, 55, 900, 120)
        patch_area(image, draw, box, rng)
        fake_hosp = rng.choice([hosp for hosp in HOSPITALS if hosp != fields.hospital])
        draw_centered(draw, 70, fake_hosp.upper(), load_font(28, bold=True, rng=rng), accent)
    elif edit_type == "diagnosis_change":
        # Bounding box roughly matching diagnosis region
        box = (120, 330, 850, 380)
        patch_area(image, draw, box, rng)
        fake_diag = rng.choice([diag for diag in DIAGNOSES if diag != fields.diagnosis])
        draw.text((120, 340 + rng.randint(-2, 2)), fake_diag, fill=accent, font=load_font(21, bold=True, rng=rng))
    else:
        raise ValueError(f"Unsupported edit type: {edit_type}")
        
    return image


def _tamper_certificate_multi(image: Image.Image, fields: MedicalCertificateFields, rng: random.Random) -> tuple[Image.Image, str]:
    num_edits = rng.randint(2, 4)
    chosen = rng.sample(EDIT_TYPES, k=num_edits)
    tamper_boxes = []
    
    for edit_type in chosen:
        draw = ImageDraw.Draw(image)
        accent = tuple(max(0, value - 20) for value in fields.accent)
        
        if edit_type == "patient_name_change":
            box = (120, 255, 750, 305)
            patch_area(image, draw, box, rng)
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            draw.text((120, 260 + rng.randint(-2, 2)), name, fill=(20, 20, 20), font=load_font(21, bold=True, rng=rng))
            tamper_boxes.append(box)
        elif edit_type == "date_change":
            box = (120, 440, 800, 480)
            patch_area(image, draw, box, rng)
            new_year = rng.randint(2023, 2026)
            new_month = rng.randint(1, 12)
            new_day = rng.randint(1, 28)
            draw.text((120, 450 + rng.randint(-2, 2)), f"Date of Examination & Issue: {new_day:02d}/{new_month:02d}/{new_year}", fill=(100, 100, 100), font=load_font(20, rng=rng))
            tamper_boxes.append(box)
        elif edit_type == "doctor_name_change":
            box = (140, 570, 500, 610)
            patch_area(image, draw, box, rng)
            new_doc = rng.choice([doc for doc in DOCTORS if doc != fields.doctor_name])
            draw.text((150, 580 + rng.randint(-2, 2)), new_doc, fill=(50, 50, 50), font=load_font(21, bold=True, rng=rng))
            tamper_boxes.append(box)
        elif edit_type == "registration_number_change":
            box = (140, 600, 500, 635)
            patch_area(image, draw, box, rng)
            reg_prefix = rng.choice(["MC", "REG", "MED", "LIC"])
            fake_reg = f"{reg_prefix}-{rng.randint(2023, 2026)}-{rng.randint(1000, 9999)}"
            draw.text((150, 605), f"Reg No: {fake_reg}", fill=(100, 100, 100), font=load_font(15, rng=rng))
            tamper_boxes.append(box)
        elif edit_type == "hospital_name_change":
            box = (100, 55, 900, 120)
            patch_area(image, draw, box, rng)
            fake_hosp = rng.choice([hosp for hosp in HOSPITALS if hosp != fields.hospital])
            draw_centered(draw, 70, fake_hosp.upper(), load_font(28, bold=True, rng=rng), accent)
            tamper_boxes.append(box)
        elif edit_type == "diagnosis_change":
            box = (120, 330, 850, 380)
            patch_area(image, draw, box, rng)
            fake_diag = rng.choice([diag for diag in DIAGNOSES if diag != fields.diagnosis])
            draw.text((120, 340 + rng.randint(-2, 2)), fake_diag, fill=accent, font=load_font(21, bold=True, rng=rng))
            tamper_boxes.append(box)
            
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
    bg = (250, 252, 250)
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
            existing.extend(label_dir.glob("medical_*.jpg"))
    if existing and not overwrite:
        raise FileExistsError(
            "Synthetic medical dataset files already exist. Re-run with --overwrite to replace only medical_*.jpg files."
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


def draw_forged_certificate(fields: MedicalCertificateFields, rng: random.Random) -> Image.Image:
    """Draw a medical certificate with ELA-detectable forensic artifacts."""
    image = draw_certificate(fields, rng)
    
    # Artifact 1: Seal copied from different source
    if rng.random() < 0.8:
        seal_box = (740, 480, 890, 620)
        seal_region = image.crop(seal_box)
        seal_buffer = io.BytesIO()
        seal_region.save(seal_buffer, format="JPEG", quality=rng.randint(30, 65))
        seal_buffer.seek(0)
        with Image.open(seal_buffer) as compressed_seal:
            image.paste(compressed_seal.convert("RGB"), seal_box[:2])
            
    # Artifact 2: Signature area interpolation artifacts
    if rng.random() < 0.8:
        sig_box = (130, 500, 380, 580)
        sig_region = image.crop(sig_box)
        scale = rng.choice([1.5, 2.0, 0.5])
        sig_resized = sig_region.resize((int(sig_region.width * scale), int(sig_region.height * scale)), Image.NEAREST)
        sig_resized = sig_resized.resize((sig_region.width, sig_region.height), Image.BILINEAR)
        image.paste(sig_resized, sig_box[:2])
        
    # Artifact 3: Name text region compression pattern mismatch
    if rng.random() < 0.7:
        name_box = (120, 245, 750, 310)
        name_region = image.crop(name_box)
        name_buffer = io.BytesIO()
        name_region.save(name_buffer, format="JPEG", quality=rng.randint(40, 65))
        name_buffer.seek(0)
        with Image.open(name_buffer) as compressed_name:
            image.paste(compressed_name.convert("RGB"), name_box[:2])
            
    # Artifact 4: Medical specific - Diagnosis region compression mismatch/seams
    if rng.random() < 0.7:
        diag_box = (110, 320, 880, 420)
        diag_region = image.crop(diag_box)
        diag_buffer = io.BytesIO()
        diag_region.save(diag_buffer, format="JPEG", quality=rng.randint(30, 60))
        diag_buffer.seek(0)
        with Image.open(diag_buffer) as compressed_diag:
            image.paste(compressed_diag.convert("RGB"), diag_box[:2])
            # Draw an overlay seam line
            draw = ImageDraw.Draw(image)
            draw.line([(diag_box[0], diag_box[1]), (diag_box[2], diag_box[1])], fill=(220, 220, 220), width=1)

    # Artifact 5: Medical specific - Doctor registration font mismatch / wrong format
    if rng.random() < 0.5:
        draw = ImageDraw.Draw(image)
        # Draw registration with an obviously wrong font & format (e.g. Courier New) on top of the footer
        mismatched_font = load_font(18, rng=rng)
        bad_reg_str = f"REG: FAKE-DOC-999-ILLICIT"
        draw.text((150 + rng.randint(-3, 3), 605), bad_reg_str, fill=(80, 80, 80), font=mismatched_font)

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
                source_type="synthetic_medical_certificate",
                edit_type="none",
                base_image="",
                notes="Generated privacy-safe medical certificate image.",
            )
        )

        # 50% edited, 50% fully forged
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
                    source_type="synthetic_medical_certificate_edit",
                    edit_type=edit_types,
                    base_image=str(real_path.as_posix()),
                    notes="Generated by locally editing a synthetic base medical certificate.",
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
                    source_type="synthetic_medical_certificate_forged",
                    edit_type="fully_forged",
                    base_image="",
                    notes="Generated as a completely forged medical certificate.",
                )
            )

    write_log(records, log_path)
    return {"real": count_per_class, "fake": count_per_class, "log": str(log_path)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a privacy-safe synthetic medical certificate dataset.")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT_PER_CLASS, help="Images per class to generate.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_ROOT), help="Dataset root with real/ and fake/ folders.")
    parser.add_argument("--log", default=str(DEFAULT_LOG_PATH), help="CSV dataset log path.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing medical_*.jpg files.",
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
    print("Synthetic medical dataset generation complete.")
    print(f"real: {summary['real']} image(s)")
    print(f"fake: {summary['fake']} image(s)")
    print(f"log: {summary['log']}")
    return summary


if __name__ == "__main__":
    main()
