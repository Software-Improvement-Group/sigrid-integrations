# Sigrid Excel exports

Excel exports beyond the ones available from the Sigrid user interface.

## Prerequisites

You will need the following to use these scripts.

- The script requires Python 3.9+.
- Install the dependencies, e.g. `pip3 install -r requirements.txt --user`. 
- You need a valid [API token](https://docs.sigrid-says.com/organization-integration/authentication-tokens.html).
- Your API token should be available to the script as the environment variable `SIGRID_CI_TOKEN`.

## Objectives

Export an Excel sheet that contains a full overview of every objective for every system.

    ./objectives_excel_export.py --customer <mycustomername> --out my-file.xlsx

## Portfolio Hygiene

Export an Excel sheet that contains an overview of the Sigrid hygiene for the entire portfolio.

    ./sigrid_hygiene_excel_export.py --customer <mycustomername> --out my-file.xlsx

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

