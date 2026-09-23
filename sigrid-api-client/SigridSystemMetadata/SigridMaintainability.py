import json

from SigridRest.SigridGetMaintainabilityCommand import SigridGetMaintainabilityCommand


class SigridMaintainability:
    field_order = ['system', 'customer', 'allRatings', 'maintainabilityDate', 'volume', 'unitSize',
                   'unitInterfacing', 'unitComplexity', 'testCodeRatio', 'moduleCoupling',
                   'duplication', 'componentEntanglement',
                   'componentIndependence', 'componentBalance',
                   'maintainability']

    def __init__(self, system, data=None):
        self.system = system
        self.data = data

    def parse_json(self, json_str):
        self.data = json.loads(json_str)

    def output_json(self):
        if self.data is not None:
            return json.dumps(self.data)
        else:
            raise ValueError("no data loaded")

    def pull_data(self):
        cmd = SigridGetMaintainabilityCommand(self.system.customer, self.system.token, system=self.system.name,
                                              base_url=self.system.base_url)
        self.parse_json(cmd.do_request())
