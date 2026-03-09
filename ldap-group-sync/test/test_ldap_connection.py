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

import ldap

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
    groupMemberAttr="uniqueMember",
)


def testConnectLDAP():
    ldapConnection = LdapConnection(OPEN_SOURCE_LDAP_CONFIG)
    users = ldapConnection.connection.search_s(
        OPEN_SOURCE_LDAP_CONFIG.bindDN, ldap.SCOPE_SUBTREE, "objectclass=*"
    )

    assert len(users) == 1
    assert users[0][1]["cn"][0].decode("utf8") == "read-only-admin"
    assert users[0][1]["sn"][0].decode("utf8") == "Read Only Admin"
