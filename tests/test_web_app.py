from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from app import web_app


@unittest.skipIf(web_app.Flask is None, "Flask is not installed.")
class WebAppTests(unittest.TestCase):
    def test_routing_and_auth_flow(self):
        with tempfile.TemporaryDirectory() as temp_db_dir:
            db_path = Path(temp_db_dir) / "users_test.db"
            
            # Create app with custom db and mock models
            app = web_app.create_app(
                model_paths={
                    "internship": "mock_internship.keras",
                    "medical": "mock_medical.keras"
                },
                db_path=db_path
            )
            app.config["TESTING"] = True
            
            client = app.test_client()

            # 1. Access root, should redirect to /login
            response = client.get("/")
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.headers["Location"])

            # 2. Access dashboard without auth, should redirect to /login
            response = client.get("/dashboard")
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.headers["Location"])

            # 3. GET /login and /signup
            response = client.get("/login")
            self.assertEqual(response.status_code, 200)
            response = client.get("/signup")
            self.assertEqual(response.status_code, 200)

            # 4. POST /signup to register a user
            response = client.post(
                "/signup",
                data={"username": "testuser", "email": "test@example.com", "password": "securepassword"},
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Account created successfully", response.data)

            # 5. POST /login to authenticate
            response = client.post(
                "/login",
                data={"username_or_email": "testuser", "password": "securepassword"},
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Signed in successfully", response.data)
            self.assertIn(b"Certificate Validation Hub", response.data)  # Dashboard rendered

            # 6. Access protected validation route
            response = client.get("/validate/internship")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Verify Internship Certificate", response.data)

            # 7. Access invalid validation type
            response = client.get("/validate/invalid_type", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Invalid certificate type selected", response.data)

            # 8. POST upload /validate/internship with mocked prediction
            original_predict = web_app.predict_certificate
            seen_types = []

            def fake_predict(image_path, model_path, cert_type):
                seen_types.append(cert_type)
                return {"label": "Real Certificate", "confidence": 0.85, "fake_probability": 0.15, "cert_type": cert_type, "valid": True}

            web_app.predict_certificate = fake_predict
            try:
                image = Image.new("RGB", (32, 32), "white")
                payload = io.BytesIO()
                image.save(payload, format="JPEG")
                payload.seek(0)

                response = client.post(
                    "/validate/internship",
                    data={"certificate": (payload, "certificate.jpg")},
                    content_type="multipart/form-data",
                    follow_redirects=True
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Real Certificate", response.data)
                self.assertIn(b"85.00%", response.data)
                self.assertEqual(seen_types, ["internship"])
            finally:
                web_app.predict_certificate = original_predict

            # 8b. POST upload with invalid certificate prediction (confidence below threshold)
            seen_types_invalid = []

            def fake_predict_invalid(image_path, model_path, cert_type):
                seen_types_invalid.append(cert_type)
                return {
                    "label": "Invalid Format",
                    "confidence": 0.55,
                    "fake_probability": 0.45,
                    "cert_type": cert_type,
                    "valid": False,
                }

            web_app.predict_certificate = fake_predict_invalid
            try:
                image = Image.new("RGB", (32, 32), "white")
                payload = io.BytesIO()
                image.save(payload, format="JPEG")
                payload.seek(0)

                response = client.post(
                    "/validate/internship",
                    data={"certificate": (payload, "certificate.jpg")},
                    content_type="multipart/form-data",
                    follow_redirects=True
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Invalid Format: The uploaded image does not appear to be a certificate", response.data)
                self.assertNotIn(b"Real Certificate", response.data)
                self.assertNotIn(b"Fake Certificate", response.data)
                self.assertNotIn(b"55.00%", response.data)
                self.assertEqual(seen_types_invalid, ["internship"])
            finally:
                web_app.predict_certificate = original_predict

            # 9. GET /logout
            response = client.get("/logout", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Signed out successfully", response.data)


if __name__ == "__main__":
    unittest.main()
