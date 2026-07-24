from abc import ABC
from typing import Optional

import requests
from requests import Response

from SigridRest.SigridBaseUpdateCommand import SigridBaseUpdateCommand
from SigridRest.SigridCommand import check_error_code


class SigridPutCommand(SigridBaseUpdateCommand, ABC):
    def do_request(self, dry_run: bool = False) -> Optional[Response]:
        if dry_run:
            print(self.payload)
            return
        else:
            result = requests.put(url=self.get_url(), headers=self.get_headers(), data=self.get_payload())
            check_error_code(result)
            return result
