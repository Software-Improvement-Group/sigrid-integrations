import copy
from typing import Optional
from SigridRest.SigridPostCommand import SigridPostCommand

from requests import Response

class SigridOnboardQSMCommand(SigridPostCommand):

    def __init__(self, customer: str, token: str, user_name: str, mendix_token: str, app_id: str,
                 app_name: str, team_server_branch: str = '', base_url=None):
        self.payload_dict = dict(
            userName=user_name,
            mendixToken=mendix_token,
            appId=app_id,
            appName=app_name,
            teamServerBranch=team_server_branch
        )
        if base_url is not None:
            print("WARNING: This API is not expected to do anything meaningful outside of the standard cloud-based Sigrid instance.")
        super().__init__(customer=customer, token=token, payload=self.payload_dict, system=None, base_url=base_url)

    def get_url(self):
        url = f'{self.base_url}/rest/inboundresults/qsm/{self.customer}'
        return url

    def do_request(self, dry_run=False) -> Optional[Response]:
        if dry_run:
            # Redact the token used in the payload before executing a dry run, then reset it.
            redacted_payload = copy.deepcopy(self.payload_dict)
            redacted_payload['mendixToken'] = '[TOKEN REDACTED]'
            saved_payload = self.payload
            self.set_payload(redacted_payload)
            result = super().do_request(dry_run=dry_run)
            self.set_payload(saved_payload)
        else:
            result = super().do_request(dry_run=dry_run)

        return result
