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
import urllib.request

from .architecture_graph import ArchitectureGraph


def fetchArchitectureGraph(sigridURL: str, customer: str, system: str) -> ArchitectureGraph:
    request = urllib.request.Request(f"{sigridURL}/rest/analysis-results/api/v1/architecture-quality/{customer}/{system}/raw")
    request.add_header("Accept", "application/json")
    request.add_header("Authorization", f"Bearer {os.environ['SIGRID_CI_TOKEN']}".encode("utf8"))
    with urllib.request.urlopen(request) as response:
        return ArchitectureGraph(json.load(response))


def fetchComponentEntanglement(sigridURL: str, customer: str, system: str) -> list:
    request = urllib.request.Request(f"{sigridURL}/rest/analysis-results/api/v1/refactoring-candidates/{customer}/{system}/componentEntanglement")
    request.add_header("Accept", "application/json")
    request.add_header("Authorization", f"Bearer {os.environ['SIGRID_CI_TOKEN']}".encode("utf8"))
    with urllib.request.urlopen(request) as response:
        responseBody = json.load(response)
        return responseBody["refactoringCandidates"]
