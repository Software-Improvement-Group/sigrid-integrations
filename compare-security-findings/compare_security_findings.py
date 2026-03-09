#!/usr/bin/env python3

# Copyright Software Improvement Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import sys
import urllib.request
import urllib.error
import argparse
from typing import Dict, List, Any, Optional
import pandas as pd
import logging


API_BASE_URL = "https://sigrid-says.com/rest/analysis-results/api/v1/security-findings"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_api_data(customer: str, token: str, system: str) -> Any:
    url = f"{API_BASE_URL}/{customer}/{system}"
    headers = {'Authorization': f'Bearer {token}'}

    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            logger.error("Access forbidden. Please check your API token and permissions.")
            raise RuntimeError("Access forbidden. Please check your API token and permissions.") from e
        elif e.code == 404:
            logger.error("Resource not found. Please check the customer name and system namesprovided.")
            raise RuntimeError("Resource not found. Please check the customer name and system names provided.") from e
        else:
            logger.error(f"HTTP error occurred: {e.code} {e.reason}")
            raise RuntimeError(f"HTTP error occurred: {e.code} {e.reason}") from e
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to the API: {e.reason}")
        raise RuntimeError(f"Failed to connect to the API: {e.reason}") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise RuntimeError(f"An unexpected error occurred: {e}") from e


def parse_json_data(json_data: Any) -> List[Dict]:
    if isinstance(json_data, str):
        try:
            parsed = json.loads(json_data)
            if isinstance(parsed, list):
                return parsed
            logger.error("API response is not a list of findings.")
            raise ValueError("Expected a list of findings from API.")
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON string.")
            raise ValueError("Received data is a string but not valid JSON.")
    return json_data


def create_exact_finding_key(finding: Dict) -> str:
    """Create a unique key for exact matching based on all properties including line numbers."""
    return f"{finding.get('filePath', '')}|{finding.get('startLine', '')}|{finding.get('endLine', '')}|{finding.get('type', '')}|{finding.get('ruleId', '')}"


def create_fuzzy_finding_key(finding: Dict) -> str:
    """Create a fuzzy key for matching findings in the same file with same type/CWE, ignoring line numbers."""
    return f"{finding.get('filePath', '')}|{finding.get('type', '')}|{finding.get('cweId', '')}|{finding.get('ruleId', '')}"


def find_fuzzy_match(new_finding: Dict, candidate_findings: List[Dict], line_tolerance: int = 10) -> Optional[Dict]:
    """Find a potential matching finding in candidates that is similar but at different line numbers."""
    new_start = new_finding.get('startLine', 0)
    
    for candidate in candidate_findings:
        candidate_start = candidate.get('startLine', 0)
        line_diff = abs(new_start - candidate_start)
        
        if line_diff <= line_tolerance:
            logger.debug(f"Fuzzy match found: line difference of {line_diff}")
            return candidate
    
    return None


def compare_findings(main_findings: List[Dict], new_findings: List[Dict], line_tolerance: int) -> List[Dict]:
    """Find findings in new_findings that are not in main_findings."""
    main_exact_keys = {create_exact_finding_key(f) for f in main_findings}
    logger.debug(f"Main system exact keys: {main_exact_keys}")
    
    # Pre-group main findings by their fuzzy key for O(1) lookup instead of O(m) iteration
    main_findings_by_fuzzy_key: Dict[str, List[Dict]] = {}
    for main_finding in main_findings:
        fuzzy_key = create_fuzzy_finding_key(main_finding)
        main_findings_by_fuzzy_key.setdefault(fuzzy_key, []).append(main_finding)
    
    new_only_findings = []
    for finding in new_findings:
        exact_key = create_exact_finding_key(finding)
        
        if exact_key not in main_exact_keys:
            # No exact match, check for fuzzy match using pre-grouped candidates
            fuzzy_key = create_fuzzy_finding_key(finding)
            candidate_main_findings = main_findings_by_fuzzy_key.get(fuzzy_key, [])
            fuzzy_match = find_fuzzy_match(finding, candidate_main_findings, line_tolerance)
            
            if fuzzy_match:
                # Add fuzzy match information to the finding
                finding['_fuzzy_match'] = {
                    'href': fuzzy_match.get('href', ''),
                    'startLine': fuzzy_match.get('startLine', ''),
                    'endLine': fuzzy_match.get('endLine', ''),
                    'status': fuzzy_match.get('status', '')
                }
                logger.debug(f"New finding with fuzzy match: {finding}")
            else:
                logger.debug(f"New finding detected (no fuzzy match): {finding}")
            
            new_only_findings.append(finding)
    
    logger.debug(f"Found {len(new_only_findings)} new findings not present in main system")
    return new_only_findings


