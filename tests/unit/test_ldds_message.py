import unittest

from dcpmessage.exceptions import LddsMessageError, ServerError
from dcpmessage.ldds_message import LddsMessage, LddsMessageIds


class TestLddsMessage(unittest.TestCase):
    def test_parse_w_error(self):
        parsed_message = LddsMessage.parse(b"FAF0m00030?55,0,Server requires SHA-256.")
        server_error = ServerError(
            message="Server requires SHA-256.", server_code_no=55, system_code_no=0
        )
        self.assertEqual(parsed_message.server_error, server_error)

    def test_parse_create(self):
        created_message = LddsMessage.create(
            LddsMessageIds.dcp_block,
            b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ",
        )
        parsed_message = LddsMessage.parse(
            b"FAF0n00049A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh "
        )
        self.assertEqual(parsed_message, created_message)

    def test_to_bytes(self):
        message = LddsMessage.create(
            LddsMessageIds.dcp_block,
            b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ",
        )
        self.assertEqual(
            message.to_bytes(),
            b"FAF0n00049A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ",
        )

    def test_message_with_inconsistent_length(self):
        parsed_message = LddsMessage.parse(
            b"FAF0n00049A081B07E24204153353G30-0NN096WUB00012`BST@KZ@K"
        )
        with self.assertRaises(LddsMessageError) as _:
            self.assertEqual(
                str(parsed_message.error), "Inconsistent LDDS message length"
            )
            raise parsed_message.error
