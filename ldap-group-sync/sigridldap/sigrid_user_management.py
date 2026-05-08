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
import ssl
import sys
import urllib.error
import urllib.request


class SigridUserManagement:
    def __init__(self, sigridURL, customer, token):
        self.sigridURL = sigridURL
        self.customer = customer
        self.token = token

    def callEndPoint(self, method: str, path: str, body=None):
        jsonBody = json.dumps(body).encode("utf8") if body is not None else None
        sslContext = ssl.create_default_context(cafile=os.getenv("SIGRID_CA_CERT")) if os.environ.get("SIGRID_CA_CERT") else None

        request = urllib.request.Request(f"{self.sigridURL}{path}", jsonBody, method=method)
        request.add_header("Accept", "application/json")
        request.add_header("Content-Type", "application/json")
        request.add_header("Authorization", f"Bearer {self.token}".encode("utf8"))

        try:
            with urllib.request.urlopen(request, context=sslContext) as response:
                if response.code == 204:
                    return {}
                return json.load(response)
        except urllib.error.HTTPError as e:
            print(f"Sigrid request to {path} failed with HTTP status {e.code}")
            sys.exit(1)

    def listUserGroups(self):
        response = self.callEndPoint("GET", f"/rest/auth/api/user-management/{self.customer}/groups")
        return response["groups"]

    def createUserGroup(self, name: str):
        return self.callEndPoint("POST", f"/rest/auth/api/user-management/{self.customer}/groups", {
            "name": name,
            "description": "Sigrid user group created automatically based on LDAP group synchronization.",
            "users": [],
            "systems": []
        })

    def deleteUserGroup(self, groupId: str):
        return self.callEndPoint("DELETE", f"/rest/auth/api/user-management/{self.customer}/groups/{groupId}")

    def updateGroupMembers(self, groupId: str, userIds: list[str]):
        return self.callEndPoint("PUT", f"/rest/auth/api/user-management/{self.customer}/groups/{groupId}/members", {
            "users": userIds
        })

    def listUsers(self):
        response = self.callEndPoint("GET", f"/rest/auth/api/user-management/{self.customer}/users")
        return response["users"]

    def createUser(self, email: str, firstName: str, lastName: str):
        return self.callEndPoint("POST", f"/rest/auth/api/user-management/{self.customer}/users", {
            "userInfo": {
                "firstName": firstName,
                "lastName": lastName,
                "emailAddress": email
            },
            "isSSO": True
        })

    def deleteUser(self, userId: str):
        return self.callEndPoint("DELETE", f"/rest/auth/api/user-management/{self.customer}/users/{userId}")
