import unittest
from unittest.mock import MagicMock, patch

from dcpmessage.ldds_client import (
    LddsClient,
    TlsMode,
)  # Replace 'your_module' with actual module path


class TestLddsClientTimeout(unittest.TestCase):
    def test_timeout(self):
        client = LddsClient("10.255.255.1", 80, 0.1, TlsMode.DISABLED, None)
        try:
            client.connect()
        except IOError as err:
            assert isinstance(err, OSError)
            self.assertEqual(str(err), "Connection to 10.255.255.1:80 timed out")

        client.disconnect()


class TestLddsClientTlsModes(unittest.TestCase):
    def setUp(self):
        self.host = "localhost"
        self.port = 1234
        self.timeout = 30
        self.ssl_context = MagicMock()

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_tls_disabled(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = LddsClient(
            self.host, self.port, self.timeout, TlsMode.DISABLED, self.ssl_context
        )
        client.connect()

        self.assertIs(client.socket, mock_socket)
        self.ssl_context.wrap_socket.assert_not_called()

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_immediate_tls(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        wrapped_socket = MagicMock()
        self.ssl_context.wrap_socket.return_value = wrapped_socket

        client = LddsClient(
            self.host, self.port, self.timeout, TlsMode.IMMEDIATE_TLS, self.ssl_context
        )
        client.connect()

        self.ssl_context.wrap_socket.assert_called_once_with(
            mock_socket, server_hostname=self.host
        )
        self.assertIs(client.socket, wrapped_socket)

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_optional_starttls_success(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        wrapped_socket = MagicMock()
        self.ssl_context.wrap_socket.return_value = wrapped_socket

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.OPTIONAL_STARTTLS,
            self.ssl_context,
        )

        with patch.object(client, "request_dcp_message") as mock_request:
            mock_response = MagicMock()
            mock_response.message_data = b"proceed"
            mock_request.return_value = mock_response

            client.connect()

        self.ssl_context.wrap_socket.assert_called_once()
        self.assertIs(client.socket, wrapped_socket)

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_optional_starttls_fail(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.OPTIONAL_STARTTLS,
            self.ssl_context,
        )

        with patch.object(client, "request_dcp_message") as mock_request:
            mock_response = MagicMock()
            mock_response.message_data = b"not-supported"
            mock_request.return_value = mock_response

            client.connect()

        self.ssl_context.wrap_socket.assert_not_called()

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_required_starttls_success(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        wrapped_socket = MagicMock()
        self.ssl_context.wrap_socket.return_value = wrapped_socket

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.REQUIRED_STARTTLS,
            self.ssl_context,
        )

        with patch.object(client, "request_dcp_message") as mock_request:
            mock_response = MagicMock()
            mock_response.message_data = b"proceed"
            mock_request.return_value = mock_response

            client.connect()

        self.ssl_context.wrap_socket.assert_called_once()
        self.assertIs(client.socket, wrapped_socket)

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_required_starttls_fail(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.REQUIRED_STARTTLS,
            self.ssl_context,
        )

        with patch.object(client, "request_dcp_message") as mock_request:
            mock_response = MagicMock()
            mock_response.message_data = b"nope"
            mock_request.return_value = mock_response

            with self.assertRaises(IOError) as context:
                client.connect()

            self.assertIn("TLS upgrade required but failed", str(context.exception))
