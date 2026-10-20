
import unittest

from src.passwords import hash_password, verify_password
from src.users import USERS, create_user, authenticate_user
from src.tokens import (
    SESSIONS,
    create_token,
    validate_token,
    revoke_token,
    hash_token,
)


class AuthenticationTests(unittest.TestCase):

    def setUp(self):
        USERS.clear()
        SESSIONS.clear()

    def tearDown(self):
        USERS.clear()
        SESSIONS.clear()

    def test_password_hashing(self):
        record = hash_password("my-secure-password")

        self.assertTrue(
            verify_password("my-secure-password", record)
        )

        self.assertFalse(
            verify_password("wrong-password", record)
        )

    def test_unique_password_salts(self):
        first = hash_password("same-password")
        second = hash_password("same-password")

        self.assertNotEqual(
            first["salt"],
            second["salt"]
        )

        self.assertNotEqual(
            first["hash"],
            second["hash"]
        )

    def test_registration(self):
        create_user("bob", "secure-password-123")

        self.assertIn("bob", USERS)
        self.assertEqual(USERS["bob"]["role"], "user")

        self.assertNotIn("password", USERS["bob"])

        self.assertIn(
            "password_record",
            USERS["bob"]
        )

    def test_duplicate_registration(self):
        create_user("bob", "secure-password-123")

        with self.assertRaises(ValueError):
            create_user("bob", "another-password")

    def test_correct_credentials(self):
        create_user("bob", "secure-password-123")

        user = authenticate_user(
            "bob",
            "secure-password-123"
        )

        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "bob")

    def test_wrong_credentials(self):
        create_user("bob", "secure-password-123")

        self.assertIsNone(
            authenticate_user("bob", "wrong-password")
        )

    def test_unknown_user(self):
        self.assertIsNone(
            authenticate_user("unknown", "password")
        )

    def test_token_creation(self):
        token = create_token("bob")

        self.assertEqual(
            validate_token(token),
            "bob"
        )

    def test_token_uniqueness(self):
        first = create_token("bob")
        second = create_token("bob")

        self.assertNotEqual(first, second)

    def test_only_token_digest_is_stored(self):
        token = create_token("bob")

        self.assertIn(hash_token(token), SESSIONS)
        self.assertNotIn(token, SESSIONS)

    def test_invalid_token(self):
        self.assertIsNone(
            validate_token("invalid-token")
        )

    def test_token_revocation(self):
        token = create_token("bob")

        self.assertTrue(revoke_token(token))

        self.assertIsNone(
            validate_token(token)
        )


if __name__ == "__main__":
    unittest.main()
