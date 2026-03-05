#!/bin/bash

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

usage() {
    echo "Usage: $0 <working directory> <command>"
    echo
    echo "Make sure SIGRID_CI_TOKEN contains a valid token."
    echo
    echo "Use one of the following commands:"
    for cmd in "${COMMANDS[@]}"; do
        echo "  $cmd"
    done
    exit 1
}

COMMANDS=("report-generator" "objectives_report.py" "get_scope_file.py" "export_portfolio_dependencies.py", "polarion-integration.py", "export_github_issues.py", "export_gitlab_issues.py", "osh-findings.py")

if [ $# -lt 2 ] || [ -z $SIGRID_CI_TOKEN ]; then
    usage
fi

WORKING_DIR=$1
COMMAND=$2
shift

MATCH_FOUND=false
for cmd in "${COMMANDS[@]}"; do
    if [ "$cmd" == "$COMMAND" ]; then
        MATCH_FOUND=true
        break
    fi
done

if [ "$MATCH_FOUND" = false ]; then
    echo "Error: Invalid command '$COMMAND'"
    echo
    usage
fi

docker run -it --rm \
    -e SIGRID_CI_TOKEN="$SIGRID_CI_TOKEN" \
    -v "$WORKING_DIR":/home/sigrid \
    --entrypoint "" \
    softwareimprovementgroup/sigrid-integrations "$@"
