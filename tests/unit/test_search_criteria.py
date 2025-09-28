import json
import os
import unittest

from dcpmessage.search_criteria import DcpAddress, DcpMessageSource, SearchCriteria


class TestSearchCriteria(unittest.TestCase):
    def test_from_file(self):
        criteria_file = "./test_search_criteria_DELETE_AFTER_TEST.json"
        search_criteria_data = {
            "DRS_SINCE": "2022-01-01 00:00:00",
            "DRS_UNTIL": "2022-01-01 00:02:00",
            "SOURCE": ["GOES_SELFTIMED", "GOES_RANDOM"],
            "DCP_ADDRESS": ["A081B07E", "A0806A3E", "A081B07E"],
        }

        with open(criteria_file, "w") as f:
            json.dump(search_criteria_data, f)

        search_criteria = SearchCriteria.from_file(criteria_file)
        self.assertEqual(search_criteria.lrgs_since, "2022-01-01 00:00:00")
        self.assertEqual(search_criteria.lrgs_until, "2022-01-01 00:02:00")
        self.assertEqual(len(search_criteria.sources), 12)
        self.assertEqual(
            set(search_criteria.sources),
            {
                DcpMessageSource.GOES.value,
                DcpMessageSource.GOES_SELFTIMED.value,
                DcpMessageSource.GOES_RANDOM.value,
            },
        )
        for x, y in zip(
            sorted(search_criteria.dcp_address, key=lambda da: da.address),
            ["A0806A3E", "A081B07E"],
            strict=True,
        ):
            self.assertEqual(x, DcpAddress(y))
        os.remove(criteria_file)
