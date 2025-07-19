dcpmessage
==========

dcpmessage is a lightweight Python library for retrieving **GOES DCS messages** from **LRGS servers** using defined
search criteria. It was originally developed for deployment as an AWS Lambda function for periodic message retrieval
from specified Data Collection Platforms (DCPs).

.. note:: 🔹 This package only retrieves DCP messages. Decoding, processing, or archiving must be handled externally.

.. toctree::
    :maxdepth: 4
    :caption: Contents:

    installation
    usage
    search_criteria
    dcp_message