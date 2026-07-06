from SigridRest.SigridGetCommand import SigridGetCommand


class SigridGetUserCommand(SigridGetCommand):
    def __init__(self, customer: str, token: str, user_id: str, base_url=None):
        self.user_id = user_id
        super().__init__(customer, token, base_url=base_url)

    def get_url(self) -> str:
        return f'{self.base_url}/rest/auth/api/user-management/{self.customer}/users/{self.user_id}'


