import unittest
from datetime import datetime, timedelta, timezone

PTZ = timezone(timedelta(hours=-7))

from dcpmessage.credentials import Credentials, HashAlgo, Sha1, Sha256


class InvalidHashClass(HashAlgo):
    def __init__(self):
        super().__init__("sha384")


class TestAuthenticator(unittest.TestCase):
    def test_to_string_sha1(self):
        username = "test_user"
        password = "test_pass"
        credentials = Credentials(username=username, password=password)
        time = datetime(2022, 4, 14, 22, 20, 0, tzinfo=PTZ)  # Example timestamp
        auth_str = credentials.get_authenticator_hash(time, Sha1())

        expected_auth_str = (
            "C91F758CDED80910C0C4FC11CBEB31395AABB9B4"  # Example expected string
        )
        self.assertEqual(auth_str, expected_auth_str)

    def test_to_string_sha256(self):
        username = "test_user"
        password = "test_pass"
        credentials = Credentials(username=username, password=password)
        time = datetime(2022, 4, 14, 22, 20, 0, tzinfo=PTZ)
        auth_str = credentials.get_authenticator_hash(time, Sha256())

        expected_auth_str = (
            "850D6D0BA8D5C00BFF01D507E9C50B3E639C9C0EC93B1E2A84BE2673581439DF"
        )
        self.assertEqual(auth_str, expected_auth_str)

    def test_invalid_algorithm(self):
        username = "test_user"
        password = "test_pass"
        credentials = Credentials(username=username, password=password)
        time = datetime(2022, 4, 14, 22, 20, 0)

        try:
            credentials.get_authenticator_hash(time, InvalidHashClass())
        except AssertionError as err:
            self.assertEqual(str(err), "sha384 is not a supported hash algorithm")
