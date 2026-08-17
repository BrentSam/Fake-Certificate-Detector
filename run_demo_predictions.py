"""Run predictions on demo certificates and print a summary."""
from predict import predict_certificate
import os
import json

results = {}
for cert_type in ["internship", "medical"]:
    results[cert_type] = {"real": [], "fake": []}
    for label in ["real", "fake"]:
        folder = f"demo_certificates/{cert_type}/{label}"
        for f in sorted(os.listdir(folder)):
            if f.endswith(".jpg"):
                path = os.path.join(folder, f)
                r = predict_certificate(path, cert_type=cert_type)
                results[cert_type][label].append({
                    "file": f,
                    "predicted": r["label"],
                    "confidence": round(r["confidence"] * 100, 1),
                    "fake_prob": round(r["fake_probability"] * 100, 1),
                })
                status = "CORRECT" if (label == "real" and r["label"] == "Real Certificate") or (label == "fake" and r["label"] == "Fake Certificate") else "WRONG"
                print(f"  [{cert_type.upper():10s}] {label:4s}/{f}: {r['label']:4s} (confidence: {r['confidence']:.1%}) [{status}]")

print("\n" + "=" * 60)
print("DEMO PREDICTION SUMMARY")
print("=" * 60)
for ct in ["internship", "medical"]:
    real_correct = sum(1 for r in results[ct]["real"] if r["predicted"] == "Real Certificate")
    fake_correct = sum(1 for r in results[ct]["fake"] if r["predicted"] == "Fake Certificate")
    total = len(results[ct]["real"]) + len(results[ct]["fake"])
    correct = real_correct + fake_correct
    print(f"\n{ct.title()} Model: {correct}/{total} correct ({correct/total*100:.0f}%)")
    print(f"  Real certificates detected correctly: {real_correct}/{len(results[ct]['real'])}")
    print(f"  Fake certificates detected correctly: {fake_correct}/{len(results[ct]['fake'])}")

with open("demo_certificates/prediction_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nDetailed results saved to demo_certificates/prediction_results.json")
