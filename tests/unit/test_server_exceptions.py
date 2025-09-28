import unittest

from dcpmessage.exceptions import ServerError


class TestServerExceptions(unittest.TestCase):
    def test_server_error_from_string(self):
        se = ServerError.parse(b"?55,0,Server requires SHA-256.")
        self.assertEqual(se.server_code_no, 55)
        self.assertEqual(se.system_code_no, 0)
        self.assertEqual(se.message, "Server requires SHA-256.")

    def test_server_error_str(self):
        se = ServerError.parse(b"?55,0,Server requires SHA-256.")
        self.assertEqual(se.server_code_no, 55)
        self.assertEqual(se.system_code_no, 0)
        expected = (
            "System Code #0; Server Code #55 - Server requires SHA-256. "
            "(Server requires strong encryption algorithm)"
        )
        self.assertEqual(str(se), expected)

    def test_server_error_eq(self):
        se1 = ServerError.parse(b"?55,0,Server requires SHA-256.")
        se2 = ServerError("Server requires SHA-256.", 55, 0)
        self.assertEqual(se1, se2)
