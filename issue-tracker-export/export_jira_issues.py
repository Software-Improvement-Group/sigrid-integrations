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

import dateutil.parser
import itertools
import json
import os
import sys
import urllib.parse
import urllib.request
from argparse import ArgumentParser

from issue_data import Issue
from issue_data_serializer import IssueDataSerializer


def fetchIssues(baseURL, projects):
    start = 0

    while True:
        request = urllib.request.Request(f"{baseURL}/rest/api/2/search?jql=ORDER%20BY%20Created&start={start}")
        request.add_header("Authorization", f"Bearer {os.environ['JIRA_API_TOKEN']}")
        with urllib.request.urlopen(request) as response:
            body = json.loads(response.read().decode("utf8"))
            yield from [parseIssue(issue) for issue in body["issues"]]
            if body["startAt"] + body["maxResults"] >= body["total"]:
                break
            start += body["maxResults"]


def parseDate(value):
    if value in (None, "", "None"):
        return None
    return dateutil.parser.isoparse(value)


def parseIssue(issue):
    return Issue(
        id=issue["key"],
        project=issue["fields"]["project"]["name"],
        title=issue["fields"]["summary"],
        status=issue["fields"]["status"]["name"],
        created=parseDate(issue["fields"]["created"]),
        closed=parseDate(issue["fields"]["resolutiondate"]),
        author=issue["fields"]["creator"]["displayName"],
        assignee=issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else None,
        epic=None,
        labels=issue["fields"]["labels"]
    )


if __name__ == "__main__":
    parser = ArgumentParser(description="Exports JIRA issues into a format that can be analyzed by Sigrid.")
    parser.add_argument("--jira-base-url", type=str, required=True, help="JIRA base URL.")
    parser.add_argument("--project", type=str, default="", help="Comma-separated list of JIRA project keys.")
    parser.add_argument("--out", type=str, default=".sigrid", help="Output directory.")
    args = parser.parse_args()

    if not "JIRA_API_TOKEN" in os.environ:
        print("Missing environment variable JIRA_API_TOKEN")
        sys.exit(1)

    issues = list(fetchIssues(args.jira_base_url, args.project.split(",")))
    outputDir = os.path.expanduser(args.out)
    IssueDataSerializer.serialize("JIRA", issues, outputDir)
    print(f"Exported {len(issues)} issues to {outputDir}")
