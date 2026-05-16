import logging

from .dcp_message import DcpMessage

logging.getLogger(__name__).addHandler(logging.NullHandler())


__all__ = ["DcpMessage"]
