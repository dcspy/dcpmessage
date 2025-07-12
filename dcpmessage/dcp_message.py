import logging
import ssl
from pathlib import Path
from typing import Union

from .ldds_client import LddsClient, TlsMode
from .ldds_message import LddsMessage
from .search_criteria import SearchCriteria

logger = logging.getLogger(__name__)


class DcpMessage:
    """
    Class for handling DCP messages, including fetching and processing them
    from a remote server using the LDDS protocol.

    :param DATA_LENGTH: Standard length of the data field in a DCP message.
    :param HEADER_LENGTH: Standard length of the header in a DCP message.
    """

    DATA_LENGTH = 32
    HEADER_LENGTH = 37

    @staticmethod
    def get(
        username: str,
        password: str,
        search_criteria: Union[dict, str, Path],
        host: str,
        port: int = 16003,
        timeout: int = 30,
        tls_mode: int = 1,
    ):
        """
        Fetches DCP messages from a server based on provided search criteria.

        This method handles the complete process of connecting to the server,
        authenticating, sending search criteria, retrieving DCP messages, and
        finally disconnecting.

        :param username: Username for server authentication.
        :param password: Password for server authentication.
        :param search_criteria: File path to search criteria or search criteria as a string.
        :param host: Hostname or IP address of the server.
        :param port: Port number for server connection (default: 16003).
        :param timeout: Connection timeout in seconds (default: 30 seconds).
            Will be passed to `socket.settimeout <https://docs.python.org/3/library/socket.html#socket.socket.settimeout>`_
        :param tls_mode: TLS configuration level for the connection (default: 1 - DISABLED).
            Must be one of the following values from the `TlsMode` enum:

            * 1: Do not use TLS.
            * 2: Try to upgrade to TLS via STARTTLS. Continue without TLS if upgrade fails.
            * 3: Try to upgrade via STARTTLS. Fail if TLS cannot be established.
            * 4: Require full TLS before any communication begins.
        :return: List of DCP messages retrieved from the server.
        :raises ValueError: If `tls_mode` is not valid value.
        :raises TypeError: If `search_criteria` is not a valid type (dict, str, or Path).
        :raises Exception: If connection, authentication, or message retrieval fails.
        """

        try:
            tls_mode = TlsMode(tls_mode)
        except ValueError:
            valid_values = ", ".join(f"{e.value} ({e.name})" for e in TlsMode)
            raise ValueError(
                f"Invalid tls_mode: {tls_mode}. Must be one of: {valid_values}"
            )

        match tls_mode:
            case TlsMode.DISABLED:
                ssl_context = None
            case _:
                ssl_context = ssl.create_default_context(
                    purpose=ssl.Purpose.SERVER_AUTH
                )

        client = LddsClient(
            host=host,
            port=port,
            timeout=timeout,
            tls_mode=tls_mode,
            ssl_context=ssl_context,
        )

        try:
            client.connect()
        except Exception as e:
            logger.error("Failed to connect to server.")
            raise e

        try:
            client.authenticate_user(username, password)
        except Exception as e:
            logger.error("Failed to authenticate user.")
            client.disconnect()
            raise e

        match search_criteria:
            case str() | Path():
                criteria = SearchCriteria.from_file(search_criteria)
            case dict():
                criteria = SearchCriteria.from_dict(search_criteria)
            case _:
                raise TypeError("search_criteria must be a filepath or a dict.")

        try:
            client.send_search_criteria(criteria)
        except Exception as e:
            logger.error("Failed to send search criteria.")
            client.disconnect()
            raise e

        # Retrieve the DCP block and process it into individual messages
        dcp_blocks = client.request_dcp_blocks()
        dcp_messages = DcpMessage.explode(dcp_blocks)

        client.send_goodbye()
        client.disconnect()
        return dcp_messages

    @staticmethod
    def explode(
        message_blocks: list[LddsMessage],
    ) -> list[str]:
        """
        Splits a message block bytes containing multiple DCP messages into individual messages.

        :param message_blocks: message block (concatenated response from the server).
        :return: A list of individual DCP messages.
        """

        data_length = DcpMessage.DATA_LENGTH
        header_length = DcpMessage.HEADER_LENGTH
        dcp_messages = []

        for ldds_message in message_blocks:
            message = ldds_message.message_data.decode()
            start_index = 0
            while start_index < ldds_message.message_length:
                # Extract the length of the current message
                message_length = int(
                    message[(start_index + data_length) : (start_index + header_length)]
                )
                # Extract the entire message using the determined length
                end_index = start_index + header_length + message_length
                dcp_message = message[start_index:end_index]
                dcp_messages.append(dcp_message)
                start_index += DcpMessage.HEADER_LENGTH + message_length

        return dcp_messages
