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
from typing import Dict, List, Any
import pandas as pd
import logging


API_BASE_URL = "https://sigrid-says.com/rest/analysis-results/api/v1/osh-findings"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_api_data(customer: str, token: str):
    url = f"{API_BASE_URL}/{customer}"
    headers = {'Authorization': f'Bearer {token}'}

    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            logger.error(f"Access forbidden. Please check your API token and permissions.")
            raise RuntimeError("Access forbidden. Please check your API token and permissions.") from e
        elif e.code == 404:
            logger.error(f"Resource not found. Please check the customer name provided.")
            raise RuntimeError("Resource not found. Please check the customer name provided.") from e
        else:
            logger.error(f"HTTP error occurred: {e.code} {e.reason}")
            raise RuntimeError(f"HTTP error occurred: {e.code} {e.reason}") from e
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to the API: {e.reason}")
        raise RuntimeError(f"Failed to connect to the API: {e.reason}") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise RuntimeError(f"An unexpected error occurred: {e}") from e


def parse_json_data(json_data: Any) -> Dict:
    if isinstance(json_data, str):
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON string.")
            raise ValueError("Received data is a string but not valid JSON.")
    return json_data


def validate_json_structure(data: Dict) -> List[Dict]:
    if 'systems' not in data:
        logger.error("No systems found in API response.")
        raise ValueError("Invalid JSON structure: 'systems' key not found.")

    systems = data['systems']
    return systems if isinstance(systems, list) else [systems]


def process_component(component: Dict, system_name: str) -> Dict:
    flat_component = {
        'systemName': system_name,
        'name': component.get('name', ''),
        'version': component.get('version', '')
    }

    licenses = component.get('licenses', [])
    if licenses:
        flat_component['licenses'] = ", ".join(l.get('license', {}).get('name', '') for l in licenses)

    flat_component['location'] = str(component.get('evidence', ''))
    for property_item in component.get('properties', []):
        flat_component[property_item.get("name", '')] = property_item.get("value", '')

    component_locations = component.get('evidence', {}).get('occurrences', [])
    if component_locations:
        flat_component['location'] = ", ".join(
            location.get('location', '') for location in component_locations)

    return flat_component


def process_all_systems(systems: List[Dict]) -> List[Dict]:
    all_components = {}
    for system in systems:
        system_name = system.get('systemName', 'Unknown System')
        logger.info(f"Processing system '{system_name}'")
        components = system.get('sbom', {}).get('components', [])

        for component in components:
            key = (component.get('name', ''), component.get('version', ''))
            if key not in all_components:
                all_components[key] = process_component(component, system_name)
                all_components[key]['systems'] = set()
            all_components[key]['systems'].add(system_name)

    for component in all_components.values():
        component['systems'] = ', '.join(sorted(component['systems']))

    return list(all_components.values())


def process_system(system: Dict) -> List[Dict]:
    system_name = system.get('systemName', 'Unknown System')
    components = system.get('sbom', {}).get('components', [])
    logger.debug(f"Processing system: {system_name}")

    return [process_component(component, system_name) for component in components]


def create_excel_sheet(writer: pd.ExcelWriter, system_name: str, components: List[Dict]):
    if components:
        df = pd.DataFrame(components)
        sheet_name = str(system_name)[:31]
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.debug(f"Created sheet for system {system_name}")
        return True
    else:
        logger.warning(f"No dependencies found for system {system_name}")
        return False


def create_single_excel_sheet(writer: pd.ExcelWriter, components: List[Dict]):
    if components:
        df = pd.DataFrame(components)
        df.to_excel(writer, sheet_name='All Components', index=False)
        logger.debug(f"Created single sheet with all components")
        return True
    else:
        logger.warning(f"No dependencies found across all systems")
        return False
    
def retrieve_mendix_versions(json_data: Any):
    for system in json_data['systems']:
        sbom = system.get('sbom', {})
        components = sbom.get('components', [])
        filtered_components = [component for component in components if component.get('name') == 'Mendix-Runtime']
        sbom['components'] = filtered_components
    return json_data


def process_api_output(json_data: Any, output_file: str, pivot: bool, mendix_versions_only: bool):
    try:
        logger.debug(f"Received data type: {type(json_data)}")
        parsed_data = parse_json_data(json_data)

        if mendix_versions_only:
            parsed_data = retrieve_mendix_versions(parsed_data)

        systems = validate_json_structure(parsed_data)

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            if pivot or mendix_versions_only:
                all_components = process_all_systems(systems)
                if create_single_excel_sheet(writer, all_components):
                    logger.info(f"Excel file created successfully with pivoted data: {output_file}")
                else:
                    logger.warning("No data available. Adding a default sheet.")
                    pd.DataFrame({"Message": ["No data available"]}).to_excel(writer, sheet_name='No Data', index=False)
            else:
                sheets_created = 0
                for system in systems:
                    components = process_system(system)
                    if create_excel_sheet(writer, system['systemName'], components):
                        sheets_created += 1

                if sheets_created == 0:
                    logger.warning("No sheets were created. Adding a default sheet.")
                    pd.DataFrame({"Message": ["No data available"]}).to_excel(writer, sheet_name='No Data', index=False)
                else:
                    logger.info(f"Excel file created successfully with multiple sheets: {output_file}")

    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise
    except Exception as e:
        logger.exception(f"Error processing data or writing to Excel file: {e}")
        raise RuntimeError(f"Error processing data or writing to Excel file: {e}")


def validate_output_filename(value):
    if os.path.dirname(value):
        raise argparse.ArgumentTypeError(f"The --output argument should be a file name, not a path. You provided: {value}")
    if not value.endswith('.xlsx'):
        raise argparse.ArgumentTypeError(f"The output file must have a .xlsx extension. You provided: {value}")
    return value


def parse_arguments():
    parser = argparse.ArgumentParser(description="Export all Portfolio dependencies to Excel")
    parser.add_argument("--customer", type=str, required=True, help="Sigrid customer name.")
    parser.add_argument("--output", type=validate_output_filename,
                        help="Output Excel file name (not path). If not specified, a default name will be used.")
    parser.add_argument("--pivot", action="store_true", help="Generate a single sheet with all dependencies "
                                                             "instead of a sheet per system")
    parser.add_argument("--mendix_versions_only", action="store_true", help="Get a full list of Mendix versions only if enabled")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    token = os.environ.get("SIGRID_CI_TOKEN")
    if not token:
        logger.error("Missing Sigrid API token in environment variable SIGRID_CI_TOKEN")
        sys.exit(1)

    customer_name = args.customer.lower()

    if args.output:
        output_file = args.output
    elif args.mendix_versions_only:
        output_file = f'{customer_name}-mendix-versions.xlsx'
    else:
        output_file = f'{customer_name}-portfolio-dependencies.xlsx'

    try:
        logger.info(f"Fetching data for customer: {customer_name}")
        json_data = fetch_api_data(customer_name, token)
        logger.info(f"Data fetched successfully. Processing output...")
        process_api_output(json_data, output_file, args.pivot, args.mendix_versions_only)
        logger.info(f"Data successfully exported to {output_file}")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()