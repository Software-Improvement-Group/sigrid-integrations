#!/usr/bin/env python3

# Copyright Software Improvement Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
import json
import os
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from http.client import RemoteDisconnected
from json import JSONDecodeError
import ssl

from terminaltables3 import SingleTable
from typing import Dict, List
import urllib.parse
import urllib.request
import urllib.error
from urllib.error import URLError
import logging

LOG = logging.getLogger(__name__)


class Risk(Enum):
    UNKNOWN = 0
    NONE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class FindingType:
    name: str
    objective_name: str
    risk_name: str
    exit_code: int


SIGRID_CI_TOKEN_ENV_NAME = "SIGRID_CI_TOKEN"

RELEASE_DATE_PROPERTY = "sigrid:releaseDate"
NEXT_VERSION_PROPERTY = "sigrid:next:version"
NEXT_VERSION_DATE_PROPERTY = "sigrid:next:releaseDate"
LATEST_VERSION_PROPERTY = "sigrid:latest:version"
LATEST_VERSION_DATE_PROPERTY = "sigrid:latest:releaseDate"
TRANSITIVE_PROPERTY = "sigrid:transitive"
TRANSITIVE_VALUE = "TRANSITIVE"

VULNERABILITY_FINDING_TYPE = FindingType(
    "vulnerability risk", "OSH_MAX_SEVERITY", "sigrid:risk:vulnerability", 1
)
LEGAL_FINDING_TYPE = FindingType(
    "license risk", "OSH_MAX_LICENSE_RISK", "sigrid:risk:legal", 2
)
FRESHNESS_FINDING_TYPE = FindingType(
    "freshness risk", "OSH_MAX_FRESHNESS_RISK", "sigrid:risk:freshness", 4
)


class SigridApiClient:
    def __init__(self, customer: str, system: str, sigrid_url: str):
        self.customer = customer.lower()
        self.system = system.lower()
        self.sigrid_url = sigrid_url

    def get_osh_results(self):
        return self.send_request(
            f"/rest/analysis-results/api/v1/osh-findings/{self.customer}/{self.system}/current"
        )

    def get_objectives(self):
        return self.send_request(
            f"/rest/analysis-results/api/v1/objectives/{self.customer}/{self.system}/config"
        )

    def send_request(self, path):
        try:
            req = urllib.request.Request(f"{self.sigrid_url}{path}")
            req.add_header(
                "Authorization", "Bearer " + os.environ.get(SIGRID_CI_TOKEN_ENV_NAME)
            )
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(req, context=context) as response:
                return json.loads(self.handle_response(response))
        except URLError as e:
            LOG.error("Unable to connect to Sigrid API: %s", str(e))
            return None
        except RemoteDisconnected:
            LOG.error("Sigrid disconnected or timed out")
            return None
        except JSONDecodeError:
            LOG.error("Sigrid API response contains invalid JSON")
            return None

    @staticmethod
    def handle_response(response):
        if response.status == 200:
            body = response.read().decode("utf-8")
            LOG.info("Sigrid returned JSON (length: %s chars)", len(body))
            return body
        else:
            LOG.error("Sigrid returned status code %s", response.status)
            return None


def risk_exceeds_objective(
    component: Dict, risk_name: str, objective_value: str
) -> bool:
    risk_value = get_property_value(component, risk_name)
    return (risk_value.lower() != "none") and (
        Risk[risk_value].value > Risk[objective_value].value
    )


def get_property_value(component: Dict, property_name: str) -> str:
    return next(
        iter(
            [
                property.get("value")
                for property in component.get("properties")
                if property.get("name") == property_name
            ]
        ),
        None,
    )


def is_transitive(component) -> bool:
    return get_property_value(component, TRANSITIVE_PROPERTY) == TRANSITIVE_VALUE


def get_locations(component) -> str:
    locations = [
        location.get("location")
        for location in component.get("evidence").get("occurrences")
    ]
    locations_limit = 3
    if len(locations) > locations_limit:
        return (
            ",\n".join(locations[:locations_limit])
            + f"\nand {len(locations) - locations_limit} other location(s)"
        )

    return "\n".join(locations)


def get_warning_text(text: str) -> str:
    return f"\033[91m\033[1m{text}\033[0m"


def get_colored_risk(risk: str, objective: str) -> str:
    if Risk[risk].value > Risk[objective].value:
        return get_warning_text(risk)
    return risk


def get_vulnerability_risks(sbom: Dict, objective: str) -> int:
    findings = [
        dep
        for dep in sbom.get("components")
        if risk_exceeds_objective(
            dep, VULNERABILITY_FINDING_TYPE.risk_name, Risk.NONE.name
        )
    ]
    libraries_not_meeting_objective = len(
        [
            dep
            for dep in sbom.get("components")
            if risk_exceeds_objective(
                dep, VULNERABILITY_FINDING_TYPE.risk_name, objective
            )
            and not is_transitive(dep)
        ]
    )

    if findings:
        table = [["risk", "library", "type", "locations", "description"]]
        table_data = []
        for finding in findings:
            vulnerability_details = [
                v
                for v in sbom.get("vulnerabilities")
                if finding.get("bom-ref") in [ref["ref"] for ref in v["affects"]]
            ]
            table_data.append(
                [
                    get_property_value(finding, VULNERABILITY_FINDING_TYPE.risk_name),
                    finding.get("name"),
                    get_property_value(finding, TRANSITIVE_PROPERTY),
                    get_locations(component=finding),
                    "\n\n".join(
                        [summarize_vulnerability(v) for v in vulnerability_details]
                    ),
                ]
            )
        table.extend(sort_and_color_table(table_data, objective))

        table_instance = SingleTable(table, "Detected vulnerabilities")
        table_instance.inner_row_border = True
        print(table_instance.table + "\n\n")
        if libraries_not_meeting_objective > 0:
            return VULNERABILITY_FINDING_TYPE.exit_code
    return 0


