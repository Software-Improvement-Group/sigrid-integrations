# Sigrid LDAP group synchronization

Synchronizes group memberships from LDAP groups to Sigrid user groups.

Groups are assumed to be connected if the LDAP group and Sigrid user group have the same name. The group memberships
for each Sigrid user group are then updated, based on the users in the corresponding LDAP group. 

The [Sigrid user management API](https://docs.sigrid-says.com/integrations/sigrid-api-documentation.html#user-management)
is used for interaction between these scripts and Sigrid.

## Prerequisites

- You need Python 3.9+
- Install the dependencies: `pip3 install -r requirements.txt --user`
- You need a [Sigrid API token](https://docs.sigrid-says.com/organization-integration/authentication-tokens.html)
  - This token needs to have administrator rights (since user management requires administrator rights)
  - Your Sigrid API token (also known as `SIGRID_CI_TOKEN` in other Sigrid integrations) needs to be available to the script via the `SIGRID_UM_TOKEN` environment variable

## Usage

Configuration is done using environment variables:

| Name                               | Example                              | Description                                                       |
|------------------------------------|--------------------------------------|-------------------------------------------------------------------|
| `SIGRID_UM_URL`                    | https://sigrid-says.com              | Sigrid base URL.                                                  |
| `SIGRID_UM_CUSTOMER`               | mycompany                            | Your Sigrid customer name.                                        |
| `SIGRID_UM_TOKEN`                  | (token)                              | Sigrid API token with administrator privileges.                   |
| `SIGRID_LDAP_URL`                  | ldap://ldap.example.com:389          | LDAP URL.                                                         |
| `SIGRID_LDAP_BIND_DN`              | cn=read-only-admin,dc=example,dc=com | LDAP DN used for authenticating this integration.                 |
| `SIGRID_LDAP_BIND_PASSWORD`        | (password)                           | LDAP password used for authenticating this integration.           |
| `SIGRID_LDAP_USER_DN`              | dc=example,dc=com                    | Locations of users to sync.                                       |
| `SIGRID_LDAP_USER_QUERY`           | objectclass=inetOrgPerson            | Query on user DN to get the list of user objects.                 |
| `SIGRID_LDAP_USER_FIRST_NAME_ATTR` | cn                                   | Name of the LDAP attribute used for users' first names.           |
| `SIGRID_LDAP_USER_LAST_NAME_ATTR`  | cn                                   | Name of the LDAP attribute used for users' last names.            |
| `SIGRID_LDAP_USER_EMAIL_ATTR`      | mail                                 | Name of the LDAP attribute used for users' email addresses.       |
| `SIGRID_LDAP_GROUP_DN`             | dc=example,dc=com                    | Location of groups to sync.                                       |
| `SIGRID_LDAP_GROUP_QUERY`          | objectclass=groupOfUniqueNames       | Query on group DN to get the list of group objects.               |
| `SIGRID_LDAP_GROUP_NAME_ATTR`      | cn                                   | Name of the LDAP attribute used for group names.                  |
| `SIGRID_LDAP_GROUP_MEMBER_ATTR`    | uniqueMember                         | (Optional) Name of the LDAP attribute used for group memberships. |
| `SIGRID_CA_CERT`                   | mysigridcert.pem                     | (Optional) Path to `.pem` file for connecting to Sigrid.          |
| `LDAP_CA_CERT`                     | myldapcert.pem                       | (Optional) Path to `.pem` file for connecting to LDAP.            |


Once all environment variables are in place, you can run the integration:

    ./sigrid_ldap_group_sync.py

You would typically run this as a scheduled job, to periodically perform this synchronization. However, it's also 
possible to run this manually or ad-hoc.

## License

Copyright Software Improvement Group

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
