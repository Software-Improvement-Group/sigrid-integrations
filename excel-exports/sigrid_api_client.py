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


class SigridApiClient:
    def __init__(self, sigridURL, customer):
        self.sigridURL = sigridURL
        self.customer = customer
        self.token = os.environ["SIGRID_CI_TOKEN"]

    def callEndPoint(self, path):
        request = urllib.request.Request(f"{self.sigridURL}/rest/analysis-results/api/v1{path}")
        request.add_header("Accept", "application/json")
        request.add_header("Authorization", f"Bearer {self.token}".encode("utf8"))

        with urllib.request.urlopen(request) as response:
            if response.status >= 400:
                raise Exception(f"Sigrid API returns HTTP status {response.status}")
            return json.load(response)

    def fetchMetadata(self):
        response = self.callEndPoint(f"/system-metadata/{self.customer}")
        return {system["systemName"]: system for system in response}

    def fetchObjectivesEvaluation(self):
        response = self.callEndPoint(f"/objectives-evaluation/{self.customer}")
        return response["systems"]

    def fetchSecurityFindings(self, system):
        return self.callEndPoint(f"/security-findings/{self.customer}/{system}")

    def fetchArchitectureQuality(self, system):
        return self.callEndPoint(f"/architecture-quality/{self.customer}/{system}")

    def fetchUsers(self):
        request = urllib.request.Request(f"{self.sigridURL}/rest/auth/api/user-management/{self.customer}/users")
        request.add_header("Accept", "application/json")
        request.add_header("Authorization", f"Bearer {self.token}".encode("utf8"))

        with urllib.request.urlopen(request) as response:
            if response.status >= 400:
                raise Exception(f"Sigrid API returns HTTP status {response.status}")
            response = json.load(response)
            return response["users"]
