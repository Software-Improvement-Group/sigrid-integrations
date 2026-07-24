import json
from functools import singledispatchmethod
from typing import Dict, List, Union, Optional

from openpyxl.worksheet import worksheet

from SigridSystemMetadata.Users.SigridGetUserCommand import SigridGetUserCommand
from SigridSystemMetadata.Users.SigridUpdateUserCommand import SigridUpdateUserCommand
from Utils.DictUtils import diff_dicts
from Utils.ExcelUtils import parseType, ExcelTypes, load_from_excel_as_type


class SigridUser:
    ID = "id"
    FIRST_NAME = "firstName"
    LAST_NAME = "lastName"
    EMAIL = "email"
    IS_ADMIN = "isAdmin"
    ACCESS_TO_ALL = "accessToAll"
    SYSTEMS = "systems"
    LAST_LOGIN_AT = "lastLoginAt"

    field_order = [ID, FIRST_NAME, LAST_NAME, EMAIL, IS_ADMIN, ACCESS_TO_ALL, SYSTEMS, LAST_LOGIN_AT]
    updatable_permissions = [ACCESS_TO_ALL, SYSTEMS]
    type_mapping = {ID: ExcelTypes.STRING, FIRST_NAME: ExcelTypes.STRING, LAST_NAME: ExcelTypes.STRING,
                    EMAIL: ExcelTypes.STRING, IS_ADMIN: ExcelTypes.BOOL, ACCESS_TO_ALL: ExcelTypes.BOOL,
                    SYSTEMS: ExcelTypes.STRING_ARRAY, LAST_LOGIN_AT: ExcelTypes.STRING}

    def __init__(self,
                 user_id: str,
                 first_name: str,
                 last_name: str,
                 email: str,
                 is_admin: bool,
                 access_to_all: bool,
                 systems: Union[List[Dict], List[str]],
                 last_login_at: str,
                 ):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.access_to_all = access_to_all

        # Sigrid API reports an array of objects that only have a single attribute.
        # we will convert it to an array of the system names if we receive it.
        if len(systems) == 0 or isinstance(systems[0], str):
            self.systems: List[str] = systems
        elif isinstance(systems[0], dict):
            self.systems: List[str] = [x['systemName'] for x in systems]
        else:
            raise TypeError(f'Unknown type {type(systems)} \n {systems}')

        self.last_login_at = last_login_at

    @classmethod
    def from_excel(cls, xlsx_file) -> Dict[str, 'SigridUser']:
        user_dict = {}
        data = load_from_excel_as_type(xlsx_file, cls.type_mapping)
        for entry in data:
            user = cls.from_dict(entry)
            user_dict[user.id] = user
        return user_dict

    @classmethod
    def from_dict(cls, data: Dict):
        if SigridUser.ID not in data:
            raise KeyError(f'Provided dict {data} does not contain Sigrid userID and is not valid')
        return cls(
            data[SigridUser.ID],
            data[SigridUser.FIRST_NAME],
            data[SigridUser.LAST_NAME],
            data[SigridUser.EMAIL],
            data[SigridUser.IS_ADMIN],
            data[SigridUser.ACCESS_TO_ALL],
            data[SigridUser.SYSTEMS],
            data[SigridUser.LAST_LOGIN_AT],
        )

    @classmethod
    def from_sigrid(cls, customer: str, token: str, user_id: str,
                    base_url=None) -> Optional['SigridUser']:
        dict = json.loads(SigridGetUserCommand(customer, token, user_id, base_url=base_url).do_request())
        if dict is None:
            print(f'User {user_id} not found in Sigrid for {customer}')
            return None
        return cls.from_dict(dict)

    def to_dict(self):
        return {
            self.ID: self.id,
            self.FIRST_NAME: self.first_name,
            self.LAST_NAME: self.last_name,
            self.EMAIL: self.email,
            self.IS_ADMIN: self.is_admin,
            self.ACCESS_TO_ALL: self.access_to_all,

            # for compatibility with Sigrid API, we convert the string array back to a dict array.
            self.SYSTEMS: [{'systemName': x} for x in self.systems],
            self.LAST_LOGIN_AT: self.last_login_at
        }

    def write_to_excel(self, ws: worksheet):
        field_arr = [self.id, self.first_name, self.last_name, self.email, self.is_admin, self.access_to_all,
                     self.systems, self.last_login_at]
        ws.append([parseType(x) for x in field_arr])

    def _get_diff_dict(self, other: 'SigridUser'):
        def filter_dict(in_dict: dict):
            return {key: in_dict[key] for key in self.updatable_permissions}

        new_dict = filter_dict(self.to_dict())
        old_dict = filter_dict(other.to_dict())

        return diff_dicts(new_dict=new_dict, old_dict=old_dict)

    def update_permissions(self, customer: str, token: str, dry_run: bool = True,
                           base_url=None):
        old_user = SigridUser.from_sigrid(customer, token, self.id, base_url=base_url)
        if old_user is None:
            print(
                f'Unable to find user {self.first_name} {self.last_name} with ID {self.id}, '
                f'cannot insert users via API. Skipping.')
            return

        diff = self._get_diff_dict(old_user)
        if len(diff) == 0:
            print(f'No updates for user {self.id}, {self.email}')
            return
        print(f'Updating user {self.id}, {self.email}')
        cmd = SigridUpdateUserCommand(customer, token, self.id, diff, base_url=base_url)
        cmd.do_request(dry_run)
