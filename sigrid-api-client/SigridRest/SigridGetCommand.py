import abc
from abc import ABC

import requests
from requests import Response

from SigridRest.SigridCommand import SigridCommand, check_error_code


class SigridGetCommand(SigridCommand, ABC):

    @abc.abstractmethod
    def __init__(self, customer, token, system=None, base_url=None):
        super().__init__(customer, token, system, base_url=base_url)

    def do_request(self) -> str:
        return self.do_request_raw().content.decode("utf-8")

    def do_request_raw(self) -> Response:
        result = requests.get(url=self.get_url(), headers=self.get_headers())
        check_error_code(result, True)
        return result