def summarize_vulnerability(vulnerability: Dict) -> str:
    details = [
        f"ID: {vulnerability.get('id')}",
        f"Published: {vulnerability.get('published')[:10]}",
    ]
    if vulnerability.get("ratings"):
        details.append(
            f"Severity: {vulnerability.get('ratings')[0].get('score')} ({vulnerability.get('ratings')[0].get('severity')})"
        )
    if vulnerability.get("source", {}).get("url", None):
        details.append(f"URL: {vulnerability.get('source').get('url')}")
    if vulnerability.get("description"):
        details.append(f"Description: {vulnerability.get('description')}")

    return "\n".join(details)


def get_legal_risks(components: List[Dict], objective: str) -> int:
    findings = [
        dep
        for dep in components
        if risk_exceeds_objective(dep, LEGAL_FINDING_TYPE.risk_name, objective)
        or get_property_value(dep, LEGAL_FINDING_TYPE.risk_name) == Risk.UNKNOWN.name
    ]
    libraries_not_meeting_objective = len(
        [
            dep
            for dep in components
            if risk_exceeds_objective(dep, LEGAL_FINDING_TYPE.risk_name, objective)
        ]
    )
    if findings:
        table = [["risk", "library", "location(s)", "license(s)"]]
        table_data = []
        for finding in findings:
            table_data.append(
                [
                    get_property_value(finding, LEGAL_FINDING_TYPE.risk_name),
                    finding.get("name"),
                    get_locations(finding),
                    "\n".join(
                        [l.get("license").get("name") for l in finding.get("licenses")]
                    ),
                ]
            )
        table.extend(sort_and_color_table(table_data, objective))
        table_instance = SingleTable(table, "Legal risks")
        table_instance.inner_row_border = True
        print(table_instance.table + "\n\n")
        if libraries_not_meeting_objective > 0:
            return LEGAL_FINDING_TYPE.exit_code
    return 0


def sort_and_color_table(table: List[List], objective: str) -> List[List]:
    table = sorted(table, key=lambda row: (Risk[row[0]].value, row[1]), reverse=True)
    for row in table:
        row[0] = get_colored_risk(row[0], objective)
    return table


def get_updates(components: List[Dict], objective: str) -> int:
    updates_available = [
        dep
        for dep in components
        if get_property_value(dep, NEXT_VERSION_PROPERTY) and not is_transitive(dep)
    ]
    libraries_not_meeting_objective = len(
        [
            dep
            for dep in components
            if risk_exceeds_objective(dep, FRESHNESS_FINDING_TYPE.risk_name, objective)
            and not is_transitive(dep)
        ]
    )
    if updates_available:
        table = [["risk", "library", "location(s)", "versions"]]
        table_data = []
        for library in updates_available:
            table_data.append(
                [
                    get_property_value(library, FRESHNESS_FINDING_TYPE.risk_name),
                    library.get("name"),
                    get_locations(library),
                    get_version_info(library),
                ]
            )
        table.extend(sort_and_color_table(table_data, objective))

        table_instance = SingleTable(table, "Available updates")
        table_instance.inner_row_border = True
        print(table_instance.table + "\n\n")
        if libraries_not_meeting_objective > 0:
            return FRESHNESS_FINDING_TYPE.exit_code
    return 0


def get_version_info(library: Dict) -> str:
    result = [
        f"Current version: {library.get('version')} ({get_property_value(library, RELEASE_DATE_PROPERTY)[:10]})",
        f"Next version: {get_property_value(library, NEXT_VERSION_PROPERTY)} ({get_property_value(library, NEXT_VERSION_DATE_PROPERTY)[:10]})",
        f"Latest version: {get_property_value(library, LATEST_VERSION_PROPERTY)} ({get_property_value(library, LATEST_VERSION_DATE_PROPERTY)[:10]})",
    ]
    return "\n".join(result)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Generates a report on the current status of OpenSource Health for a system"
    )
    parser.add_argument("--customer", type=str, help="Sigrid customer name.")
    parser.add_argument("--system", type=str, help="Sigrid system name.")
    parser.add_argument("--sigridurl", type=str, default="https://sigrid-says.com")
    args = parser.parse_args()

    if not os.environ.get(SIGRID_CI_TOKEN_ENV_NAME):
        print("Missing Sigrid API token in environment variable SIGRID_CI_TOKEN")
        sys.exit(1)

    sigrid = SigridApiClient(args.customer, args.system, args.sigridurl)
    objectives = sigrid.get_objectives()
    osh_results = sigrid.get_osh_results()

    exit_code = 0
    exit_code += get_vulnerability_risks(
        osh_results, objectives.get(VULNERABILITY_FINDING_TYPE.objective_name)
    )
    exit_code += get_updates(
        osh_results.get("components"),
        objectives.get(FRESHNESS_FINDING_TYPE.objective_name),
    )
    exit_code += get_legal_risks(
        osh_results.get("components"), objectives.get(LEGAL_FINDING_TYPE.objective_name)
    )

    if exit_code:
        print(get_warning_text("Risks exceeding your objectives have been found"))
        print("Findings exceeding your objectives are marked in red in the output")

    exit(exit_code)
