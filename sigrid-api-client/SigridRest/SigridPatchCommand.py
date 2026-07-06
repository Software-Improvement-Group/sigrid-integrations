from abc import ABC
from tabnanny import check
from typing import Union, Optional

import requests
from requests import Response

from SigridRest.SigridBaseUpdateCommand import SigridBaseUpdateCommand
from SigridRest.SigridCommand import check_error_code


class SigridPatchCommand(SigridBaseUpdateCommand, ABC):
    def __init__(self, customer: str, token: str, payload: Union[dict, str], system: Optional[str] = None,
                 base_url=None):
        super().__init__(customer, token, payload, system, base_url=base_url)
        self._request = requests.patch

    def do_request(self, dry_run=False) -> Optional[Response]:
        if self.payload is None or self.payload == '{}':
            print(f'Not patching anything for cust: {self.customer} and system: {self.system}')
            return None
        if dry_run:
            print(f'Cust: {self.customer}, sys: {self.system}, payload: {self.payload}')
            return None
        result = requests.patch(url=self.get_url(), headers=self.get_headers(), data=self.get_payload())
        check_error_code(result)
        return result


