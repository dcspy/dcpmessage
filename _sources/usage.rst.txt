Usage
-----

The script below demonstrates an example of using ``dcpmessage``.

.. _example-script:

Example Script
##############

The :ref:`DcpMessage` can be used to get messages from LRGS server.

.. code-block:: python

    # main.py
    import logging

    from dcpmessage.dcp_message import DcpMessage

    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s]\t%(asctime)s\t[%(pathname)s]\t[%(lineno)s]\t"%(message)s"',
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    if __name__ == "__main__":
        messages = DcpMessage.get(
            username="<USERNAME>",  # <-- your NOAA LRGS username
            password="<PASSWORD>",  # <-- your NOAA LRGS password
            search_criteria={
                "DRS_SINCE": "now - 2 hour",
                "DRS_UNTIL": "now",
                "SOURCE": ["GOES_SELFTIMED", "GOES_RANDOM"],
                "DCP_ADDRESS": ["<DCP ADDRESS>"],  # <-- your DCP addresses
            },
            host="cdadata.wcda.noaa.gov",
        )

        for message in messages:
            print(message)

.. warning:: 🔐 Replace ``<USERNAME>``, ``<PASSWORD>``, and ``<DCP ADDRESS>`` with your actual NOAA LRGS credentials and DCP address.

Quick Test with uv
##################

To quickly install ``dcpmessage`` in a temporary environment with ``uv`` and run the script above, follow these steps:

1. Install ``uv`` - refer to the ``uv`` `website <https://docs.astral.sh/uv/getting-started/installation/>`_.

2. Copy the :ref:`example script <example-script>` to create ``main.py`` script

3. Run the script using ``uv``

.. code-block:: bash

    uv run --with dcpmessage ./main.py
