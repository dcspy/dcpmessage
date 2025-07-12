# dcpmessage

`dcpmessage` is a lightweight Python library for retrieving **GOES DCS messages** from **LRGS servers** using defined
search criteria. It was originally developed for deployment as an AWS Lambda function for periodic message retrieval
from specified Data Collection Platforms (DCPs).

> 🔹 Note: This package only retrieves DCP messages. Decoding, processing, or archiving must be handled externally.

## 🚀 Installation

You can install the package from [PyPI](https://pypi.org/project/dcpmessage/) using `pip` or [
`uv`](https://docs.astral.sh/uv/concepts/projects/dependencies/).

```shell
# using pip
pip install dcpmessage
```

OR

```shell
# using uv
uv add dcpmessage
```

## 🧪 Usage

The script below demonstrates an example of using `dcpmessage`.

### Example Script

```python
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
```

### 🔧 Quick Test with `uv`

To quickly install `dcpmessage` in a temporary environment with `uv` and run the script above, follow these steps:

1. Install `uv` - refer to the `uv` [website](https://docs.astral.sh/uv/getting-started/installation/).

2. Copy the example script above to create `main.py` script

    > 🔐 Replace `<USERNAME>`, `<PASSWORD>`, and `<DCP ADDRESS>` with your actual NOAA LRGS credentials and DCP address.

3. Run the script using `uv`

```bash
uv run --with dcpmessage ./main.py
```

## 📁 Search Criteria

Search Criteria should be provided to retrieve messages for specified DCPs. Search criteria can be passed either as the
path to the search criteria json file or a dict. An
example is provided below.

```json
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
```

### 🔍 Supported Fields

Only the following search criteria keys are currently supported:

| Key           | Type           | Description                                                 |
|---------------|----------------|-------------------------------------------------------------|
| `DRS_SINCE`   | `string`       | Start time for data query (e.g., `"now - 1 hour"`)          |
| `DRS_UNTIL`   | `string`       | End time for data query (e.g., `"now"`)                     |
| `SOURCE`      | `list[string]` | Must be one or both of: `"GOES_SELFTIMED"`, `"GOES_RANDOM"` |
| `DCP_ADDRESS` | `list[string]` | One or more DCP addresses to query                          |

> ⚠️ All other keys in the criteria file will be ignored. For detailed information on the search criteria format, see
> the
[opendcs docs](https://opendcs-env.readthedocs.io/en/stable/legacy-lrgs-userguide.html#search-criteria-file-format).

## 👥 Contributors

- [Manoj Kotteda](https://github.com/orgs/dcspy/people/manojkotteda)
- Darshan Baral
