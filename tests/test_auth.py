from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from app import auth


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "test_users.db")
        auth.init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_db_creates_table(self):
        conn = auth.get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(table)

    def test_create_user_and_authenticate(self):
        # Create user
        user = auth.create_user(self.db_path, "testuser", "test@example.com", "securepassword")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertNotEqual(user.password_hash, "securepassword")

        # Try duplicate username
        dup_user = auth.create_user(self.db_path, "testuser", "other@example.com", "securepassword")
        self.assertIsNone(dup_user)

        # Try duplicate email
        dup_email = auth.create_user(self.db_path, "otheruser", "test@example.com", "securepassword")
        self.assertIsNone(dup_email)

        # Authentication success with username
        auth_success = auth.authenticate_user(self.db_path, "testuser", "securepassword")
        self.assertIsNotNone(auth_success)
        self.assertEqual(auth_success.id, user.id)

        # Authentication success with email
        auth_email = auth.authenticate_user(self.db_path, "test@example.com", "securepassword")
        self.assertIsNotNone(auth_email)
        self.assertEqual(auth_email.id, user.id)

        # Authentication fail with wrong password
        auth_fail_pw = auth.authenticate_user(self.db_path, "testuser", "wrongpassword")
        self.assertIsNone(auth_fail_pw)

        # Authentication fail with non-existent user
        auth_fail_user = auth.authenticate_user(self.db_path, "nonexistent", "securepassword")
        self.assertIsNone(auth_fail_user)

        # Get user by ID
        fetched_user = auth.get_user_by_id(self.db_path, user.id)
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.username, "testuser")


if __name__ == "__main__":
    unittest.main()