def group_findings_by_status(findings: List[Dict]) -> Dict[str, List[Dict]]:
    """Group findings by their status."""
    status_groups = {
        'FIXED': [],
        'FALSE_POSITIVE_RISK_ACCEPTED': [],
        'RAW_REFINED': []
    }
    
    for finding in findings:
        status = finding.get('status', 'RAW')
        if status == 'FIXED':
            status_groups['FIXED'].append(finding)
        elif status in ['FALSE_POSITIVE', 'RISK_ACCEPTED']:
            status_groups['FALSE_POSITIVE_RISK_ACCEPTED'].append(finding)
        else:  # RAW, REFINED, WILL FIX or any other status
            status_groups['RAW_REFINED'].append(finding)
    
    logger.debug(f"Grouped findings - Fixed: {len(status_groups['FIXED'])}, "
                f"False Positive/Risk Accepted: {len(status_groups['FALSE_POSITIVE_RISK_ACCEPTED'])}, "
                f"Raw/Refined: {len(status_groups['RAW_REFINED'])}")
    
    return status_groups


def flatten_finding(finding: Dict) -> Dict:
    """Flatten a finding for Excel export."""
    flattened = {
        'ID': finding.get('id', ''),
        'File Path': finding.get('filePath', ''),
        'Line': f"{finding.get('startLine', '')}-{finding.get('endLine', '')}",
        'Component': finding.get('component', ''),
        'Type': finding.get('type', ''),
        'CWE ID': finding.get('cweId', ''),
        'Severity': finding.get('severity', ''),
        'Impact': finding.get('impact', ''),
        'Exploitability': finding.get('exploitability', ''),
        'Severity Score': finding.get('severityScore', ''),
        'Status': finding.get('status', ''),
        'Remark': finding.get('remark', ''),
        'Categories': ', '.join(finding.get('categories', [])),
        'First Seen': finding.get('firstSeenAnalysisDate', ''),
        'Last Seen': finding.get('lastSeenAnalysisDate', ''),
        'Sigrid URL': finding.get('href', '')
    }
    
    # Add fuzzy match information if available
    if '_fuzzy_match' in finding:
        fuzzy = finding['_fuzzy_match']
        flattened['Fuzzy Match in Main'] = 'Yes'
        flattened['Fuzzy Match URL'] = fuzzy.get('href', '')
        flattened['Fuzzy Match Lines'] = f"{fuzzy.get('startLine', '')}-{fuzzy.get('endLine', '')}"
        flattened['Fuzzy Match Status'] = fuzzy.get('status', '')
    else:
        flattened['Fuzzy Match in Main'] = 'No'
        flattened['Fuzzy Match URL'] = ''
        flattened['Fuzzy Match Lines'] = ''
        flattened['Fuzzy Match Status'] = ''
    
    return flattened


def create_empty_report(output_file: str, message: str):
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        pd.DataFrame({"Message": [message]}).to_excel(writer, sheet_name='No Data', index=False)


def create_status_sheet(writer: pd.ExcelWriter, findings: List[Dict], sheet_name: str) -> bool:
    if not findings:
        return False
    
    df = pd.DataFrame([flatten_finding(f) for f in findings])
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    logger.debug(f"Created '{sheet_name}' sheet with {len(findings)} findings")
    return True


