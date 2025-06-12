import json
import logging

from dcpmessage.dcp_message import DcpMessage
from dcpmessage.ldds_client import TlsMode

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s]\t%(asctime)s\t[%(pathname)s]\t[%(lineno)s]\t"%(message)s"',
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

if __name__ == "__main__":

    messages = DcpMessage.get(
        username="anonymous",
        password="anonymous",
        search_criteria={"DRS_SINCE": "now - 1hour"},
        host="lrgs.opendcs.org",
    )

    # DCP Messages
    print("============")
    print("DCP MESSAGES")
    print("============")
    for item in messages:
        print(item)
