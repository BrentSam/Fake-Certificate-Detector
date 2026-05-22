# Data Collection And Ethics

The detector handles certificate images, which can contain personal data. Keep
real certificates local unless each record is consented, anonymized, and safe to
use for academic review.

## Recommended First Dataset

- Start with synthetic data by running `python main.py sample-data --count 50`.
- Use the generated `docs/synthetic_dataset_log.csv` as the initial dataset log.
- Replace or extend synthetic samples only when consented real examples are available.

## Real Certificate Handling

- Store real images under `dataset/real/` only on the local machine.
- Remove or blur personal names, certificate IDs, QR codes, phone numbers, email addresses, and addresses unless explicit consent allows use.
- Do not commit real certificate images.
- Keep any non-synthetic dataset log under `dataset/dataset_log.csv`; this path is ignored by `.gitignore`.

## Fake Or Edited Samples

Create fake samples from consented or synthetic certificates by changing one
major element at a time:

- Name or holder details.
- Internship dates or duration.
- Issuer name or department.
- Seal, stamp, or signature placement.
- Certificate ID or verification URL.
- Program title or completion wording.

## Dataset Log Columns

Use these columns for each image:

```csv
filename,class_label,source_type,edit_type,base_image,notes
```

- `filename`: Local image path.
- `class_label`: `real` or `fake`.
- `source_type`: `synthetic_certificate`, `consented_anonymized`, or another concise source label.
- `edit_type`: `none`, `name_change`, `date_change`, `seal_shift`, `signature_change`, or another concise edit label.
- `base_image`: Source image for edited fake examples, if applicable.
- `notes`: Short privacy-safe notes only.

## Balance Check

Before ELA conversion, check that `dataset/real/` and `dataset/fake/` have
similar image counts. A first prototype should have at least 50 images per class.
