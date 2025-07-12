from enum import UNIQUE, Enum, verify

from .utils import ByteUtil


@verify(UNIQUE)
class ServerErrorCode(Enum):
    """
    Enum for server error codes, each with a numeric value and description.

    Each member has:

    - A unique numeric value (int)
    - A human-readable description (str), accessible via `.description`
    """

    DSUCCESS = 0, "Success."
    DNOFLAG = 1, "Could not find start of message flag."
    DDUMMY = 2, "Message found (and loaded) but it's a dummy."
    DLONGLIST = 3, "Network list was too long to upload."
    DARCERROR = 4, "Error reading archive file."
    DNOCONFIG = 5, "Cannot attach to configuration shared memory"
    DNOSRCHSHM = 6, "Cannot attach to search shared memory"
    DNODIRLOCK = 7, "Could not get ID of directory lock semaphore"
    DNODIRFILE = 8, "Could not open message directory file"
    DNOMSGFILE = 9, "Could not open message storage file"
    DDIRSEMERR = 10, "Error on directory lock semaphore"
    DMSGTIMEOUT = 11, "Timeout waiting for new messages"
    DNONETLIST = 12, "Could not open network list file"
    DNOSRCHCRIT = 13, "Could not open search criteria file"
    DBADSINCE = 14, "Bad since time in search criteria file"
    DBADUNTIL = 15, "Bad until time in search criteria file"
    DBADNLIST = 16, "Bad network list in search criteria file"
    DBADADDR = 17, "Bad DCP address in search criteria file"
    DBADEMAIL = 18, "Bad electronic mail value in search criteria file"
    DBADRTRAN = 19, "Bad retransmitted value in search criteria file"
    DNLISTXCD = 20, "Number of network lists exceeded"
    DADDRXCD = 21, "Number of DCP addresses exceeded"
    DNOLRGSLAST = 22, "Could not open last read access file"
    DWRONGMSG = 23, "Message doesn't correspond with directory entry"
    DNOMOREPROC = 24, "Can't attach: No more processes allowed"
    DBADDAPSSTAT = 25, "Bad DAPS status specified in search criteria."
    DBADTIMEOUT = 26, "Bad TIMEOUT value in search crit file."
    DCANTIOCTL = 27, "Cannot ioctl() the open serial port."
    DUNTILDRS = 28, "Specified 'until' time reached"
    DBADCHANNEL = 29, "Bad GOES channel number specified in search crit"
    DCANTOPENSER = 30, "Can't open specified serial port."
    DBADDCPNAME = 31, "Unrecognized DCP name in search criteria"
    DNONAMELIST = 32, "Cannot attach to name list shared memory."
    DIDXFILEIO = 33, "Index file I/O error"
    # DNOSRCHSEM = 34, "Bad search-criteria data"
    DBADSEARCHCRIT = 34, "Bad search-criteria data"
    DUNTIL = 35, "Specified 'until' time reached"
    DJAVAIF = 36, "Error in Java - Native Interface"
    DNOTATTACHED = 37, "Not attached to LRGS native interface"
    DBADKEYWORD = 38, "Bad keyword"
    DPARSEERROR = 39, "Error parsing input file"
    DNONAMELISTSEM = 40, "Cannot attach to name list semaphore."
    DBADINPUTFILE = 41, "Cannot open or read specified input file"
    DARCFILEIO = 42, "Archive file I/O error"
    DNOARCFILE = 43, "Archive file not opened"
    DICPIOCTL = 44, "Error on ICP188 ioctl call"
    DICPIOERR = 45, "Error on ICP188 I/O call"
    DINVALIDUSER = 46, "Invalid DDS User"
    DDDSAUTHFAILED = 47, "DDS Authentication failed"
    DDDSINTERNAL = 48, "DDS Internal Error (connection will close)"
    DDDSFATAL = 49, "DDS Fatal Server Error (retry later)"
    DNOSUCHSOURCE = 50, "No such data source"
    DALREADYATTACHED = 51, "User already attached (mult disallowed)"
    DNOSUCHFILE = 52, "No such file"
    DTOOMANYDCPS = 53, "Too many DCPs for real-time stream"
    DBADPASSWORD = 54, "Password does not meet local requirements."
    DSTRONGREQUIRED = 55, "Server requires strong encryption algorithm"

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, description: str = None):
        self.__description = description

    def __str__(self):
        return self.value

    @property
    def description(self):
        """
        Returns the description of the error code.

        :return: Human-readable description.
        """

        return self.__description


class ServerError:
    def __init__(self, message: str, server_code_no: int = 0, system_code_no: int = 0):
        """

        :param message:
        :param server_code_no:
        :param system_code_no:
        """

        self.message = message
        self.server_code_no = server_code_no
        self.system_code_no = system_code_no
        self.is_end_of_message = self.is_end_of_message()

    def is_end_of_message(self):
        if self.server_code_no in (
            ServerErrorCode.DUNTIL.value,
            ServerErrorCode.DUNTILDRS.value,
        ):
            return True
        return False

    @property
    def description(self):
        return ServerErrorCode(self.server_code_no).description

    @staticmethod
    def parse(message: bytes):
        """
        Parse ServerError from error_string

        :param message: bytes response returned from server
        :return: object of ServerError class
        """
        if not message.startswith(b"?"):
            # Not a server error
            return ServerError("")
        error_string = ByteUtil.extract_string(message)
        split_error_string = error_string[1:].split(",", maxsplit=2)
        sever_code_no, system_code_no, error_string = [
            x.strip() for x in split_error_string
        ]
        return ServerError(error_string, int(sever_code_no), int(system_code_no))

    def raise_exception(self):
        raise ProtocolError(self.__str__())

    def __str__(self):
        if self.system_code_no == 0 and self.server_code_no == 0:
            return "No Server Error"

        server_error_code = ServerErrorCode(self.server_code_no)
        r = f"System Code #{self.system_code_no}; "
        r += f"Server Code #{server_error_code.value} - {self.message} ({server_error_code.description})"
        return r

    def __eq__(self, other):
        return (
            self.server_code_no == other.server_code_no
            and self.system_code_no == other.system_code_no
            and self.message == other.message
        )


class ProtocolError(Exception):
    pass


class LddsMessageError(Exception):
    pass
