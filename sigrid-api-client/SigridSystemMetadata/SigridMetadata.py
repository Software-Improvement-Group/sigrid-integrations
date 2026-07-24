import copy
import json
from typing import List, Any, Dict, Optional
from datetime import date

from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from SigridRest.SigridGetMetadataCommand import SigridGetMetadataCommand
from Utils.DictUtils import diff_dicts
from Utils.ExcelUtils import parse_type, ExcelTypes, coerce_value


def _string_list_from_array(arr: List[str]) -> str:
    out = ['"']
    for x in arr:
        out.append(x)
        out.append(',')
    out[-1] = '"'
    return "".join(out)


class _MetadataValidatorWriter:
    """Adds openpyxl data validations to a metadata worksheet. Holds the worksheet and row
    count as state so the individual add-* helpers keep small interfaces."""

    def __init__(self, ws: Worksheet, num_systems: int):
        self.ws = ws
        self.num_systems = num_systems

    def _add(self, dv: DataValidation, field_name: str):
        index = get_column_letter(SigridMetadata.field_order.index(field_name) + 1)
        self.ws.add_data_validation(dv)
        dv.add(f'{index}2:{index}{self.num_systems}')

    def str_len(self, field_names: List[str], max_len: int):
        for name in field_names:
            dv = DataValidation(type="textLength", operator="lessThanOrEqual", formula1=max_len,
                                allow_blank=True, errorStyle='stop', showErrorMessage=True)
            self._add(dv, name)

    def choices(self, fields: Dict):
        for name, valid_values in fields.items():
            dv = DataValidation(type="list", formula1=_string_list_from_array(valid_values),
                                allow_blank=True, showDropDown=False, errorStyle='stop', showErrorMessage=True)
            self._add(dv, name)

    def whole_number(self, field_names: List[str], lower: int, upper: int):
        for name in field_names:
            dv = DataValidation(type="whole", operator="between", formula1=lower, formula2=upper,
                                allow_blank=True, errorStyle='stop', showErrorMessage=True)
            self._add(dv, name)


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

    # Fields that need type coercion when read from a spreadsheet; everything else stays a string.
    coercion_types = {inProductionSince: ExcelTypes.INT,
                      supplierNames: ExcelTypes.STRING_ARRAY,
                      teamNames: ExcelTypes.STRING_ARRAY,
                      isDevelopmentOnly: ExcelTypes.BOOL,
                      scopeFileInRepository: ExcelTypes.BOOL}

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

        # coerce the fields that are not plain strings to their expected Python types.
        # empty cells (None) are left as-is.
        for field, excel_type in SigridMetadata.coercion_types.items():
            if metadata.get(field) is not None:
                metadata[field] = coerce_value(metadata[field], excel_type)

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
            diff = copy.deepcopy(self.data)
        elif self.data is not None:
            diff = diff_dicts(self.data, current)
        return diff

    def get_array_of_fields(self) -> List[Any]:
        def parse_type_and_check(name):
            if name not in self.get_data():
                print(f'Warning: {name} not found in metadata response.')
            return parse_type(self.get_data().get(name))

        return [parse_type_and_check(name) for name in self.field_order]

    @staticmethod
    def write_metadata_header(ws: Worksheet):
        ws.append(SigridMetadata.field_order)

    def write_metadata_to_worksheet(self, ws: Worksheet):
        ws.append(self.get_array_of_fields())

    @staticmethod
    def write_data_validators(ws: Worksheet, num_systems=5000):
        writer = _MetadataValidatorWriter(ws, num_systems)
        writer.choices(SigridMetadata.valid_entries)
        writer.str_len([SigridMetadata.displayName, SigridMetadata.divisionName, SigridMetadata.externalID], 60)
        writer.str_len([SigridMetadata.remark], 300)
        writer.whole_number([SigridMetadata.inProductionSince], 1960, date.today().year)
