import unittest

from dcpmessage.dcp_message import DcpMessage
from dcpmessage.ldds_message import LddsMessage, LddsMessageIds


class TestDcpMessage(unittest.TestCase):
    def test_explode_simple_block(self):
        message_block = [
            LddsMessage.create(
                LddsMessageIds.dcp_block,
                b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh "
                b"A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh "
                b"A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg "
                b"A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg ",
            )
        ]
        dcp_messages = DcpMessage._explode(message_block)
        self.assertEqual(
            dcp_messages,
            [
                "A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ",
                "A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh ",
                "A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg ",
                "A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg ",
            ],
        )
