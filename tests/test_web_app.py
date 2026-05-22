from __future__ import annotations

import io
import unittest
from pathlib import Path

from PIL import Image

from app import web_app


@unittest.skipIf(web_app.Flask is None, "Flask is not installed.")
class WebAppTests(unittest.TestCase):
    def test_upload_route_uses_temporary_image_path(self):
        original_predict = web_app.predict_certificate
        seen_paths: list[Path] = []

        def fake_predict(image_path, model_path="model/certificate_cnn.keras"):
            path = Path(image_path)
            seen_paths.append(path)
            self.assertTrue(path.exists())
            return {"label": "Fake Certificate", "confidence": 0.9, "fake_probability": 0.9}

        web_app.predict_certificate = fake_predict
        try:
            app = web_app.create_app()
            client = app.test_client()
            image = Image.new("RGB", (32, 32), "white")
            payload = io.BytesIO()
            image.save(payload, format="JPEG")
            payload.seek(0)

            response = client.post(
                "/",
                data={"certificate": (payload, "certificate.jpg")},
                content_type="multipart/form-data",
            )
        finally:
            web_app.predict_certificate = original_predict

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Fake Certificate", response.data)
        self.assertEqual(len(seen_paths), 1)


if __name__ == "__main__":
    unittest.main()
