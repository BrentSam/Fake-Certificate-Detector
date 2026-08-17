# Product Context

## Users

- Individuals who need a quick first-pass assessment of a certificate.
- Administrators or reviewers who receive certificates and need help spotting obvious issues.
- HR teams verifying internship certificates from applicants.
- Healthcare administrators verifying medical certificates.
- Developers or maintainers extending the detection workflow.

## User Problems

- Manual certificate review is slow and inconsistent.
- Users may not know which visual or textual signals indicate a suspicious certificate.
- A fake certificate can look polished while still containing inconsistent dates, invalid issuer details, altered text, mismatched seals, or layout anomalies.
- Different certificate types (internship vs. medical) have different visual patterns and forgery techniques — a single generic model may miss domain-specific cues.

## Product Experience Goals

- Make the upload and review flow simple, with clear certificate type selection upfront.
- Present findings as evidence, not opaque verdicts — show confidence and fake probability.
- Use plain language for risk levels and recommendations.
- Make uncertainty visible when the system cannot verify a claim.
- Preserve user trust by avoiding overconfident claims.
- Provide a premium, modern UI that feels professional and trustworthy.
- Require authentication to protect the tool from anonymous misuse.

## Expected User Flow (Planned)

1. **Sign Up** — create account with username, email, password.
2. **Log In** — authenticate with credentials.
3. **Dashboard** — see two options: "Validate Internship Certificate" or "Validate Medical Certificate".
4. **Select Type** — click one of the two cards.
5. **Upload** — drag-and-drop or browse to upload a certificate image.
6. **View Result** — see verdict (Real/Fake), confidence percentage, and fake probability with visual indicators.
7. **Return** — go back to dashboard to validate another certificate.

## Expected Output Shape

A detection result should include:

- Overall verdict: Real Certificate or Fake Certificate.
- Confidence percentage with visual progress bar.
- Fake probability percentage with visual indicator.
- Certificate type badge (Internship or Medical).
- Color-coded result (green for real, red for fake).

## Safety And Privacy Expectations

- Treat uploaded certificates as potentially sensitive personal documents.
- Avoid logging or committing sample certificates that contain real personal information.
- Use anonymized or synthetic fixtures for tests whenever possible.
- Require authentication before allowing certificate uploads.
- Do not store uploaded certificates beyond the validation session.
