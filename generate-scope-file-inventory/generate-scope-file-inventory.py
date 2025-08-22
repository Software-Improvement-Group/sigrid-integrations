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

from dataclasses import dataclass
import yaml
import os
import sys
import csv
from datetime import datetime
from argparse import ArgumentParser, SUPPRESS
from sigrid_api_client import SigridApiClient

@dataclass
class scope_file:
    system: str
    snapshot: datetime
    scope: dict

def get_scope_data(api, system):
    response = api.fetchArchitectureRaw(system)
    if response is not None:
        date = response["snapshot"]["date"][:10]
        scope = yaml.safe_load(response["metadata"]["scopeFile"])
        return date, scope

if __name__ == "__main__":
    parser = ArgumentParser(description="Creates an overview of scope files for a customer")
    parser.add_argument("--customer", type=str, help="Sigrid customer name.")
    parser.add_argument("--system", type=str, help="Sigrid system name.")
    parser.add_argument("--out", type=str, default="scope_inventory.csv")
    parser.add_argument("--sigridurl", type=str, default="https://sigrid-says.com", help=SUPPRESS)
    args = parser.parse_args()

    if None in [args.customer]:
        parser.print_help()
        sys.exit(1)

    if not os.environ.get("SIGRID_CI_TOKEN"):
        print("Missing Sigrid API token in environment variable SIGRID_CI_TOKEN")
        sys.exit(1)

    api_client = SigridApiClient(args.sigridurl, args.customer, os.environ["SIGRID_CI_TOKEN"])
    
    if args.system is None:
        systems = api_client.fetchSystemNames()
    else:
        systems = [args.system]

    fieldnames = [
        "system", "external_id", "division", "date", "age", "sfir",
        "maint_model", "maint_excludes",
        "osh_enabled", "osh_model", "osh_excludes",
        "security_enabled", "security_model", "security_excludes",
        "architecture_enabled"
    ]

    with open(args.out, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for system in systems:
            try:
                date, scope = get_scope_data(api_client, system)
            except Exception as e:
                writer.writerow({"system": system, "external_id": "Error"})
                continue
            metadata = api_client.fetchSystemMetadata(system)
            row = {
                "system": system,
                "external_id": metadata.get("externalID", ""),
                "division": metadata.get("divisionName", ""),
                "date": date,
                "age": (datetime.now() - datetime.strptime(date, "%Y-%m-%d")).days,
                "sfir": metadata.get("scopeFileInRepository", ""),
                "maint_model": scope.get("model", ""),
                "maint_excludes": len(scope.get("exclude", {})),
                "osh_enabled": scope.get("dependencychecker") is not None,
                "osh_model": scope.get("dependencychecker", {}).get("model", ""),
                "osh_excludes": len(scope.get("dependencychecker", {}).get("exclude", [])),
                "security_enabled": scope.get("thirdpartyfindings", {}).get("enabled") is True,
                "security_model": scope.get("thirdpartyfindings", {}).get("model", ""),
                "security_excludes": len(scope.get("thirdpartyfindings", {}).get("exclude", [])),
                "architecture_enabled": scope.get("architecture", {}).get("enabled") is not False,
            }
            writer.writerow(row)
