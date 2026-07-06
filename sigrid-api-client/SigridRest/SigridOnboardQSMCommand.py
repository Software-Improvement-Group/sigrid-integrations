from SigridRest.SigridPostCommand import SigridPostCommand


class SigridOnboardQSMCommand(SigridPostCommand):

    def __init__(self, customer: str, token: str, user_name: str, mendix_token: str, app_id: str,
                 app_name: str, team_server_branch: str = '', base_url=None):
        payload = dict(
            userName=user_name,
            mendixToken=mendix_token,
            appId=app_id,
            appName=app_name,
            teamServerBranch=team_server_branch
        )
        if base_url is not None:
            print("WARNING: This API is not expected to do anything meaningful outside of the standard cloud-based Sigrid instance.")
        super().__init__(customer=customer, token=token, payload=payload, system=None, base_url=base_url)

    def get_url(self):
        url = f'{self.base_url}/rest/inboundresults/qsm/{self.customer}'
        return url
