from binascii import hexlify


class ByteUtil:
    @staticmethod
    def extract_string(b: bytes | bytearray, offset: int = 0) -> str:
        """
        Pull a null-terminated string out of a byte array starting at given offset.

        :param b: The byte array to extract string from.
        :param offset: The offset to start reading from. Default is 0.
        :return: The extracted string.
        """
        end = b.find(b"\x00", offset)
        if end == -1:
            return b[offset:].decode()
        else:
            return b[offset:end].decode()

    @staticmethod
    def to_hex_string(b: bytes | bytearray):
        """
        Convert byte array to hex string.

        :param b: The byte array to convert to hex string.
        :return: Hex string of byte array.
        """
        return hexlify(b).decode("utf-8").upper()  # Use uppercase hexadecimal
