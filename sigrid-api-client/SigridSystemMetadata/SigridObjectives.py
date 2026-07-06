import json
from json import JSONDecodeError


class SigridObjectives:

    field_order = ['ARCHITECTURE_QUALITY', 'RELIABILITY_MAX_SEVERITY', 'MAINTAINABILITY', 'TEST_CODE_RATIO',
                        'OSH_MAX_SEVERITY', 'SECURITY_MAX_SEVERITY', 'CLOUD_READINESS_MAX_SEVERITY',
                        'OSH_MAX_FRESHNESS_RISK', 'OSH_MAX_LICENSE_RISK']

    def __init__(self, system, data=None):
        self.system = system
        self.data = data

    def __str__(self):
        return f'{self.data}'

    def system_name(self):
        return self.system

    def parse_json(self, json_str):
        try:
            self.data = json.loads(json_str)
        except JSONDecodeError:
            #no data!
            self.data = dict()


    def output_json(self):
        if self.data is not None:
            return json.dumps(self.data)
        else:
            raise ValueError("no data loaded")

    def pull_data(self):
        cmd = SigridGetObjectivesCommand(self.system.customer, self.system.token, system=self.system.name,
                                         base_url=self.system.base_url)
        self.parse_json(cmd.do_request())

from SigridRest.SigridGetObjectivesCommand import SigridGetObjectivesCommand
