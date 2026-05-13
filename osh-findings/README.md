# Sigrid OSH findings task

This script fetches the latest Open Source Health status of your system. It uses the detected dependencies of the last published snapshot, SIG's Open Source Health data and the objectives set for the system.

The intended use of this script is in a scheduled pipeline. It has two purposes:
- Inform the user of available information, by printing it
- For use as a quality gate in the pipeline, by emitting exit codes

The script checks for risks in the categories vulnerabilities, legal (licenses) and freshness (available updates).

The script checks the status of your libraries against cached data. The data is scheduled to refresh at least daily, very new information might not yet be included. 

## Prerequisites

You will need the following to use this script:

- The script has been written for Python 3.13. 
- Install the dependencies (e.g. `pip3 install -r requirements.txt --user`). The listed dependency is needed for creating tables in the output of the script.
- You will need a valid [API token](https://docs.sigrid-says.com/organization-integration/authentication-tokens.html) to access the [Sigrid REST API](https://docs.sigrid-says.com/integrations/sigrid-api-documentation.html).
- Your API token should be available to the script as the environment variable `SIGRID_CI_TOKEN`.

## Usage

Once all prerequisites are in place, you can use the script.

    ./osh-findings.py --customer <mycustomername> --system <mysystemname> [--defaultObjective [HIGH|MEDIUM|LOW|NONE]]

The objectives set (at system or portfolio level) take precedence over the defaultObjective argument. The default value is HIGH.

## Exit codes

The script uses bit-encoded exit codes. If there are findings exceeding your objectives, it will exit non-0 based on the type of risk.

- Vulnerability risk: 1
- Legal risk: 2
- Freshness risk: 4

This way you can make a pipeline job non-blocking on certain exit codes. For example, you can accept 2, 4 and 6 if you want legal and freshness risks to be a warning and non-blocking. Vulnerability risks will be blocking.

## Text output

The examples below are for a system with the following objectives:
- Vulnerability risks at most LOW
- Legal risks at most MEDIUM
- Freshness risks at most LOW

### Vulnerabilities
The table lists all known vulnerabilities in the libraries you use. If you have enabled transitive dependency checking in the system scope file it will include risks in transitive dependencies. 

```
┌Detected vulnerabilities──────┬────────────┬────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ risk       │ library         │ type       │ locations              │ description                                                                                                  │
├────────────┼─────────────────┼────────────┼────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ **MEDIUM** │ vertx-core      │ DIRECT     │ AuthService/maven.tree │ ID: GHSA-cphf-4846-3xx9                                                                                      │
│            │                 │            │                        │ Published: 2026-01-15                                                                                        │
│            │                 │            │                        │ Severity: 6.9 (medium)                                                                                       │
│            │                 │            │                        │ URL: https://nvd.nist.gov/vuln/detail/CVE-2026-1002                                                          │
│            │                 │            │                        │ Description: Vert.x Web static handler component cache can be manipulated to deny the access to static files │
├────────────┼─────────────────┼────────────┼────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ MEDIUM     │ nimbus-jose-jwt │ TRANSITIVE │ AuthService/maven.tree │ ID: GHSA-xwmg-2g98-w7v9                                                                                      │
│            │                 │            │                        │ Published: 2025-07-11                                                                                        │
│            │                 │            │                        │ Severity: 5.8 (medium)                                                                                       │
│            │                 │            │                        │ URL: https://nvd.nist.gov/vuln/detail/CVE-2025-53864                                                         │
│            │                 │            │                        │ Description: Nimbus JOSE + JWT is vulnerable to DoS attacks when processing deeply nested JSON               │
└────────────┴─────────────────┴────────────┴────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

If the risk exceeds your objective for vulnerability risks and is a direct dependency, the risk will be marked in red. 

Only direct dependencies are taken into account for the exit code.


### Legal

The table lists all legal risks higher than your objective. Only direct dependencies are listed.

Additionally, the table lists libraries for which we could not detect the license type. These are not taken into account when determining the exit code of the script. 

```
┌Legal risks───────────────────┬───────────────────┬────────────────────────────┐
│ risk        │ library        │ location(s)       │ license(s)                 │
├─────────────┼────────────────┼───────────────────┼────────────────────────────┤
│ **MEDIUM**  │ vanilla-css    │ package-lock.json │ GPL-3.0                    │
├─────────────┼────────────────┼───────────────────┼────────────────────────────┤
│ UNKNOWN     │ extensions-api │ package-lock.json │ SEE LICENSE IN LICENSE.txt │
└─────────────┴────────────────┴───────────────────┴────────────────────────────┘
```

### Freshness
The table lists all available updates for direct dependencies. If the freshness risk exceeds your objective, it will be marked in red and the script will use the corresponding exit code.

```
┌Available updates─────────────────────────────────────────┬───────────────────────────────────┬────────────────────────────────────────────┐
│ risk       │ library                                     │ location(s)                       │ versions                                   │
├────────────┼─────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────────────────────┤
│ **HIGH**   │ sts                                         │ NotificationService/maven.tree    │ Current version: 2.31.78 (2025-07-09)      │
│            │                                             │                                   │ Next version: 2.32.0 (2025-07-15)          │
│            │                                             │                                   │ Latest version: 2.42.0 (2026-02-24)        │
├────────────┼─────────────────────────────────────────────┼───────────────────────────────────┼────────────────────────────────────────────┤
│ NONE       │ cognitoidentityprovider                     │ AuthService/maven.tree            │ Current version: 2.41.29 (2026-02-14)      │
│            │                                             │                                   │ Next version: 2.41.30 (2026-02-17)         │
│            │                                             │                                   │ Latest version: 2.42.0 (2026-02-24)        │
└────────────┴─────────────────────────────────────────────┴───────────────────────────────────┴────────────────────────────────────────────┘
```

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


