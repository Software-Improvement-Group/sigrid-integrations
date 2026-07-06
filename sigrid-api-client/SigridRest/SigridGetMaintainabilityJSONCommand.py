from SigridRest.SigridGetCommand import SigridGetCommand


class SigridGetMaintainabilityJSONCommand(SigridGetCommand):
    def __init__(self, customer, token, system, snapshotDate=None, base_url=None):
        if system is None or system == '':
            raise ValueError(f'Need a system name, got {system}')
        super().__init__(customer, token, system, base_url=base_url)
        self.snapshotDate = snapshotDate

    def get_url(self):
        base_url = f'{self.base_url}/rest/analysis-results/api/v1/maintainability/'
        snapshot_date_str = "?snapshotDate={snapshotDate}".format(snapshotDate=self.snapshotDate) \
            if self.snapshotDate is not None else ''
        customer, system = self.parse_customer_system()

        return '{base_url}{customer}/{system}/raw{snapshotDate}'.format(base_url=base_url,
                                                                        customer=customer,
                                                                        system=system,
                                                                        snapshotDate=snapshot_date_str)
