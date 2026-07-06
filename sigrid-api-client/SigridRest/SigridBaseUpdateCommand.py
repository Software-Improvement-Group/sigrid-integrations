import abc
import json
from abc import ABC
from functools import singledispatchmethod
from typing import Union, Optional

from SigridRest.SigridCommand import SigridCommand


class SigridBaseUpdateCommand(SigridCommand, ABC):

    @abc.abstractmethod
    def __init__(self, customer: str, token: str, payload: Union[dict, str], system=None,
                 base_url=None):
        super().__init__(customer, token, system, base_url=base_url)
        self.payload: Optional[str] = None
        self.set_payload(payload)

    @singledispatchmethod
    def set_payload(self, payload):
        raise TypeError("expected str or dict, got " + str(type(payload)))

    @set_payload.register
    def _set_payload_None(self, payload: type(None)):
        raise TypeError("None is not accepted here")

    @set_payload.register
    def _set_payload_dict(self, payload: dict):
        self.payload = json.dumps(payload)

    @set_payload.register
    def _set_payload_str(self, payload: str):
        self.payload = payload

    def get_payload(self) -> str:
        return self.payload


