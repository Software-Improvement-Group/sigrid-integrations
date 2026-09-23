from SigridRest.SigridGetCommand import SigridGetCommand


class SigridGetSecurityResultsCommand(SigridGetCommand):
    def __init__(self, customer, token, system, base_url=None):
        super().__init__(customer=customer, token=token, system=system, base_url=base_url)

    def get_url(self):

        customer, system = self.parse_customer_system()
        return (self.base_url + "/rest/analysis-results/api/v1/security-findings/{customer}/{system}").format(customer=customer, system=system)

