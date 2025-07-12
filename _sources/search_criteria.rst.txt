Search Criteria
---------------

Search Criteria should be provided to retrieve messages for specified DCPs. Search criteria can be passed either as the
path to the search criteria json file or a dict. An
example is provided below.

.. code-block:: json

    {
      "DRS_SINCE": "now - 1 hour",
      "DRS_UNTIL": "now",
      "SOURCE": [
        "GOES_SELFTIMED",
        "GOES_RANDOM"
      ],
      "DCP_ADDRESS": [
        "address1",
        "address2"
      ]
    }

Supported Fields
################

Only the following search criteria keys are currently supported:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Key
     - Type
     - Description
   * - ``DRS_SINCE``
     - ``string``
     - Start time for data query (e.g., ``"now - 1 hour"``)
   * - ``DRS_UNTIL``
     - ``string``
     - End time for data query (e.g., ``"now"``)
   * - ``SOURCE``
     - ``list[string]``
     - Must be one or both of: ``"GOES_SELFTIMED"``, ``"GOES_RANDOM"``
   * - ``DCP_ADDRESS``
     - ``list[string]``
     - One or more DCP addresses to query

.. warning:: ⚠️ All other keys in the criteria file will be ignored. For detailed information on the search criteria format, see
   the `opendcs docs <https://opendcs-env.readthedocs.io/en/stable/legacy-lrgs-userguide.html#search-criteria-file-format>`_.
