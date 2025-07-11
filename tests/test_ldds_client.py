import unittest

from dcpmessage.ldds_client import LddsClient, TlsMode


class TestBasicClient(unittest.TestCase):
    def test_timeout(self):
        client = LddsClient("10.255.255.1", 80, 0.1, TlsMode.DISABLED, None)
        try:
            client.connect()
        except IOError as err:
            assert isinstance(err, OSError)
            self.assertEqual(str(err), "Connection to 10.255.255.1:80 timed out")

        client.disconnect()
