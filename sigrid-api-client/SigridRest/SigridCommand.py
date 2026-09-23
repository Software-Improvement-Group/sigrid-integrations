import abc
from abc import ABC
from typing import Optional

from requests import Response

DEFAULT_SIGRID_URL = 'https://sigrid-says.com'

# Check for the most common error codes without raising for 200 or 300 codes.
# 300 codes are not expected from the Sigrid API.
def check_error_code(response: Response, data_expected=False):
    if response.status_code == 401 or response.status_code == 403:
        raise RuntimeError(f'Authorization error {response.status_code} - check your Sigrid CI token and customer/system parameters.')
    if response.status_code == 404:
        raise RuntimeError(f'Sigrid returned 404')
    if response.status_code >= 400:
        raise RuntimeError(f'Sigrid returned {response.status_code}. Text:\n {response.text}')
    if response.status_code >= 300:
        print(f'Sigrid returned unexpected code {response.status_code}. Text:\n {response.text}')
    if response.status_code == 204 and data_expected:
        raise RuntimeError(f'Sigrid returned 204 - double-check your customer/system parameters.')


class SigridCommand(ABC):

    def __init__(self, customer: str, token, system: Optional[str] = None, content_type='application/json',
                 base_url: Optional[str] = None):
        self.customer: str = customer
        self.system: Optional[str] = system
        self.token: str = token
        self.content_type: str = content_type
        self.base_url: str = (base_url or DEFAULT_SIGRID_URL).rstrip('/')

    @abc.abstractmethod
    def get_url(self) -> str:
        pass

    @abc.abstractmethod
    def do_request(self) -> Optional[Response]:
        pass

    def parse_customer_system(self):
        if self.customer is None or self.customer == '':
            raise ValueError('Customer not provided')

        system = '/' + self.system if self.system is not None and self.system != '' else ''

        return self.customer, system

    def get_headers(self):
        return {"Authorization": "Bearer " + self.token, "Content-Type": self.content_type}

