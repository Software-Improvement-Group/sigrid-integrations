from SigridRest.SigridGetCommand import SigridGetCommand


class SigridGetObjectivesCommand(SigridGetCommand):
    def __init__(self, customer, token, system, base_url=None):
        super().__init__(customer=customer, token=token, system=system, base_url=base_url)

    def get_url(self):

        customer, system = self.parse_customer_system()
        return (self.base_url + "/rest/analysis-results/api/v1/objectives/{customer}/{system}/config").format(customer=self.customer, system=system)

