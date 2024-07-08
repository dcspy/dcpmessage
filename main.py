import json
import logging
from src.logs import write_log, write_error
from src.ldds_message import LddsMessage
from src.basic_client import BasicClient
from src.utils.byte_util import get_c_string
from src.search.search_criteria import SearchCriteria


def test_basic_client(username: str,
                      password: str,
                      search_criteria: str,
                      host: str,
                      port: int = None,
                      timeout: int = None,
                      debug: bool = True
                      ):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    port = port if port is not None else 16003
    timeout = timeout if timeout is not None else 30
    client = BasicClient(host=host, port=port, timeout=timeout)

    try:
        client.connect()
    except Exception as e:
        write_error("Failed to connect to server. Error: " + str(e))
        return

    try:
        client.authenticate_user(username, password)
    except Exception as e:
        write_error("Failed to authenticate user. Error: " + str(e))
        client.disconnect()
        return

    try:
        # TODO: look for error scenarios
        criteria = SearchCriteria()
        criteria.parse_file(search_criteria)
        client.send_search_criteria(data=criteria.to_string_proto(14).encode('utf-8'))
    except Exception as e:
        write_error("Failed to send search criteria. Error: " + str(e))
        client.disconnect()

        return

    try:
        # TODO: message request iterations
        # requesting Dcp Messages
        msg_id = LddsMessage.IdDcpBlock
        dcp_messages = bytearray()
        while True:
            dcp_message = client.request_dcp_message(msg_id)
            c_string = get_c_string(dcp_message, 10)
            if c_string.startswith("?35"):
                break
            dcp_messages += dcp_message
        print(dcp_messages)
    except Exception as e:
        write_error(f"An error occurred: {e}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)

    test_basic_client(username=credentials["username"],
                      password=credentials["password"],
                      search_criteria="./test_search_criteria.sc",
                      host="cdadata.wcda.noaa.gov",
                      debug=True)
