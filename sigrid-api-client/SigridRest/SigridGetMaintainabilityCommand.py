from SigridRest.SigridGetCommand import SigridGetCommand


class SigridGetMaintainabilityCommand(SigridGetCommand):
    def __init__(self, customer, token, system=None, component_level=False, base_url=None):
        super().__init__(customer=customer, token=token, system=system, base_url=base_url)
        self.component_level = component_level

    def get_url(self):

        customer, system = self.parse_customer_system()

        component_level = '' if system == '' or not self.component_level else '/components'

        return (self.base_url + "/rest/analysis-results/api/v1/maintainability/{customer}{system}{"
                "component_level}").format(customer=customer, system=system, component_level=component_level)

