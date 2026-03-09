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

from sigridaq.architecture_graph import ArchitectureGraph
from sigridaq.graphviz import exportDot


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Exports data from Sigrid's Architecture Quality."
    )
    parser.add_argument(
        "--customer", type=str, required=True, help="Sigrid customer name."
    )
    parser.add_argument(
        "--system", type=str, required=True, help="Sigrid customer name."
    )
    parser.add_argument(
        "--format",
        choices=["json", "dot", "pdf", "png"],
        required=True,
        help="Export format.",
    )
    parser.add_argument("--out", type=str, required=True, help="Output directory.")
    parser.add_argument("--sigridurl", type=str, default="https://sigrid-says.com")
    args = parser.parse_args()

    if not os.environ.get("SIGRID_CI_TOKEN"):
        print("Missing environment variable SIGRID_CI_TOKEN")
        sys.exit(1)

    request = urllib.request.Request(
        f"{args.sigridurl}/rest/analysis-results/api/v1/architecture-quality/{args.customer}/{args.system}/raw"
    )
    request.add_header("Accept", "application/json")
    request.add_header(
        "Authorization", f"Bearer {os.environ['SIGRID_CI_TOKEN']}".encode("utf8")
    )
    with urllib.request.urlopen(request) as response:
        architectureGraph = ArchitectureGraph(json.load(response))

    outputDir = os.path.expanduser(args.out)
    os.makedirs(outputDir, exist_ok=True)

    if args.format == "json":
        with open(
            f"{outputDir}/{args.customer}-{args.system}-architecture.json",
            "w",
            encoding="utf8",
        ) as f:
            json.dump(architectureGraph, f, indent=2)
    else:
        dotFile = f"{outputDir}/{args.customer}-{args.system}-architecture.dot"
        exportDot(architectureGraph, dotFile, args.format)
