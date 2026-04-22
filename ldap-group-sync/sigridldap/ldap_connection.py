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
import ssl
from dataclasses import dataclass

from ldap3 import ALL, Connection, Server, Tls
from ldap3.core.exceptions import LDAPException


@dataclass
class LdapConfig:
    url: str
    bindDN: str
    bindPassword: str
    userDN: str
    userQuery: str
    userFirstNameAttr: str
    userLastNameAttr: str
    userEmailAttr: str
    groupDN: str
    groupQuery: str
    groupNameAttr: str
    groupMemberAttr: str


@dataclass
class LdapUser:
    uid: str
    email: str
    firstName: str
    lastName: str


@dataclass
class LdapGroup:
    name: str
    userIds: list[str]


class LdapConnection:
    def __init__(self, config: LdapConfig):
        self.config = config

        self.url = os.environ["SIGRID_LDAP_URL"]

        tls = None
        if os.environ.get("LDAP_CA_CERT"):
            tls = Tls(
                ca_certs_file=os.environ["LDAP_CA_CERT"],
                validate=ssl.CERT_REQUIRED
            )

        self.server = Server(self.url, tls=tls, get_info=ALL)

        self.connection = Connection(
            self.server,
            config.bindDN,
            config.bindPassword,
            auto_bind=False
        )

        try:
            self.connection.open()

            if tls and not self.server.ssl:
                self.connection.start_tls()

            self.connection.bind()

            if self.server.ssl:
                print(f"LDAP connected using LDAPS to {self.server.host}")
            elif self.connection.tls_started:
                print(f"LDAP connected using StartTLS to {self.server.host}")
            else:
                print(f"LDAP connected without TLS to {self.server.host}")

        except LDAPException as e:
            raise RuntimeError(f"Failed to connect to LDAP server {self.url}: {e}") from e

    def listUsers(self) -> list[LdapUser]:
        self.connection.search(
            search_base=self.config.userDN,
            search_filter=f"({self.config.userQuery})",
            attributes=[
                self.config.userFirstNameAttr,
                self.config.userLastNameAttr,
                self.config.userEmailAttr
            ]
        )
        return [
            self.parseUserEntry(entry)
            for entry in self.connection.entries
            if entry[self.config.userEmailAttr].value is not None
        ]

    def parseUserEntry(self, entry) -> LdapUser:
        uid = entry.entry_dn
        email = entry[self.config.userEmailAttr].value
        firstName = entry[self.config.userFirstNameAttr].value
        lastName = entry[self.config.userLastNameAttr].value
        return LdapUser(uid, email, firstName, lastName)

    def listGroups(self) -> list[LdapGroup]:
        self.connection.search(
            search_base=self.config.groupDN,
            search_filter=f"({self.config.groupQuery})",
            attributes=[
                self.config.groupNameAttr,
                self.config.groupMemberAttr
            ]
        )
        return [self.parseGroupEntry(entry) for entry in self.connection.entries]

    def parseGroupEntry(self, entry) -> LdapGroup:
        name = str(entry[self.config.groupNameAttr])
        userIds = [str(member) for member in entry[self.config.groupMemberAttr].values]
        return LdapGroup(name, userIds)