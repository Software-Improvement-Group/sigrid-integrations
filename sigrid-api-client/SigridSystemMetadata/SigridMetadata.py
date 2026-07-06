import json
from typing import List, Any, Dict, Optional
from datetime import date

from openpyxl import worksheet
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from SigridRest.SigridGetMetadataCommand import SigridGetMetadataCommand
from Utils.ExcelUtils import parseType

class SigridMetadata:
    systemName = 'systemName'
    applicationType = 'applicationType'
    businessCriticality = 'businessCriticality'
    customerName = 'customerName'
    deploymentType = 'deploymentType'
    displayName = 'displayName'
    divisionName = 'divisionName'
    externalDisplayName = 'externalDisplayName'
    externalID = 'externalID'
    inProductionSince = 'inProductionSince'
    isDevelopmentOnly = 'isDevelopmentOnly'
    lifecyclePhase = 'lifecyclePhase'
    remark = 'remark'
    scopeFileInRepository = 'scopeFileInRepository'
    softwareDistributionStrategy = 'softwareDistributionStrategy'
    supplierNames = 'supplierNames'
    targetIndustry = 'targetIndustry'
    teamNames = 'teamNames'
    technologyCategory = 'technologyCategory'

    field_order = [systemName, applicationType, businessCriticality, customerName, deploymentType, displayName,
                   divisionName, externalDisplayName, externalID, inProductionSince, isDevelopmentOnly,
                   lifecyclePhase, remark, scopeFileInRepository, softwareDistributionStrategy,
                   supplierNames, targetIndustry, teamNames, technologyCategory]

    valid_entries = {applicationType: ["PROCESS_CONTROLLER", "TRANSACTION_PROCESSING", "RESOURCE_MANAGEMENT",
                                       "CASE_MANAGEMENT", "DESIGN_ENGINEERING_DEVELOPMENT", "ANALYTICAL",
                                       "AUTHENTICATION_AND_PORTALS", "COMMUNICATION", "FUNCTIONAL_APPLICATIONS",
                                       "KNOWLEDGE_AND_DOCUMENT_MANAGEMENT", "PERSONAL_PRODUCTIVITY_APPLICATIONS"],
                     deploymentType: ["PUBLIC_FACING", "CONNECTED", "INTERNAL", "PHYSICAL"],
                     targetIndustry: ["ICD0500", "ICD1750", "ICD2350", "ICD2710", "ICD2730", "ICD2750", "ICD2770",
                                      "ICD2790", "ICD2797", "ICD3350", "ICD3500", "ICD3700", "ICD4500", "ICD5300",
                                      "ICD5500", "ICD5700", "ICD6500", "ICD7500", "ICD7577", "ICD8300", "ICD8500",
                                      "ICD8630", "ICD8700", "ICD9530", "ICD9570", "SIG2200", "SIG1200", "SIG1000",
                                      "SIG1100"],
                     businessCriticality: ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                     lifecyclePhase: ["INITIAL", "EVOLUTION", "MAINTENANCE", "EOL", "DECOMMISSIONED"],
                     technologyCategory: ["AGGREGATE", "BPM", "CUSTOMIZATION", "CONFIGURATION", "DATABASE", "DSL",
                                          "EMBEDDED", "LEGACY", "LOW_CODE", "MAINFRAME", "MODERN_GENERAL_PURPOSE",
                                          "SCIENTIFIC", "SCRIPTING", "SDI", "TEMPLATING", "WEB"],
                     softwareDistributionStrategy: ["NOT_DISTRIBUTED", "NETWORK_SERVICE", "DISTRIBUTED"],
                     isDevelopmentOnly: ["FALSE", "TRUE"]}

    def __init__(self, system, data=None):
        self.system = system
        self.data: Optional[dict] = None
        self.set_data(data)

    def __str__(self):
        return f'{self.data}'

    def get_data(self) -> dict:
        if self.data is None:
            self.pull_metadata()
        return self.data

    def set_data(self, metadata):
        if metadata is None:
            self.data = None
            return

        # first strip out everything we don't recognize as a valid metadata field.
        metadata = {k: v for (k, v) in metadata.items() if k in SigridMetadata.field_order}

        def checkbool(title):
            if title in metadata:
                if isinstance(metadata[title], str):
                    metadata[title] = metadata[title].upper() == "TRUE"

        def checkint(title):
            if title in metadata:
                if not isinstance(metadata[title], int):
                    try:
                        metadata[title] = int(metadata[title])
                    except (ValueError, TypeError):
                        # in this case there was probably an empty line
                        metadata[title] = None

        def checkArr(title):
            if title in metadata:
                if isinstance(metadata[title], str):
                    if metadata[title] == '[]' or metadata[title] == '':
                        metadata[title] = []
                    else:
                        metadata[title] = [x.strip() for x in metadata[title].replace("[", '').replace("]", "")
                        .replace('\'', '').replace("\"", '').split(',')]

        supplierNames = 'supplierNames'
        inprodsince = 'inProductionSince'
        isDevOnly = 'isDevelopmentOnly'
        scopeInRepo = 'scopeFileInRepository'
        teamNames = 'teamNames'

        checkint(inprodsince)
        checkArr(supplierNames)
        checkArr(teamNames)
        checkbool(isDevOnly)
        checkbool(scopeInRepo)

        self.data = metadata

    def system_name(self):
        if self.data is not None:
            return self.data['systemName']
        else:
            return ''

    def parse_json(self, json_str):
        self.data = json.loads(json_str)

    def output_json(self):
        if self.data is not None:
            return json.dumps(self.data)
        else:
            raise ValueError("no data loaded")

    def pull_metadata(self):
        cmd = SigridGetMetadataCommand(self.system.customer, self.system.token, system=self.system.name,
                                       base_url=self.system.base_url)
        self.parse_json(cmd.do_request())
        self.data['systemName'] = self.system.name
        self.data['customerName'] = self.system.customer

    def diff_data(self, current=None):
        if current is None:
            current = json.loads(
            SigridGetMetadataCommand(self.system.customer, self.system.token, system=self.system.name,
                                     base_url=self.system.base_url).do_request())
        diff = {}
        if current is None:
            diff = self.data.copy()
        if self.data is not None:
            # find all things in new that were different in old.
            # we will *not* check the case where something from old is missing from new, we assume
            # that in this case we don't want to change it.
            for k, v in self.data.items():
                try:
                    if isinstance(v, list):
                        for entry in v:
                            if entry not in current[k]:
                                diff[k] = v
                                continue
                    if v != current[k]:
                        if v == '' and current[k] is None or v is None and current[k] == '':
                            continue
                        diff[k] = v
                except KeyError:
                    diff[k] = v
        return diff

    def get_array_of_fields(self) -> List[Any]:
        return [parseType(self.get_data()[name]) for name in self.field_order]

    @staticmethod
    def write_metadata_header(ws: worksheet):
        ws.append(SigridMetadata.field_order)

    def write_metadata_to_worksheet(self, ws: worksheet):
        ws.append(self.get_array_of_fields())

    @staticmethod
    def write_data_validators(ws: worksheet, num_systems=5000):
        def string_list_from_array(arr: List[str]) -> str:
            out = ['"']
            for x in arr:
                out.append(x)
                out.append(',')
            out[-1] = '"'
            return "".join(out)

        def write_validator(dv: DataValidation, field_name: str):
            index = get_column_letter(SigridMetadata.field_order.index(field_name) + 1)
            ws.add_data_validation(dv)
            dv.add(f'{index}2:{index}{num_systems}')

        def write_str_len_validator(field_names: List[str], max_len: int):
            for name in field_names:
                dv = DataValidation(type="textLength", operator="lessThanOrEqual", formula1=max_len,
                                    allow_blank=True, errorStyle='stop', showErrorMessage=True)
                write_validator(dv, name)

        def write_list_validator(fields: Dict):
            for name, valid_values in fields.items():
                dv = DataValidation(type="list", formula1=string_list_from_array(valid_values),
                                    allow_blank=True, showDropDown=False, errorStyle='stop', showErrorMessage=True)
                write_validator(dv, name)

        def write_number_validator(field_names: List[str], lower: int, upper: int, whole: bool = True):
            for name in field_names:
                dv = DataValidation(type="whole" if whole else "decimal", operator="between",
                                    formula1=lower, formula2=upper, allow_blank=True, errorStyle='stop',
                                    showErrorMessage=True)
                write_validator(dv, name)

        write_list_validator(SigridMetadata.valid_entries)
        write_str_len_validator([SigridMetadata.displayName, SigridMetadata.divisionName,
                                 SigridMetadata.externalID], 60)
        write_str_len_validator([SigridMetadata.remark], 300)
        write_number_validator([SigridMetadata.inProductionSince], 1960, date.today().year)
