# Product Context

## Users

- Individuals who need a quick first-pass assessment of a certificate.
- Administrators or reviewers who receive certificates and need help spotting obvious issues.
- Developers or maintainers extending the detection workflow.

## User Problems

- Manual certificate review is slow and inconsistent.
- Users may not know which visual or textual signals indicate a suspicious certificate.
- A fake certificate can look polished while still containing inconsistent dates, invalid issuer details, altered text, mismatched seals, or layout anomalies.

## Product Experience Goals

- Make the upload and review flow simple.
- Present findings as evidence, not opaque verdicts.
- Use plain language for risk levels and recommendations.
- Make uncertainty visible when the system cannot verify a claim.
- Preserve user trust by avoiding overconfident claims.

## Expected Output Shape

A detection result should ideally include:

- Overall risk level or status.
- Extracted certificate metadata.
- Evidence list with suspicious, valid-looking, and uncertain signals.
- Recommended next steps, such as verifying with the issuing authority.

## Safety And Privacy Expectations

- Treat uploaded certificates as potentially sensitive personal documents.
- Avoid logging or committing sample certificates that contain real personal information.
- Use anonymized or synthetic fixtures for tests whenever possible.
