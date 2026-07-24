import json
from json import JSONDecodeError
from typing import List, Any

from openpyxl.worksheet.worksheet import Worksheet

from SigridRest.SigridGetSecurityResultsCommand import SigridGetSecurityResultsCommand
from Utils.ExcelUtils import parse_type


class SigridSecurityResults:
    id = "id"
    href = "href"
    firstSeenAnalysisDate = "firstSeenAnalysisDate"
    lastSeenAnalysisDate = "lastSeenAnalysisDate"
    firstSeenSnapshotDate = "firstSeenSnapshotDate"
    lastSeenSnapshotDate = "lastSeenSnapshotDate"
    filePath = "filePath"
    startLine = "startLine"
    endLine = "endLine"
    component = "component"
    type = "type"
    severity = "severity"
    impact = "impact"
    exploitability = "exploitability"
    severityScore = "severityScore"
    impactScore = "impactScore"
    exploitabilityScore = "exploitabilityScore"
    status = "status"
    remark = "remark"
    toolName = "toolName"
    isManualFinding = "isManualFinding"
    isSeverityOverridden = "isSeverityOverridden"
    weaknessIds = "weaknessIds"

    field_order = [id, href, firstSeenAnalysisDate, lastSeenAnalysisDate, firstSeenSnapshotDate, lastSeenSnapshotDate,
                   filePath, startLine, endLine, component, type, severity, impact, exploitability, severityScore,
                   impactScore, exploitabilityScore, status, remark, toolName, isManualFinding, isSeverityOverridden,
                   weaknessIds]

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
            self.data = []


    def output_json(self):
        if self.data is not None:
            return json.dumps(self.data)
        else:
            raise ValueError("no data loaded")

    def pull_data(self):
        cmd = SigridGetSecurityResultsCommand(self.system.customer, self.system.token, system=self.system.name,
                                              base_url=self.system.base_url)
        self.parse_json(cmd.do_request())

    def get_data(self):
        if self.data is None:
            self.pull_data()
        return self.data

    def get_array_of_fields(self) -> List[Any]:
        return [[parse_type(finding[name]) for name in self.field_order] for finding in self.get_data()]

    @staticmethod
    def write_header(ws: Worksheet):
        ws.append(SigridSecurityResults.field_order + ['systemName'])

    def write_metadata_to_worksheet(self, ws: Worksheet):
        for row in self.get_array_of_fields():
            ws.append(row + [self.system.name])
