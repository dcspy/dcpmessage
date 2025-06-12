from dataclasses import dataclass

from .exceptions import LddsMessageError, ProtocolError, ServerError, ServerErrorCode


@dataclass
class LddsMessageConstants:
    """Constants related to LDDS messages."""

    VALID_HEADER_LENGTH: int = 10
    SYNC_LENGTH: int = 4
    VALID_SYNC_CODE: bytes = b"FAF0"
    MAX_DATA_LENGTH: int = 99000
    VALID_IDS: frozenset[str] = frozenset(
        (
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
        )
    )


@dataclass
class LddsMessageIds:
    """
    Ids associated with LDDS messages.
    """

    hello: str = "a"
    goodbye: str = "b"
    status: str = "c"
    start: str = "d"
    stop: str = "e"
    dcp: str = "f"
    search_criteria: str = "g"
    get_outages: str = "h"
    idle: str = "i"
    put_netlist: str = "j"
    get_netlist: str = "k"
    assert_outages: str = "l"
    auth_hello: str = "m"
    dcp_block: str = "n"
    events: str = "o"
    ret_config: str = "p"
    inst_config: str = "q"
    dcp_block_ext: str = "r"
    unused_6: str = "s"
    start_tls: str = "t"
    user: str = "u"


class LddsMessage:
    def __init__(
        self,
        message_id: str = None,
        message_length: int = None,
        message_data: bytes = None,
        header: bytes = None,
    ):
        """
        Initialize a LddsMessage instance.

        :param message_id: The ID of the message.
        :param message_length: The length of the message data.
        :param message_data: The message data in bytes.
        :param header: The header of the message in bytes.
        """
        self.message_id = message_id
        self.message_length = message_length
        self.message_data = message_data
        self.header = header
        self.server_error: ServerError = None
        self.error: LddsMessageError = None

    def check_server_errors(self):
        if self.message_data.startswith(b"?"):
            self.server_error = ServerError.parse(self.message_data)

    def check_other_errors(self):
        if self.message_length != len(self.message_data):
            self.error = LddsMessageError("Inconsistent LDDS message length")
        # TODO: add other errors

    @staticmethod
    def parse(
        message: bytes,
    ):
        """
        Parse bytes into an LddsMessage instance.

        :param message: The message in bytes to parse.
        :return: A tuple containing an LddsMessage instance and a ServerError if any.
        :raises ProtocolError: If there is an issue with the message header.
        """
        header_length = LddsMessageConstants.VALID_HEADER_LENGTH
        assert len(message) >= header_length, (
            f"Invalid LDDS message - length={len(message)}"
        )
        header = message[:header_length]

        sync_length = LddsMessageConstants.SYNC_LENGTH
        sync = header[:sync_length]
        assert sync == LddsMessageConstants.VALID_SYNC_CODE, (
            f"Invalid LDDS message header - bad sync '{sync}'"
        )

        message_id = header.decode()[4]
        assert message_id in LddsMessageConstants.VALID_IDS, (
            f"Invalid LDDS message header - ID = '{message_id}'"
        )

        message_length = LddsMessage.get_message_length(header)
        message_data = message[header_length:]

        ldds_message = LddsMessage(
            message_id=message_id,
            message_length=message_length,
            message_data=message_data,
            header=header,
        )
        ldds_message.check_other_errors()
        ldds_message.check_server_errors()

        return ldds_message

    @staticmethod
    def get_message_length(
        message: bytes,
    ) -> int:
        message_length_str = message[5:10].decode().replace(" ", "0")
        try:
            message_length = int(message_length_str)
        except ValueError:
            raise ProtocolError(
                f"Invalid LDDS message header - bad length field = '{message_length_str}'"
            )
        return message_length

    @staticmethod
    def get_total_length(
        message: bytes,
    ) -> int:
        return (
            LddsMessage.get_message_length(message)
            + LddsMessageConstants.VALID_HEADER_LENGTH
        )

    @staticmethod
    def create(message_id: str, message_data: bytes = b""):
        """
        Create a LDDS message from scratch.

        :param message_id: The ID of the message.
        :param message_data: The data of the message in bytes.
        :return: A new LddsMessage instance.
        """
        message_length = len(message_data)
        ldds_message = LddsMessage(
            message_id=message_id,
            message_length=message_length,
            message_data=message_data,
        )
        ldds_message.__make_header()
        return ldds_message

    def __make_header(self):
        """
        Generate the header for the LDDS message.
        """
        header = bytearray(LddsMessageConstants.VALID_HEADER_LENGTH)
        header[:4] = LddsMessageConstants.VALID_SYNC_CODE
        header[4] = ord(self.message_id)

        message_length_str = f"{self.message_length:05d}"
        header[5:10] = (
            message_length_str.encode()
        )  # Set the message length in the header
        self.header = header

    def to_bytes(self):
        """
        Convert the LDDS message to bytes.

        :return: The message in bytes.
        """
        return self.header + self.message_data

    def __eq__(self, other):
        """
        Check equality with another LddsMessage instance.

        :param other: Another LddsMessage instance to compare with.
        :return: True if equal, False otherwise.
        """
        return (
            self.message_length == other.message_length
            and self.message_id == other.message_id
            and self.message_data == other.message_data
        )

    def is_end_of_message(self):
        server_error = ServerError.parse(self.message_data)
        if server_error.server_code_no in (
            ServerErrorCode.DUNTIL.value,
            ServerErrorCode.DUNTILDRS.value,
        ):
            return True
        return False

    def is_success(self):
        server_error = ServerError.parse(self.message_data)
        if server_error.server_code_no == 0 and server_error.system_code_no == 0:
            return True
        return False