def create_excel_report(grouped_findings: Dict[str, List[Dict]], output_file: str):
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        sheets_created = 0
        
        sheets_created += create_status_sheet(writer, grouped_findings['FIXED'], 'Fixed')
        sheets_created += create_status_sheet(writer, grouped_findings['FALSE_POSITIVE_RISK_ACCEPTED'], 
                                               'False Positive-Risk Accepted')
        sheets_created += create_status_sheet(writer, grouped_findings['RAW_REFINED'], 'Raw-Refined')
        
        if sheets_created == 0:
            logger.warning("No sheets were created. Adding a default sheet.")
            pd.DataFrame({"Message": ["No new findings to report"]}).to_excel(
                writer, sheet_name='No Data', index=False)
        else:
            logger.debug(f"Excel file created successfully with {sheets_created} sheet(s): {output_file}")


def process_api_output(main_system_data: str, new_system_data: str, output_file: str, line_tolerance: int):
    try:
        main_findings = parse_json_data(main_system_data)
        new_findings = parse_json_data(new_system_data)
        
        logger.debug(f"Main system has {len(main_findings)} findings")
        logger.debug(f"New system has {len(new_findings)} findings")
        
        new_only_findings = compare_findings(main_findings, new_findings, line_tolerance)
        
        if not new_only_findings:
            logger.warning("No new findings to report.")
            create_empty_report(output_file, "No new security findings found")
            return
        
        grouped_findings = group_findings_by_status(new_only_findings)
        create_excel_report(grouped_findings, output_file)
    
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise
    except Exception as e:
        logger.exception(f"Error processing data or writing to Excel file: {e}")
        raise RuntimeError(f"Error processing data or writing to Excel file: {e}")


def validate_output_filename(value):
    if os.path.dirname(value):
        raise argparse.ArgumentTypeError(f"The --output argument should be a file name, not a path. You provided: {value}")
    if value.endswith('.xlsx'):
        return value
    if '.' in value:
        raise argparse.ArgumentTypeError(f"The output file has an incorrect extension. Only .xlsx is supported. You provided: {value}")
    return value + '.xlsx'


def parse_arguments():
    parser = argparse.ArgumentParser(description="Compare security findings between two systems in Sigrid")
    parser.add_argument("--customer", type=str, required=True, help="Sigrid customer name.")
    parser.add_argument("--token", type=str, help="Sigrid API token. If not provided, the SIGRID_CI_TOKEN environment variable will be used.")
    parser.add_argument("--output", type=validate_output_filename,
                        help="Output Excel file name (not path). If not specified, a default name will be used.")
    parser.add_argument("--main-system", type=str, required=True, help="The main branch of the system, the name has to be exactly the same as 'System name' in Sigrid.")
    parser.add_argument("--new-system", type=str, required=True, help="The new system/branch that is about to be merged into main.")
    parser.add_argument("--line-tolerance", type=int, default=50, help="Line number tolerance for fuzzy matching findings (default: 50).")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('compare_security_findings_debug.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

    token = args.token or os.environ.get("SIGRID_CI_TOKEN")
    if not token:
        logger.error("Missing Sigrid API token in arguments and in environment variable SIGRID_CI_TOKEN")
        sys.exit(1)

    customer_name = args.customer.lower()
    main_system = args.main_system
    new_system = args.new_system
    line_tolerance = args.line_tolerance

    if args.output:
        output_file = args.output
    else:
        output_file = f'{customer_name}-{main_system}-{new_system}-security-findings.xlsx'

    try:
        logger.info(f"Fetching data for customer: {customer_name}")
        main_system_data = fetch_api_data(customer_name, token, main_system)
        new_system_data = fetch_api_data(customer_name, token, new_system)
        logger.info("Data fetched successfully. Processing output...")
        
        process_api_output(main_system_data, new_system_data, output_file, line_tolerance)
        logger.info(f"Data successfully exported to {output_file}")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()