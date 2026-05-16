import unittest
from unittest.mock import MagicMock, patch

from dcpmessage.ldds_client import (
    LddsClient,
    TlsMode,
)
from dcpmessage.ldds_message import LddsMessage


class TestLddsClientTimeout(unittest.TestCase):
    def test_timeout(self):
        client = LddsClient("10.255.255.1", 80, 0.1, TlsMode.DISABLED)
        try:
            client.connect()
        except OSError as err:
            assert isinstance(err, OSError)
            self.assertEqual(str(err), "Connection to 10.255.255.1:80 timed out")

        client.disconnect()


class TestLddsClientTlsModes(unittest.TestCase):
    def setUp(self):
        self.host = "localhost"
        self.port = 1234
        self.timeout = 30

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_tls_disabled(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.DISABLED,
        )
        client.connect()

        self.assertIs(client.socket, mock_socket)

    @patch("dcpmessage.ldds_client.ssl.create_default_context")
    @patch("dcpmessage.ldds_client.socket.socket")
    def test_immediate_tls(self, mock_socket_class, mock_ssl_context_func):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        wrapped_socket = MagicMock()
        mock_ssl_context = MagicMock()
        mock_ssl_context.wrap_socket.return_value = wrapped_socket
        mock_ssl_context_func.return_value = mock_ssl_context

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.IMMEDIATE_TLS,
        )
        client.connect()

        mock_socket.connect.assert_called_once_with((self.host, self.port))
        mock_ssl_context.wrap_socket.assert_called_once_with(mock_socket, server_hostname=self.host)
        self.assertIs(client.socket, wrapped_socket)

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_optional_starttls_success(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        wrapped_socket = MagicMock()

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.OPTIONAL_STARTTLS,
        )

        with (
            patch.object(client, "request_dcp_message") as mock_request,
            patch.object(
                client,
                "_wrap_tls",
                side_effect=lambda: setattr(client, "socket", wrapped_socket),
            ),
        ):
            mock_response = MagicMock()
            mock_response.message_data = b"proceed"
            mock_request.return_value = mock_response

            client.connect()

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
        )

        with patch.object(client, "request_dcp_message") as mock_request:
            mock_response = MagicMock()
            mock_response.message_data = b"not-supported"
            mock_request.return_value = mock_response

            client.connect()

        self.assertIs(client.socket, mock_socket)

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_required_starttls_success(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        wrapped_socket = MagicMock()

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.REQUIRED_STARTTLS,
        )

        with (
            patch.object(client, "request_dcp_message") as mock_request,
            patch.object(
                client,
                "_wrap_tls",
                side_effect=lambda: setattr(client, "socket", wrapped_socket),
            ),
        ):
            mock_response = MagicMock()
            mock_response.message_data = b"proceed"
            mock_request.return_value = mock_response

            client.connect()

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
        )

        with patch.object(client, "request_dcp_message") as mock_request:
            mock_response = MagicMock()
            mock_response.message_data = b"nope"
            mock_request.return_value = mock_response

            with self.assertRaises(IOError) as context:
                client.connect()

            self.assertIn("Required TLS upgrade failed", str(context.exception))

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_required_starttls_wrap_tls_failure(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.REQUIRED_STARTTLS,
        )

        with (
            patch.object(client, "request_dcp_message") as mock_request,
            patch.object(client, "_wrap_tls", side_effect=Exception("TLS wrap failed")),
        ):
            mock_response = MagicMock()
            mock_response.message_data = b"proceed"
            mock_request.return_value = mock_response

            with self.assertRaises(IOError) as context:
                client.connect()

            self.assertIn("Required TLS upgrade failed", str(context.exception))

    @patch("dcpmessage.ldds_client.socket.socket")
    def test_optional_starttls_wrap_tls_failure(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = LddsClient(
            self.host,
            self.port,
            self.timeout,
            TlsMode.OPTIONAL_STARTTLS,
        )

        with (
            patch.object(client, "request_dcp_message") as mock_request,
            patch.object(client, "_wrap_tls", side_effect=Exception("TLS wrap failed")),
        ):
            mock_response = MagicMock()
            mock_response.message_data = b"proceed"
            mock_request.return_value = mock_response

            client.disconnect = MagicMock()
            client.connect = MagicMock()

            client._attempt_starttls_upgrade()

            client.disconnect.assert_called_once()
            client.connect.assert_called_once()
            self.assertEqual(client.tls_mode, TlsMode.DISABLED)


class TestLddsClientDataIO(unittest.TestCase):
    def setUp(self):
        self.client = LddsClient("localhost", 1234, 5, TlsMode.DISABLED)

    def test_send_data_socket_none_raises(self):
        self.client.socket = None
        with self.assertRaises(IOError):
            self.client.send_data(b"test")

    def test_send_data_success(self):
        mock_socket = MagicMock()
        self.client.socket = mock_socket
        self.client.send_data(b"hello")
        mock_socket.sendall.assert_called_once_with(b"hello")

    def test_receive_data_socket_none_raises(self):
        self.client.socket = None
        with self.assertRaises(IOError):
            self.client.receive_data()

    def test_receive_data_socket_closed_raises(self):
        mock_socket = MagicMock()
        mock_socket.recv.return_value = b""
        self.client.socket = mock_socket
        with self.assertRaises(IOError):
            self.client.receive_data()

    def test_receive_data_incomplete_raises(self):
        mock_socket = MagicMock()
        # first recv returns partial data
        mock_socket.recv.side_effect = [b"abc", b""]
        self.client.socket = mock_socket

        with patch.object(LddsMessage, "get_total_length", return_value=10):
            with self.assertRaises(IOError):
                self.client.receive_data()

    def test_receive_data_success(self):
        mock_socket = MagicMock()
        # first recv gives full message
        mock_socket.recv.side_effect = [b"abcdefghij"]
        self.client.socket = mock_socket

        with patch.object(LddsMessage, "get_total_length", return_value=10):
            result = self.client.receive_data()

        self.assertEqual(result, b"abcdefghij")
