import unittest

from dcpmessage.utils import ByteUtil


class TestUtils(unittest.TestCase):
    def test_extract_string(self):
        b = b"?55,0,Server requires SHA-256."
        s = "Server requires SHA-256."
        self.assertEqual(ByteUtil.extract_string(b, 6), s)

    def test_extract_string_w_null(self):
        b = b"?55,0,Server requires \x00SHA-256."
        s = "Server requires "
        self.assertEqual(ByteUtil.extract_string(b, 6), s)
