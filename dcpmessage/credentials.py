import hashlib
from datetime import datetime

from dcpmessage.utils import ByteUtil


class HashAlgo:
    """
    A class representing a hashing algorithm.

    This class serves as a base class for different hashing algorithms,
    such as SHA-1 and SHA-256, providing a common interface to initialize
    and create new hash objects.

    Attributes:
        algorithm (str): The name of the hashing algorithm.
    """

    def __init__(self, algorithm):
        """
        Initialize the HashAlgo with a specific hashing algorithm.

        :param algorithm: The name of the hashing algorithm (e.g., "sha1",
        "sha256").
        """
        assert algorithm in {"sha1", "sha256"}, f"{algorithm} is not a supported hash algorithm"
        self.algorithm = algorithm

    def new(self):
        """
        Create a new hash object using the specified algorithm.

        :return: A new hash object from the hashlib library.
        """
        return hashlib.new(self.algorithm)


class Sha1(HashAlgo):
    """
    A class representing the SHA-1 hashing algorithm.

    Inherits from the HashAlgo class and is pre-configured with the "sha1"
    algorithm.
    """

    def __init__(self):
        """
        Initialize the Sha1 class with the "sha1" algorithm.
        """
        super().__init__("sha1")


class Sha256(HashAlgo):
    """
    A class representing the SHA-256 hashing algorithm.

    Inherits from the HashAlgo class and is pre-configured with the "sha256"
    algorithm.
    """

    def __init__(self):
        """
        Initialize the Sha256 class with the "sha256" algorithm.
        """
        super().__init__("sha256")


class Credentials:
    def __init__(self, username: str = None, password: str = None):
        """
        Initialize the Credentials with a username and password.

        :param username: The username of the user.
        :param password: The password of the user.
        """
        self.username = username
        self.preliminary_hash = self.get_preliminary_hash(password)

    def get_preliminary_hash(self, password: str) -> bytes:
        """
        Generate the preliminary hash for the password.

        This method creates a hash by combining the username and password
        multiple times.

        :param password: The password to hash.
        :return: The resulting hash as bytes.
        """
        username_b = self.username.encode("utf-8")
        password_b = password.encode("utf-8")
        md = Sha1().new()
        md.update(username_b)
        md.update(password_b)
        md.update(username_b)
        md.update(password_b)
        return md.digest()

    def get_authenticator_hash(self, time: datetime, hash_algo: HashAlgo) -> str:
        """
        Generate an authenticator hash using a specified hash algorithm.

        This hash is used for authenticating the user based on the current time and the
        user's credentials.

        :param time: The current time as a datetime object.
        :param hash_algo: The hashing algorithm to use (e.g., Sha1, Sha256).
        :return: The authenticator hash as a hexadecimal string.
        """
        time_t = int(time.timestamp())
        time_b = time_t.to_bytes(length=4, byteorder="big")
        username_b = self.username.encode("utf-8")

        md = hash_algo.new()
        md.update(username_b)
        md.update(self.preliminary_hash)
        md.update(time_b)
        md.update(username_b)
        md.update(self.preliminary_hash)
        md.update(time_b)
        authenticator_bytes = md.digest()
        return ByteUtil.to_hex_string(authenticator_bytes)

    def get_authenticated_hello(self, time: datetime, hash_algo: HashAlgo):
        """
        Create an authenticated hello message for the user.

        This method combines the username, current time, authenticator hash, and
        protocol version into a single string used for authentication with the server.

        :param time: The current time as a datetime object.
        :param hash_algo: The hashing algorithm to use for the authenticator hash
        (e.g., Sha1, Sha256).
        :return: The authenticated hello message as a string.
        """
        authenticator_hash = self.get_authenticator_hash(time, hash_algo)
        time_str = time.strftime("%y%j%H%M%S")
        protocol_version = 14

        authenticated_hello = f"{self.username} {time_str} {authenticator_hash} {protocol_version}"
        return authenticated_hello
