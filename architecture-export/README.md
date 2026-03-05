# Sigrid architecture data export

Exports data from Sigrid's [Architecture Quality](https://docs.sigrid-says.com/capabilities/architecture-quality.html)
so that it can be processed elsewhere. The following export formats are available:

- [JSON](https://docs.sigrid-says.com/integrations/sigrid-api-documentation.html#architecture-quality-data)
- [Graphviz](https://www.graphviz.org)

## Prerequisites

- You need Python 3.9+.
- You need a [Sigrid API token](https://docs.sigrid-says.com/organization-integration/authentication-tokens.html).
  - This token needs to be available as the environment variable `SIGRID_CI_TOKEN`.
- If you want to use the PDF or PNG export, you will need to have Graphviz installed.

## Usage

Assuming you meet the prerequisites listed above, you can run the script:

    ./sigrid_aq_export.py --customer mycompany --system mysystem --format dot --out ~/Desktop

This script takes the following arguments:

| Argument     | Description                                        |
|--------------|----------------------------------------------------|
| `--customer` | Your Sigrid customer name.                         |
| `--system`   | Your Sigrid system name.                           |
| `--format`   | Export format, one of `json`, `dot`, `png`, `pdf`. |
| `--out`      | Output directory.                                  |

## License

Copyright Software Improvement Group

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
