from typing import Union

from SigridRest.SigridPutCommand import SigridPutCommand


class SigridUpdateUserCommand(SigridPutCommand):
    def __init__(self, customer: str, token: str, user_id: str, payload: Union[str, dict],
                 base_url=None):
        self.user_id = user_id
        super().__init__(customer, token, payload, None, base_url=base_url)

    def get_url(self) -> str:
        return f'{self.base_url}/rest/auth/api/user-management/{self.customer}/users/{self.user_id}/permissions'