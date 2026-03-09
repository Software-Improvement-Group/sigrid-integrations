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
import yaml
import os
import sys
import urllib.error
import urllib.request
from argparse import ArgumentParser, SUPPRESS


"""
Removes redundant files that are present in the default generated scopefile but either are redundant or 
negatively impact Sigrid usage in the long term
"""
def remove_redundant_fields(scope_file):
    redundant_fields = ['alerts',
                        'repository',
                        'model',
                        'project_code',
                        'system',
                        'customer',
                        'partner']

    scope_values = yaml.safe_load(scope_file)

    for field in redundant_fields:
        if field in scope_values:
             del scope_values[field]

    # These values are redundant in most cases but would be required in the scope file if they are set to false
    if 'architecture' in scope_values and scope_values['architecture']['enabled']:
            del scope_values['architecture']
    if 'default_excludes' in scope_values and scope_values['default_excludes']:
        del scope_values['default_excludes']

    scope_file = yaml.dump(scope_values)
    return scope_file

"""
Checks if there is a client scope file defined for the system and if there isn't, removes the default fields that are redundant
It assumes that redundant fields a client has uploaded could be part of a logic so currently it doesn't override those
"""
def clean_up_default_scopefile(scope_file, args):
    url = f"{args.sigridurl}/rest/analysis-results/api/v1/system-metadata/{args.customer}/{args.system}"
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/json")
    request.add_header("Authorization", f"Bearer {os.environ['SIGRID_CI_TOKEN']}".encode("utf8"))

    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 204:
                print(f"Sigrid cannot find metadata for this system (HTTP status {response.status})")
                sys.exit(1)

            metadata = json.load(response)
            if not metadata['scopeFileInRepository']:
                scope_file = remove_redundant_fields(scope_file)
    except urllib.error.HTTPError as e:
        print(f"Failed to retrieve metadata from Sigrid (HTTP status {e.code})")
        sys.exit(1)
    return scope_file


if __name__ == "__main__":
    parser = ArgumentParser(description="Retrieves and dumps the Sigrid scope configuration file for a system.")
    parser.add_argument("--customer", type=str, help="Sigrid customer name.")
    parser.add_argument("--system", type=str, help="Sigrid system name.")
    parser.add_argument("--sigridurl", type=str, default="https://sigrid-says.com", help=SUPPRESS)
    args = parser.parse_args()

    if None in [args.customer, args.system]:
        parser.print_help()
        sys.exit(1)

    if not os.environ.get("SIGRID_CI_TOKEN"):
        print("Missing Sigrid API token in environment variable SIGRID_CI_TOKEN")
        sys.exit(1)

    url = f"{args.sigridurl}/rest/analysis-results/api/v1/architecture-quality/{args.customer}/{args.system}/raw"
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/json")
    request.add_header("Authorization", f"Bearer {os.environ['SIGRID_CI_TOKEN']}".encode("utf8"))

    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 204:
                print(f"Sigrid cannot find analysis results for this system (HTTP status {response.status})")
                sys.exit(1)

            results = json.load(response)
            scope_file = results["metadata"]["scopeFile"]
            print(clean_up_default_scopefile(scope_file, args))
    except urllib.error.HTTPError as e:
        print(f"Failed to retrieve analysis results from Sigrid (HTTP status {e.code})")
        sys.exit(1)
