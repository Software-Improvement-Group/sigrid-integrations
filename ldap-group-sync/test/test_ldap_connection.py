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

from ldap3 import SUBTREE

from sigridldap.ldap_connection import LdapConfig, LdapConnection


OPEN_SOURCE_LDAP_CONFIG = LdapConfig(
    url="ldap://ldap.forumsys.com:389",
    bindDN="cn=read-only-admin,dc=example,dc=com",
    bindPassword="password",
    userDN="dc=example,dc=com",
    userQuery="objectclass=inetOrgPerson",
    userFirstNameAttr="cn",
    userLastNameAttr="cn",
    userEmailAttr="mail",
    groupDN="dc=example,dc=com",
    groupQuery="objectclass=groupOfUniqueNames",
    groupNameAttr="cn",
    groupMemberAttr="uniqueMember"
)


def testConnectLDAP():
    ldapConnection = LdapConnection(OPEN_SOURCE_LDAP_CONFIG)
    ldapConnection.connection.search(
        search_base=OPEN_SOURCE_LDAP_CONFIG.bindDN,
        search_filter="(objectclass=*)",
        attributes=["cn", "sn"]
    )
    users = ldapConnection.connection.entries

    assert len(users) == 1
    assert users[0]["cn"].value == "read-only-admin"
    assert users[0]["sn"].value == "Read Only Admin"
