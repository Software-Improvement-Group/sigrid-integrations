# Scripts for exporting portfolio dependencies from Sigrid's Open Source Health

Contains scripts to export data from Sigrid's Open Source Health across your entire portfolio into various formats.
These scripts use the Sigrid REST API, but add some command line options and behavior that make it easier to export
and filter the data into formats suitable for different use cases.

## Prerequisites

You will need the following to use this script:

- These scripts require Python 3.11 or newer.
- Install the dependencies (e.g. `pip3 install -r requirements.txt --user`).
- You will need a valid [API token](https://docs.sigrid-says.com/organization-integration/authentication-tokens.html)
  to access the [Sigrid REST API](https://docs.sigrid-says.com/integrations/sigrid-api-documentation.html).
- Your API token should be available to the script as the environment variable `SIGRID_CI_TOKEN`.

## Export portfolio dependencies to Excel

The export portfolio dependencies to Excel is a tiny Python script to export all third party open source (OSH)
dependencies measured from a Sigrid portfolio in a single self-contained document. Each sheet in the output Excel
file will contain a systems' dependencies.

    ./export_portfolio_dependencies.py [-h] --customer CUSTOMER [--output OUTPUT] [--pivot] [--mendix_versions_only] [--debug]  

The script creates a sheet per system and saves it into a single Excel file. Using `--pivot`, it creates
a single sheet where all dependencies are pivoted, with an additional column containing a comma-separated list of systems where 
that single dependency is measured. 

If all goes well, the export should be in the folder where you run the command. Optionally, in the specified 
filename when passing the `--output` parameter.  

The `--mendix_versions_only` field is an optional field for users using Mendix QSM. Using this field retrieves all 
the different Mendix-Runtime versions used for each system and writes it to the output file. 

If there is an error, and you can't figure out what causes it, run the tool again with the `--debug` parameter
appended to gather additional information. Then, open an issue on this repository.

## Export portfolio dependencies to SBOM

The Sigrid REST API allows you to export all dependencies across your portfolio into one giant SBOM. However, in
some cases you might want to export *multiple* systems into one large SBOM, but not *all* systems. This script helps
you to filter the output based on your selection criteria.

    ./export_portfolio_sbom.py --customer yourcompany [--team Aap] [--division Something] --out my-sbom.json

If you add the `--team` and/or `--division` arguments, the list of systems will be filtered accordingly. You can use
a comma-separated list if you want to filter on multiple divisions or teams. If you add *neither* option, you will 
just get the entire portfolio. The resulting SBOM in CycloneDX format is saved to the file in `--out`.

## Suggestions and feedback

Feedback is welcome! If you have ideas to improve this export, please reach out to Software Improvement Group, or 
open a pull request to this repository.

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
