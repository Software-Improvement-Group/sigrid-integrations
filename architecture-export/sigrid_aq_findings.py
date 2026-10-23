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
from typing import Iterator
from tabulate import tabulate

from sigridaq.architecture_graph import ArchitectureGraph


QUALIFICATIONS = {
    "UNDESIRABLE" : "🔴",
    "CYCLIC" : "🟠"
}


def fetchArchitectureGraph(sigridURL: str, customer: str, system: str) -> ArchitectureGraph:
    request = urllib.request.Request(f"{sigridURL}/rest/analysis-results/api/v1/architecture-quality/{customer}/{system}/raw")
    request.add_header("Accept", "application/json")
    request.add_header("Authorization", f"Bearer {os.environ['SIGRID_CI_TOKEN']}".encode("utf8"))
    with urllib.request.urlopen(request) as response:
        return ArchitectureGraph(json.load(response))
        
        
def locateArchitectureFindings(architectureGraph: ArchitectureGraph) -> Iterator[tuple[str, str, str]]:
    fileMap = {se["id"]: se for se in architectureGraph.graph["systemElements"] if se["type"] == "FILE"}
    componentMap = {se["id"]: se for se in architectureGraph.graph["systemElements"] if se["type"] == "CODE_COMPONENT"}
    
    parentIds = {}
    for dependency in architectureGraph.findAllHierarchyDependencies():
        if dependency["type"] == "CONTAINS":
            parentIds[dependency["targetElementId"]] = dependency["sourceElementId"]

    for dependency in architectureGraph.findAllCallDependencies():
        for qualification, severity in QUALIFICATIONS.items():
            if qualification in dependency.get("qualifications", []):
                sourceFile = fileMap.get(dependency["sourceElementId"])
                targetFile = fileMap.get(dependency["targetElementId"])
                if sourceFile and targetFile:
                    sourceComponent = componentMap.get(parentIds.get(sourceFile["id"]))
                    targetComponent = componentMap.get(parentIds.get(targetFile["id"]))
                    if sourceComponent and targetComponent:
                        description = formatDescription(qualification, sourceComponent, targetComponent)
                        location = formatLocation(sourceFile, dependency.get("lines"))
                        yield (severity, description, location)
                    
                    
def formatDescription(qualification: str, sourceComponent: dict, targetComponent: dict) -> str:
    if qualification == "UNDESIRABLE":
        return f"Undesirable dependency from {sourceComponent['shortName']} to {targetComponent['shortName']}."
    elif qualification == "CYCLIC":
        return f"Cyclic dependency between {sourceComponent['shortName']} and {targetComponent['shortName']}."
    else:
        raise Exception(f"Unknown dependency qualification: {qualification}")
                    
                    
def formatLocation(file: dict, lines: list[list[int]]) -> str:
    if not lines or len(lines) == 0:
        return file["shortName"]
    return f"{file['shortName']}:{lines[0][0]}"


if __name__ == "__main__":
    parser = ArgumentParser(description="Prints all findings from Sigrid's Architecture Quality to stdout.")
    parser.add_argument("--customer", type=str, required=True, help="Sigrid customer name.")
    parser.add_argument("--system", type=str, required=True, help="Sigrid customer name.")
    parser.add_argument("--sigridurl", type=str, default="https://sigrid-says.com")
    args = parser.parse_args()

    if not os.environ.get("SIGRID_CI_TOKEN"):
        print("Missing environment variable SIGRID_CI_TOKEN")
        sys.exit(1)

    architectureGraph = fetchArchitectureGraph(args.sigridurl, args.customer, args.system)
    columns = ["Severity", "Description", "Location"]
    rows = list(locateArchitectureFindings(architectureGraph))
    table = tabulate(rows, headers=columns, tablefmt="simple")
    print(f"\n{table}\n")
