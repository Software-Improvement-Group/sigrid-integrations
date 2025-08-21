# Sigrid/Siemens Polarion integration

Enables synchronization of Sigrid data to [Siemens Polarion](https://polarion.plm.automation.siemens.com). When you
run this integration, the following information will be synchronized to Siemens Polarion:

- Open Source Health (SBOM) components.
- Open Source Health (SBOM) vulnerabilities.
- Security findings in your own code.
- Ratings for maintainability/architecture/OSH/security.

This then allows you to manage Sigrid data in Polarion.

## Prerequisites

- You have [on-boarded your system into Sigrid](https://docs.sigrid-says.com/organization-integration/onboarding-steps.html).
- You have a [Sigrid API token](https://docs.sigrid-says.com/organization-integration/authentication-tokens.html).
- You have *both* a Polarion development project and a Polarion cybersecurity project.
- You can run this integration in two ways:
    - Using the Docker container in this repository, which requires Docker.
    - By directly running the code in your environment, which requires Python 3.9+.

## Usage

You need to add this integration to your environment, so that Sigrid data is periodically synchronized to Polarion.
*When* you should schedule this synchronization depends on your development process. For example, if you use a
[nightly build](https://softwareengineering.stackexchange.com/questions/56490/what-does-nightly-builds-mean), it
would be logical to make the Sigrid/Polarion integration part of that nightly build.

As mentioned in the [prerequisites](#prerequisites) section, you can run the integration using Docker. The container
is available from DockerHub: `softwareimprovementgroup/sigrid-integrations`. If you prefer to not use Docker, you
can clone this repository and run the integration directly.

The integration requires the following environment variables:

- `SIGRID_CI_TOKEN` should be a Sigrid API token that has access to your Sigrid system.
- `POLARION_API_TOKEN` should be a Polarion PAT Token that has access to your Polarion project.

You can then run the integration using the following command line arguments:

| Argument             | Required | Description                                                                     |
|----------------------|----------|---------------------------------------------------------------------------------|
| `--customer`         | Yes      | Your Sigrid customer name, e.g. `mycompany`.                                    |
| `--system`           | Yes      | Your Sigrid system name, e.g. `mysystem`.                                       |
| `--polarionurl`      | Yes      | The base URL for your Polarion instance.                                        |
| `--polarionproject`  | Yes      | The name of the Polarion project that you want to synchronize with Sigrid.      |
| `--systemworkitem`   | Yes      | The ID of the Polarion work item that should act as the "root" for Sigrid data. |

## Contact and support

Feel free to contact SIG’s [support department](mailto:support@softwareimprovementgroup.com) for any questions or 
issues you may have after reading this document, or when using Sigrid or Sigrid CI. Users in Europe can also 
contact us by phone at +31 20 314 0953.

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
