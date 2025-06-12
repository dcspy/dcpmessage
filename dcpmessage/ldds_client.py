import logging
import socket
from datetime import datetime, timezone
from ssl import Purpose, SSLContext
import ssl
from typing import Union
from enum import Enum

from .credentials import Credentials, Sha1, Sha256
from .ldds_message import LddsMessage, LddsMessageConstants, LddsMessageIds
from .search_criteria import SearchCriteria

logger = logging.getLogger(__name__)

class TlsMode(Enum):
    """
    Level of encryption desired.

    """

    """
    """
    NO_TLS = 1 # No encryption
    START_TLS = 2 # Start encryption after initial connection, raise exception if not able
    START_TLS_WANTED = 3 # Start encryption after initial connection, log warning if not able
    TLS = 4 # Encryption is required and immediately enabled before any other communications


class BasicClient:
    """
    A class for managing basic socket connections to a remote server.

    :param host: The hostname or IP address of the remote server.
    :param port: The port number to connect to on the remote server.
    :param timeout: The timeout duration for the socket connection in seconds.
    :param tls_mode: Whether to directly use TLS, START_TLS, or no encryption
    :param ssl_context: SSL information required to establish TLS encryption
    """

    def __init__(self, host: str, port: int, timeout: Union[float, int], tls_mode: TlsMode, ssl_context: SSLContext):
        """
        Initialize the BasicClient with the provided host, port, and timeout.

        :param host: The hostname or IP address of the remote server.
        :param port: The port number to connect to on the remote server.
        :param timeout: The timeout duration for the socket connection in seconds.
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
            if self.tls_mode == TlsMode.TLS:
                self.raw_socket = self.socket # original socket must be closed as well as the tls socket
                self.socket = self.ssl_context.wrap_socket(self.socket, server_hostname=self.host)
            logger.info(f"Successfully connected to {self.host}:{self.port}")
        except socket.timeout as ex:
            raise IOError(f"Connection to {self.host}:{self.port} timed out") from ex
        except socket.error as ex:
            raise IOError(f"Cannot connect to {self.host}:{self.port}") from ex

    def disconnect(self):
        """
        Close the established socket connection.

        :return: None
        """
        try:
            if self.socket:
                self.socket.close()
                logger.debug("Closed socket")

            if self.raw_socket != None:
                self.raw_socket.close()
                logger.debug("Closed raw socket")
        except IOError as ex:
            logger.debug(f"Error during disconnect: {ex}")
        finally:
            self.socket = None

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
            raise IOError("BasicClient socket closed.")
        self.socket.sendall(data)


class LddsClient(BasicClient):
    """
    A client for communicating with an LDDS (Low Data Rate Demodulation System) server.
    Inherits from BasicClient and adds LDDS-specific functionality.
    """

    def __init__(self, host: str, port: int, timeout: Union[float, int], tls_mode: TlsMode, ssl_context: SSLContext):
        """
        Initialize the LddsClient with the provided host, port, and timeout.

        :param host: The hostname or IP address of the LDDS server.
        :param port: The port number to connect to on the LDDS server.
        :param timeout: The timeout duration for the socket connection in seconds.
        """
        super().__init__(host=host, port=port, timeout=timeout, tls_mode=tls_mode, ssl_context=ssl_context)

    def connect(self):
        """
        Start Tls, is used *MUST* be the first command sent
        """
        super().connect()
        if self.tls_mode in (TlsMode.START_TLS, TlsMode.START_TLS_WANTED):
            logger.info("Attempting TLS upgrade.")
            msg = self.request_dcp_message(LddsMessageIds.start_tls)
            if msg.message_data == b"proceed":
                self.raw_socket = self.socket
                self.socket = self.ssl_context.wrap_socket(self.socket, server_hostname=self.host)
                logger.info("TLS upgrade successful")
            elif msg.message_data != b"proceed" and self.tls_mode == TlsMode.START_TLS:
                raise IOError(f"Server {self.host} does not support Start TLS operation.")
            else:
                logger.warning(f"TLS upgrade failed. {msg.message_data}")

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
            raise IOError("BasicClient socket closed.")

        data = self.socket.recv(buffer_size)
        if len(data) == 0:
            raise IOError("BasicClient socket closed.")

        ldds_message_length = LddsMessage.get_total_length(data)
        while len(data) < ldds_message_length:
            data += self.socket.recv(buffer_size)

        return data

    def authenticate_user(
        self,
        user_name: str = "user",
        password: str = "pass",
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

        is_authenticated = False
        for hash_algo in [Sha1, Sha256]:
            auth_str = credentials.get_authenticated_hello(
                datetime.now(timezone.utc), hash_algo()
            )
            logger.debug(auth_str)
            ldds_message = self.request_dcp_message(msg_id, auth_str)
            server_error = ldds_message.server_error
            if server_error is not None:
                logger.debug(str(server_error))
            else:
                is_authenticated = True

        if is_authenticated:
            logger.info("Successfully authenticated user")
        else:
            raise Exception(
                f"Could not authenticate for user:{user_name}\n{server_error}"
            )

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
        message_bytes = message.to_bytes()
        self.send_data(message_bytes)
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
        logger.debug(f"Sending criteria message (filesize = {len(data_to_send)} bytes)")
        ldds_message = self.request_dcp_message(
            LddsMessageIds.search_criteria, data_to_send
        )

        server_error = ldds_message.server_error
        if server_error is not None:
            server_error.raise_exception()
        else:
            logger.info("Search criteria sent successfully.")

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
