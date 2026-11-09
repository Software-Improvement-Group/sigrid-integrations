# Sigrid architecture data export

Exports data from Sigrid's [Architecture Quality](https://docs.sigrid-says.com/capabilities/architecture-quality.html)
so that it can be processed elsewhere. The following export formats are available:

- [JSON](https://docs.sigrid-says.com/integrations/sigrid-api-documentation.html#architecture-quality-data)
- CSV (top-level component dependencies, as `from`, `to`, `weight`, `type` rows)
- [Graphviz](https://www.graphviz.org) (only if you want to generate diagrams)

## Prerequisites

- You need Python 3.9+.
- You need a [Sigrid API token](https://docs.sigrid-says.com/organization-integration/authentication-tokens.html).
  - This token needs to be available as the environment variable `SIGRID_CI_TOKEN`.
- If you want to use the PDF or PNG export, you will need to have Graphviz installed.

## Exporting the Sigrid architecture graph

Assuming you meet the prerequisites listed above, you can run the script:

    python3 sigrid_aq_export.py --customer mycompany --system mysystem --format dot --out ~/Desktop

This script takes the following arguments:

| Argument         | Description                                                                                        |
|------------------|----------------------------------------------------------------------------------------------------|
| `--customer`     | Your Sigrid customer name.                                                                         |
| `--system`       | Your Sigrid system name.                                                                           |
| `--format`       | Export format, one of `json`, `csv`, `dot`, `png`, `pdf`.                                          |
| `--out`          | Output directory.                                                                                  |
| `--entanglement` | (Optional) Color-codes every dependency in the diagram based on the Component Entanglement metric. |

## Exporting architecture findings

Sigrid CI, the Sigrid IDE integrations, and Sigrid Axis give you concrete feedback on where you can improve your
architecture. If you want to obtain this data ad-hoc, you can use the following script:

    python3 sigrid_aq_findings.py --customer mycompany --system mysystem

## Exporting architecture hotspots (Beta)

An architecture "hotspot" is an area that has high development activity *and* is having structural architecture issues.
We are experimenting with using architecture hotspots to prioritize issues and drive architecture evolution. 
This information is not yet available in Sigrid, but you can use the following script to export the data for your
system:

    python3 sigrid_aq_hotspots.py --customer mycompany --system mysystem --components <all | toplevel> out test.csv

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
