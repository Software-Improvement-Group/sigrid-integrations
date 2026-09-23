from SigridRest.SigridPatchCommand import SigridPatchCommand

class SigridPatchMetadataCommand(SigridPatchCommand):
    def get_url(self):
        endpoint = f'{self.base_url}/rest/analysis-results/api/v1/system-metadata/'
        customer, system = self.parse_customer_system()
        return '{base_url}{customer}{system}'.format(base_url=endpoint, customer=customer, system=system)

    def __init__(self, customer, token, payload, system=None, base_url=None):
        super().__init__(customer=customer, token=token, system=system, payload=payload, base_url=base_url)
