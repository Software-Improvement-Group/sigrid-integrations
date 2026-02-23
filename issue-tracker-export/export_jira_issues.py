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
import urllib.parse
import urllib.request
from argparse import ArgumentParser
from base64 import urlsafe_b64encode
from datetime import datetime
from typing import Iterator

from issue_data_model import IssueTrackerData, WorkItem, WorkItemType
from issue_utils import parseDate, serialize


def fetchIssues(baseURL: str, projects: list[str]) -> Iterator[tuple[str, WorkItem]]:
    for project in projects:
        next = ""
        identity = urlsafe_b64encode(f"{os.environ['JIRA_API_USER']}:{os.environ['JIRA_API_TOKEN']}".encode("utf8"))

        while True:
            url = f"{baseURL}/rest/api/3/search/jql?jql=project%3D{project}&fields=*all&nextPageToken={next}"
            request = urllib.request.Request(url)
            request.add_header("Authorization", f"Basic {identity.decode('utf8')}")
            with urllib.request.urlopen(request) as response:
                body = json.loads(response.read().decode("utf8"))
                yield from [parseIssue(baseURL, issue) for issue in body["issues"]]
                if not body.get("nextPageToken"):
                    break
                next = body["nextPageToken"]


def parseIssue(baseURL: str, issue: dict) -> tuple[str, WorkItem]:
    issueType = issue["fields"]["issuetype"]["name"]

    parsed = WorkItem(
        id=issue["key"],
        type=mapIssueType(issueType),
        parentId=issue["parent"]["key"] if issue.get("parent") else None,
        url=f"{baseURL}/browser/{issue['key']}",
        project=issue["fields"]["project"]["name"],
        title=issue["fields"]["summary"],
        descriptionLength=len(issue["fields"]["description"] or ""),
        created=parseDate(issue["fields"]["created"]),
        closed=parseDate(issue["fields"]["resolutiondate"]),
        author=issue["fields"]["creator"]["displayName"],
        assignees=[issue["fields"]["assignee"]["displayName"]] if issue["fields"]["assignee"] else [],
        labels=issue["fields"]["labels"]
    )

    return issueType, parsed


def mapIssueType(issueType: str) -> WorkItemType:
    if "epic" in issueType.lower():
        return WorkItemType.EPIC
    elif "story" in issueType.lower() or "feature" in issueType.lower():
        return WorkItemType.FEATURE
    else:
        return WorkItemType.ISSUE


if __name__ == "__main__":
    parser = ArgumentParser(description="Exports JIRA issues into a format that can be analyzed by Sigrid.")
    parser.add_argument("--jira-base-url", type=str, required=True, help="JIRA base URL.")
    parser.add_argument("--project", type=str, required=True, help="Comma-separated list of JIRA project keys.")
    parser.add_argument("--out", type=str, default=".sigrid/jira-issues.json", help="Output file.")
    parser.add_argument("--anonymize", action="store_true", help="Anonymize author names.")
    parser.add_argument("--epic-type", type=str, default="Epic", help="The issue type you use for epics.")
    args = parser.parse_args()

    if "JIRA_API_USER" not in os.environ or "JIRA_API_TOKEN" not in os.environ:
        print("Missing environment variable JIRA_API_USER or JIRA_API_TOKEN")
        sys.exit(1)

    items = list(fetchIssues(args.jira_base_url, args.project.split(",")))
    epics = [item for type, item in items if type == args.epic_type]
    issues = [item for type, item in items if type != args.epic_type]
    data = IssueTrackerData("JIRA", datetime.now(), issues + epics, [])

    outputFile = os.path.expanduser(args.out)
    serialize(data, outputFile, args.anonymize)
    print(f"Exported {len(data.workItems)} work items to {outputFile}")
