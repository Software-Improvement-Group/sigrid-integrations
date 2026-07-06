import json
from typing import List

from SigridRest.SigridGetCommand import SigridGetCommand
from SigridSystemMetadata.Users.SigridUser import SigridUser


class SigridGetUsersCommand(SigridGetCommand):
    def __init__(self, customer, token, base_url=None):
        super().__init__(customer, token, base_url=base_url)

    def get_url(self) -> str:
        return f'{self.base_url}/rest/auth/api/user-management/{self.customer}/users'

    def get_users(self) -> List[SigridUser]:
        data_dict = json.loads(self.do_request())
        return [SigridUser.from_dict(user) for user in data_dict['users']]

