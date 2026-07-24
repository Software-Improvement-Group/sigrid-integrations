from SigridRest.SigridGetCommand import SigridGetCommand


class SigridGetArchitectureJSONCommand(SigridGetCommand):
    def get_url(self):
        endpoint = f'{self.base_url}/rest/analysis-results/api/v1/architecture-quality/'
        customer, system = self.parse_customer_system()
        if system == '':
            raise ValueError('need a system for this command')
        return '{base_url}{customer}{system}/raw'.format(base_url=endpoint, customer=customer, system=system)


    def __init__(self, customer, token, system=None, base_url=None):
        super().__init__(customer=customer, token=token, system=system, base_url=base_url)

