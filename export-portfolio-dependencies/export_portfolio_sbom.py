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

import json
import os
import sys
import urllib.request
from argparse import ArgumentParser


def fetch(path, token):
    request = urllib.request.Request(f"{args.sigridurl}/rest/analysis-results/api/v1{path}")
    request.add_header("Accept", "application/json")
    request.add_header("Authorization", f"Bearer {token}".encode("utf8"))
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def filterSystem(systemSBOM, metadata):
    systemName = systemSBOM["metadata"]["component"]["name"]
    systemMetadata = next((sm for sm in metadata if sm["systemName"] == systemName), None)

    divisionFilter = args.division.split(",") if args.division else None
    teamFilter = args.team.split(",") if args.team else None

    if divisionFilter and systemMetadata["divisionName"] not in divisionFilter:
        return False

    if teamFilter and not bool(set(teamFilter) & set(systemMetadata["teamNames"])):
        return False

    return True


if __name__ == "__main__":
    parser = ArgumentParser(description="Exports an SBOM for a subset of your Sigrid portfolio..")
    parser.add_argument("--customer", type=str, required=True, help="Sigrid customer name.")
    parser.add_argument("--out", type=str, required=True, help="Output file.")
    parser.add_argument("--division", type=str, help="Filter systems on 'division' metadata.")
    parser.add_argument("--team", type=str, help="Filter systems on 'team' metadata.")
    parser.add_argument("--sigridurl", type=str, default="https://sigrid-says.com", help="Sigrid base URL.")
    args = parser.parse_args()

    token = os.environ.get("SIGRID_CI_TOKEN") or os.environ.get("SIGRID_TOKEN")

    if token is None:
        print("Missing Sigrid API token in environment variable SIGRID_CI_TOKEN or SIGRID_TOKEN")
        sys.exit(1)

    if not args.out.endswith((".json", ".sbom")):
        print(f"Invalid output file name, only .json and .sbom are supported: {args.out}")
        sys.exit(1)

    sbom = fetch(f"/osh-findings/{args.customer}", token)
    metadata = fetch(f"/system-metadata/{args.customer}", token)

    sbom["systems"] = [system for system in sbom["systems"] if filterSystem(system["sbom"], metadata)]

    with open(os.path.expanduser(args.out), "w", encoding="utf-8") as f:
        json.dump(sbom, f, indent=4)
