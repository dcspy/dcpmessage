import logging
import socket
from datetime import datetime, timezone
from enum import Enum
from ssl import SSLContext
from typing import Optional, Union

from .credentials import Credentials, Sha1, Sha256
from .ldds_message import LddsMessage, LddsMessageConstants, LddsMessageIds
from .search_criteria import SearchCriteria

logger = logging.getLogger(__name__)


class TlsMode(Enum):
    """
    Enum representing levels of Transport Layer Security (TLS) to apply during the connection to the server.
    """

    # No TLS encryption will be used at all.
    DISABLED = 1

    # Attempt to upgrade to TLS after establishing the connection;
    # continue without TLS if the upgrade fails, but log a warning.
    OPTIONAL_STARTTLS = 2

    # Attempt to upgrade to TLS after establishing the connection;
    # raise an error if the upgrade fails.
    REQUIRED_STARTTLS = 3

    # Full TLS required from the beginning of the connection;
    # no communication occurs before encryption is established.
    IMMEDIATE_TLS = 4


class LddsClient:
    """
    A client for communicating with an LDDS (Low Data Rate Demodulation System) server.
    """

    def __init__(
        self,
        host: str,
        port: int,
        timeout: Union[float, int],
        tls_mode: TlsMode,
        ssl_context: Optional[SSLContext],
    ):
        """
        Initialize the LddsClient with the provided host, port, and timeout.

        :param host: The hostname or IP address of the remote server.
        :param port: The port number to connect to on the remote server.
        :param timeout: The timeout duration for the socket connection in seconds.
        :param tls_mode: Whether to directly use TLS, START_TLS, or no encryption
        :param ssl_context: SSL information required to establish TLS encryption
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.raw_socket = None
        self.tls_mode = tls_mode
        self.ssl_context = ssl_context

    def connect(self):
        """
        Establish a socket connection to the server using the provided host and port.
        Sets the socket to blocking mode and applies the specified timeout.

        :raises IOError: If the connection attempt times out or fails for any reason.
        :return: None
        """
        try:
            logger.info(f"Connecting to {self.host}:{self.port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
        except socket.timeout as ex:
            raise IOError(f"Connection to {self.host}:{self.port} timed out") from ex
        except socket.error as ex:
            raise IOError(f"Cannot connect to {self.host}:{self.port}") from ex

        match self.tls_mode:
            case TlsMode.DISABLED:
                pass
            case TlsMode.IMMEDIATE_TLS:
                self._wrap_tls()
            case TlsMode.OPTIONAL_STARTTLS | TlsMode.REQUIRED_STARTTLS:
                self._attempt_starttls_upgrade()
        logger.info(f"Successfully connected to {self.host}:{self.port}")

    def _wrap_tls(self):
        self.raw_socket = self.socket
        self.socket = self.ssl_context.wrap_socket(
            self.socket, server_hostname=self.host
        )

    def _attempt_starttls_upgrade(self):
        logger.info("Attempting STARTTLS upgrade.")
        msg = self.request_dcp_message(LddsMessageIds.start_tls)

        if msg.message_data == b"proceed":
            self._wrap_tls()
            logger.info("TLS upgrade successful.")
            return

        if self.tls_mode == TlsMode.REQUIRED_STARTTLS:
            raise IOError(f"TLS upgrade required but failed: {msg.message_data!r}")

        logger.warning(f"TLS upgrade not supported by server: {msg.message_data!r}")

    def disconnect(self):
        """
        Close the established socket connection.

        :return: None
        """
        any_socket_closed = False

        for attr in ["socket", "raw_socket"]:
            sock = getattr(self, attr, None)
            if sock:
                try:
                    sock.close()
                    any_socket_closed = True
                    logger.debug(f"Closed {attr}")

                except IOError as ex:
                    logger.error(f"Error closing {attr}: {ex}")

        self.socket = None
        self.raw_socket = None
        if any_socket_closed:
            logger.info(f"Disconnected from {self.host}:{self.port}")

    def send_data(
        self,
        data: bytes,
    ):
        """
        Send data over the established socket connection.

        :param data: The byte data to send over the socket.
        :raises IOError: If the socket is not connected.
        :return: None
        """
        if self.socket is None:
            raise IOError("Client socket closed.")
        self.socket.sendall(data)

    def receive_data(
        self,
        buffer_size: int = 1024,
    ) -> bytes:
        """
        Receive data from the socket.

        :param buffer_size: The size of the buffer to use when receiving data.
        :return: The received byte data.
        :raises IOError: If the socket is not connected.
        """
        if self.socket is None:
            raise IOError("Client socket closed.")

        data = self.socket.recv(buffer_size)
        if len(data) == 0:
            raise IOError("Client socket closed.")

        ldds_message_length = LddsMessage.get_total_length(data)
        while len(data) < ldds_message_length:
            chunk = self.socket.recv(buffer_size)
            if not chunk:
                raise IOError("Incomplete data received from server.")
            data += chunk

        return data

    def authenticate_user(
        self,
        user_name: str,
        password: str,
    ):
        """
        Authenticate a user with the LDDS server using the provided username and password.

        :param user_name: The username to authenticate with.
        :param password: The password to authenticate with.
        :raises Exception: If authentication fails.
        :return: None
        """
        msg_id = LddsMessageIds.auth_hello
        credentials = Credentials(username=user_name, password=password)

        for hash_algo in [Sha1, Sha256]:
            auth_str = credentials.get_authenticated_hello(
                datetime.now(timezone.utc), hash_algo()
            )
            logger.debug(auth_str)
            ldds_message = self.request_dcp_message(msg_id, auth_str)
            server_error = ldds_message.server_error
            if server_error is None:
                logger.info("Successfully authenticated user")
                return

            logger.debug(str(server_error))

        raise Exception(f"Could not authenticate for user:{user_name}\n{server_error}")

    def request_dcp_message(
        self,
        message_id,
        message_data: Union[str, bytes, bytearray] = "",
    ) -> LddsMessage:
        """
        Request a DCP (Data Collection Platform) message from the LDDS server.

        :param message_id: The ID of the message to request.
        :param message_data: The data to include in the message request.
        :return: The response from the server as bytes.
        """
        if isinstance(message_data, str):
            message_data = message_data.encode()

        message = LddsMessage.create(message_id=message_id, message_data=message_data)
        self.send_data(message.to_bytes())
        server_response = self.receive_data()
        return LddsMessage.parse(server_response)

    def send_search_criteria(
        self,
        search_criteria: SearchCriteria,
    ):
        """
        Send search criteria to the LDDS server.

        :param search_criteria: The search criteria to send.
        :return: None
        """
        data_to_send = bytearray(50) + bytes(search_criteria)
        logger.debug(f"Sending criteria message (size = {len(data_to_send)} bytes)")
        ldds_message = self.request_dcp_message(
            LddsMessageIds.search_criteria, data_to_send
        )

        server_error = ldds_message.server_error
        if server_error is None:
            logger.info("Search criteria sent successfully.")
            return

        server_error.raise_exception()

    def request_dcp_blocks(
        self,
    ) -> list[LddsMessage]:
        """
        Request a block of DCP messages from the LDDS server.

        :return: The received DCP block as bytearray.
        """
        msg_id = LddsMessageIds.dcp_block
        max_data_length = LddsMessageConstants.MAX_DATA_LENGTH
        dcp_messages = []
        try:
            while True:
                response = self.request_dcp_message(msg_id)
                server_error = response.server_error
                if server_error is not None:
                    if server_error.is_end_of_message:
                        logger.info(server_error.description)
                        break
                    else:
                        server_error.raise_exception()
                dcp_messages.append(response)

            return dcp_messages
        except Exception as err:
            logger.debug(f"Error receiving data: {err}")
            raise err

    def send_goodbye(self):
        """
        Send a goodbye message to the LDDS server to terminate the session.

        :return: None
        """
        message_id = LddsMessageIds.goodbye
        ldds_message = self.request_dcp_message(message_id, "")
        server_error = ldds_message.server_error
        logger.debug(ldds_message.to_bytes())
