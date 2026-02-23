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

from typing import Iterator

from .sigrid_user_management import SigridUserManagement
from .ldap_connection import LdapConnection, LdapGroup, LdapUser


def syncUserGroups(sigrid: SigridUserManagement, ldapConnection: LdapConnection) -> None:
    ldapGroups = ldapConnection.listGroups()
    sigridGroups = {group["name"]: group for group in sigrid.listUserGroups()}

    for group in findMissingGroups(ldapGroups, sigridGroups):
        print(f"Creating Sigrid user group '{group.name}'")
        sigridGroups[group.name] = sigrid.createUserGroup(group.name)

    for group in findOrphanGroups(ldapGroups, sigridGroups):
        print(f"Removing Sigrid user group '{group}'")
        sigrid.deleteUserGroup(group)


def syncGroupMemberships(sigrid: SigridUserManagement, ldapConnection: LdapConnection) -> None:
    sigridGroups = {group["name"]: group for group in sigrid.listUserGroups()}
    connectedLdapGroups = [group for group in ldapConnection.listGroups() if group.name in sigridGroups]

    ldapUsers = ldapConnection.listUsers()
    sigridUsers = {user["email"]: user for user in sigrid.listUsers()}

    for ldapGroup in connectedLdapGroups:
        print(f"Synchronizing group memberships for '{ldapGroup.name}'")
        ldapGroupUsers = list(findLdapUsers(ldapGroup, ldapUsers))
        sigridGroupUserIds = []

        for ldapUser in ldapGroupUsers:
            if ldapUser.email not in sigridUsers:
                print(f"Creating missing Sigrid SSO user '{ldapUser.email}'")
                sigridUsers[ldapUser.email] = sigrid.createUser(ldapUser.email, ldapUser.firstName, ldapUser.lastName)
            sigridGroupUserIds.append(sigridUsers[ldapUser.email]["id"])

        sigrid.updateGroupMembers(sigridGroups[ldapGroup.name]["id"], sigridGroupUserIds)


def findMissingGroups(ldapGroups: list[LdapGroup], sigridGroups: dict) -> list[LdapGroup]:
    return [group for group in ldapGroups if group.name not in sigridGroups]


def findOrphanGroups(ldapGroups: list[LdapGroup], sigridGroups: dict) -> list[str]:
    ldapGroupNames = [group.name for group in ldapGroups]
    return [groupName for groupName in sigridGroups if groupName not in ldapGroupNames]


def findLdapUsers(group: LdapGroup, users: list[LdapUser]) -> Iterator[LdapUser]:
    uids = {user.uid: user for user in users}

    for uid in group.userIds:
        if uid in uids:
            yield uids[uid]
        else:
            print(f"Warning: user '{uid}' is a member of group '{group.name}', but found no matching LDAP user")
