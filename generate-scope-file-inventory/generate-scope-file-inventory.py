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
    
    print("system, external_id, division, date, sfir, excludes, osh_enabled, osh_excludes, security_enabled, security_excludes, architecture_enabled")
    
    for system in systems:
        try:
            date, scope = get_scope_data(api_client, system)
        except Exception as e:
            print(f"{system}, Error")
            continue
        metadata = api_client.fetchSystemMetadata(system)
        external_id = metadata.get("externalID", "")
        division = metadata.get("divisionName", "")
        scope_file_in_repo = metadata.get("scopeFileInRepository", "")
        excludes = len(scope.get("exclude", {}))
        osh_enabled = scope.get("dependencychecker") is not None
        osh_excludes = len(scope.get("dependencychecker", {}).get("exclude", []))
        security_enabled = scope.get("thirdpartyfindings", {}).get("enabled") is True
        security_excludes = len(scope.get("thirdpartyfindings", {}).get("exclude", []))
        architecture_enabled = scope.get("architecture", {}).get("enabled") is not False
        print(f"{system}, {external_id}, {division}, {date}, {scope_file_in_repo}, {excludes}, {osh_enabled}, {osh_excludes}, {security_enabled}, {security_excludes}, {architecture_enabled}")
