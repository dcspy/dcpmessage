import json
import logging
import os
from dataclasses import dataclass
from enum import UNIQUE, Enum, verify

logger = logging.getLogger(__name__)


@verify(UNIQUE)
class DcpMessageSource(Enum):
    """
    Enumeration for DCP message sources with unique values.


    :param GOES: Represents a standard GOES message source.
    :param GOES_SELFTIMED: Represents a self-timed GOES message source.
    :param GOES_RANDOM: Represents a random GOES message source.
    """

    GOES = 0x00000000
    GOES_SELFTIMED = 0x00010000
    GOES_RANDOM = 0x00020000


@dataclass
class SearchCriteriaConstants:
    """
    Constants used in SearchCriteria.

    :param max_sources: The maximum number of sources that can be added to the search criteria.
    """

    max_sources: int = 12


class DcpAddress:
    """
    Class representing a DCP address.

    :param address: (str) The DCP address, which must be 8 characters long.
    """

    def __init__(self, address: str):
        """
        Initialize the DcpAddress with a given address.

        :param address: The address string, which must be exactly 8 characters long.
        :raises AssertionError: If the address is not 8 characters long.
        """
        if len(address) != 8:
            raise ValueError(
                f"length of DCP address '{address}' is not 8 characters long."
            )
        self.address = address

    def __eq__(self, other):
        """
        Compare two DcpAddress objects for equality.

        :param other: The other DcpAddress object to compare with.
        :return: True if the addresses are the same, False otherwise.
        """
        return self.address == other.address


class SearchCriteria:
    def __init__(
        self,
        lrgs_since: str,
        lrgs_until: str,
        dcp_address: list[DcpAddress],
        sources: list[int],
    ):
        """
        Initialize the SearchCriteria with provided parameters.

        :param lrgs_since: The start time for the search criteria.
        :param lrgs_until: The end time for the search criteria.
        :param dcp_address: A list of DCP addresses to search for.
        :param sources: A list of sources to include in the search.
        """
        self.lrgs_since = lrgs_since
        self.lrgs_until = lrgs_until
        self.dcp_address = dcp_address
        self.sources = [0 for _ in range(SearchCriteriaConstants.max_sources)]
        self.num_sources = 0
        for source in sources:
            self.__add_source(source)

    @classmethod
    def from_file(
        cls,
        file: str,
    ) -> "SearchCriteria":
        """
        Create a SearchCriteria object from a JSON file.

        :param file: Path to the JSON file containing search criteria.
        :return: A SearchCriteria object.
        :raises Exception: If there is an issue parsing the JSON file.
        """
        with open(file, "r") as json_file:
            json_data = json.load(json_file)
        return cls.from_dict(json_data)

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "SearchCriteria":
        """
        Create a SearchCriteria object from a dict.

        :param data: dict containing search criteria data.
        :return: A SearchCriteria object.
        :raises Exception: If there is an issue parsing the JSON file.
        """

        lrgs_since, lrgs_until, dcp_addresses, sources = "last", "now", [], []
        try:
            for key_word_, data in data.items():
                match key_word_:
                    case "DRS_SINCE":
                        lrgs_since = data
                    case "DRS_UNTIL":
                        lrgs_until = data
                    case "DCP_ADDRESS":
                        data = list(set(data))
                        dcp_addresses = [DcpAddress(x) for x in data]
                    case "SOURCE":
                        data = list(set(data))
                        sources = [DcpMessageSource[x].value for x in data]
                    case _:
                        logger.debug(
                            f"Unrecognized key word {key_word_} in Search Criteria. Will be ignored."
                        )
            search_criteria = cls(lrgs_since, lrgs_until, dcp_addresses, sources)
            logger.debug(str(search_criteria))
            return search_criteria
        except Exception as ex:
            raise Exception(f"Unexpected exception parsing search-criteria: {ex}")

    def __add_source(
        self,
        source: int,
    ):
        """
        Add a source to the search criteria if not already present.

        :param source: The source identifier to add.
        """
        if self.num_sources >= SearchCriteriaConstants.max_sources:
            return
        if source not in self.sources:
            self.sources[self.num_sources] = source
            self.num_sources += 1

    def __str__(self) -> str:
        """
        Convert the SearchCriteria to a string format for easy readability.

        :return: A string representation of the search criteria.
        """
        line_separator = os.linesep

        ret = ["#\n# LRGS Search Criteria\n#\n"]

        if self.lrgs_since:
            ret.append(f"DRS_SINCE: {self.lrgs_since}{line_separator}")
        if self.lrgs_until:
            ret.append(f"DRS_UNTIL: {self.lrgs_until}{line_separator}")
        for dcp_address_ in self.dcp_address:
            ret.append(f"DCP_ADDRESS: {dcp_address_.address}{line_separator}")

        for i in range(self.num_sources):
            source_name = DcpMessageSource(self.sources[i]).name
            ret.append(f"SOURCE: {source_name}{line_separator}")

        return "".join(ret)

    def __bytes__(self) -> bytes:
        """
        Convert the SearchCriteria object to a bytes format for network transmission.

        :return: A bytes representation of the search criteria.
        """
        return self.__str__().encode("utf-8")

    def __eq__(self, other) -> bool:
        """
        Compare two SearchCriteria objects for equality.

        :param other: The other SearchCriteria object to compare with.
        :return: True if the criteria are the same, False otherwise.
        """
        if self.lrgs_since != other.lrgs_since or self.lrgs_until != other.lrgs_until:
            return False

        if len(self.dcp_address) != len(other.dcp_address):
            return False

        for explicit_dcp_address in self.dcp_address:
            if explicit_dcp_address not in other.dcp_address:
                return False

        return True
