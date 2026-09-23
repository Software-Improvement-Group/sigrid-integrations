from json import JSONDecodeError

from SigridRest.SigridPatchMetadataCommand import SigridPatchMetadataCommand
from SigridSystemMetadata.SigridMaintainability import SigridMaintainability
from SigridSystemMetadata.SigridMetadata import SigridMetadata
from SigridSystemMetadata.SigridObjectives import SigridObjectives
from SigridSystemMetadata.SigridSecurityResults import SigridSecurityResults


class SigridSystem:

    def __init__(self, customer: str, system_name: str, token: str, metadata: dict = None, maintainability: dict = None,
                 objectives: dict = None, security_results: dict = None, base_url=None):
        # note that components can handle None as data input using the setters
        self.name: str = system_name
        self.customer: str = customer
        self.token: str = token
        self.base_url: str = base_url
        self.metadata: SigridMetadata = SigridMetadata(self, metadata)
        self.maintainability: SigridMaintainability = SigridMaintainability(self, maintainability)
        self.objectives: SigridObjectives = SigridObjectives(self, objectives)
        self.security_results: SigridSecurityResults = SigridSecurityResults(self, security_results)

    def __str__(self):
        return f'Customer: {self.customer}, System: {self.name}'

    @classmethod
    def from_metadata(cls, metadata: dict, token: str, base_url=None):
        return SigridSystem(metadata['customerName'],
                            metadata['systemName'],
                            token,
                            metadata,
                            base_url=base_url)

    def get_name(self):
        return self.name

    def get_metadata(self) -> SigridMetadata:
        return self.metadata

    def set_metadata(self, metadata: dict):
        self.metadata = SigridMetadata(self, metadata)

    def get_maintainability(self):
        if self.maintainability.data is None:
            self.maintainability.pull_data()
        return self.maintainability

    def get_objectives(self):
        if self.objectives.data is None:
            self.objectives.pull_data()
        return self.objectives

    def get_security_results(self) -> SigridSecurityResults:
        if self.security_results.data is None:
            self.security_results.pull_data()
        return self.security_results

    def patch_metadata(self, dry_run: bool = False, current = None):
        try:
            diff_dict = self.get_metadata().diff_data(current=current)
        except JSONDecodeError as e:
            print (f'failed to parse {self.get_name()}, and error {e}')
            return
        #these labels are fixed and probably best not to send in the patch
        remove_labels = ['customerName', 'systemName', 'scopeFileInRepository',
                         'technologyCategory', 'externalID']
        for label in remove_labels:
            if label in diff_dict:
                diff_dict.pop(label)

        patchcmd = SigridPatchMetadataCommand(customer=self.customer, token=self.token, system=self.get_name(),
                                              payload=diff_dict, base_url=self.base_url)
        return patchcmd.do_request(dry_run)
