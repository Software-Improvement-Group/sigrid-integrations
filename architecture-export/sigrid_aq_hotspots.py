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

import os
import sys
from argparse import ArgumentParser

from sigridaq.architecture_graph import ArchitectureGraph
from sigridaq.csv_export import exportComponentHotspots
from sigridaq.sigrid_api import fetchArchitectureGraph


def extractComponents(graph: ArchitectureGraph, query: str) -> list:
    if query == "all":
        return graph.getAllComponents()
    elif query == "toplevel":
        return graph.getTopLevelComponents()
    else:
        raise Exception(f"Invalid component option: {query}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Exports architecture hotspot information derived from Sigrid.")
    parser.add_argument("--customer", type=str, required=True, help="Sigrid customer name.")
    parser.add_argument("--system", type=str, required=True, help="Sigrid system name.")
    parser.add_argument("--out", type=str, required=True, help="Output file location.")
    parser.add_argument("--components", type=str, choices=["all", "toplevel", "leaf"], required=True)
    parser.add_argument("--sigridurl", type=str, default="https://sigrid-says.com")
    args = parser.parse_args()

    if not os.environ.get("SIGRID_CI_TOKEN"):
        print("Missing environment variable SIGRID_CI_TOKEN")
        sys.exit(1)

    graph = fetchArchitectureGraph(args.sigridurl, args.customer, args.system)
    components = extractComponents(graph, args.components)
    exportComponentHotspots(components, os.path.expanduser(args.out))

