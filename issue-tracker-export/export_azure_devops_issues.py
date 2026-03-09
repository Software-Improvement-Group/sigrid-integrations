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
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from argparse import ArgumentParser
from base64 import b64encode
from datetime import datetime
from typing import Iterator

from issue_data_model import IssueTrackerData, PullRequest, WorkItem, WorkItemType
from issue_utils import filterIssueData, parseDate, serialize

AUTH_HEADER = b64encode(f":{os.environ.get('AZURE_DEVOPS_PAT', '')}".encode("utf8")).decode("utf8")


def sendRequest(url: str, body: dict = None) -> dict:
    try:
        data = json.dumps(body).encode("utf8") if body else None
        request = urllib.request.Request(url, data=data)
        request.add_header("Authorization", f"Basic {AUTH_HEADER}")
        if body:
            request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf8"))
    except urllib.error.HTTPError as e:
        print(f"Warning: Cannot access {url}, HTTP status {e.code}")
        return None


def fetchWorkItemIds(baseURL: str, org: str, project: str, wiql: str, pageSize: int) -> list[int]:
    url = f"{baseURL}/{urllib.parse.quote(org)}/{urllib.parse.quote(project)}/_apis/wit/wiql?$top={pageSize}&api-version=7.1"
    result = sendRequest(url, {"query": wiql})
    return [item["id"] for item in (result or {}).get("workItems", [])]


def fetchWorkItemDetails(baseURL: str, org: str, project: str, ids: list[int]) -> Iterator[dict]:
    for i in range(0, len(ids), 200):
        chunk = ids[i:i + 200]
        idList = ",".join(str(id) for id in chunk)
        batchURL = (
            f"{baseURL}/{urllib.parse.quote(org)}/{urllib.parse.quote(project)}"
            f"/_apis/wit/workitems?ids={idList}"
            f"&$expand=all&errorPolicy=omit&api-version=7.1"
        )
        result = sendRequest(batchURL)
        for workItem in (result or {}).get("value", []):
            if workItem is not None:
                yield workItem


def fetchWorkItems(baseURL: str, org: str, projects: list[str], start: str) -> Iterator[dict]:
    pageSize = 200
    for project in projects:
        lastId = 0
        while True:
            wiql = (
                f"SELECT [System.Id] FROM WorkItems "
                f"WHERE [System.TeamProject] = '{project}' "
                f"AND [System.CreatedDate] >= '{start}' "
                f"AND [System.Id] > {lastId} "
                f"ORDER BY [System.Id] ASC"
            )
            ids = fetchWorkItemIds(baseURL, org, project, wiql, pageSize)
            if not ids:
                break
            yield from fetchWorkItemDetails(baseURL, org, project, ids)
            if len(ids) < pageSize:
                break
            lastId = ids[-1]


def fetchPullRequests(baseURL: str, org: str, projects: list[str], start: str) -> Iterator[PullRequest]:
    for project in projects:
        skip = 0
        while True:
            url = (
                f"{baseURL}/{urllib.parse.quote(org)}/{urllib.parse.quote(project)}"
                f"/_apis/git/pullrequests?searchCriteria.status=all"
                f"&searchCriteria.minTime={start}T00:00:00Z"
                f"&searchCriteria.queryTimeRangeType=created"
                f"&$top=100&$skip={skip}&api-version=7.1"
            )
            result = sendRequest(url)
            prs = (result or {}).get("value", [])
            for pr in prs:
                yield parsePullRequest(baseURL, org, project, pr)
            if len(prs) < 100:
                break
            skip += 100


def getParentId(workItem: dict) -> int | None:
    for relation in (workItem.get("relations") or []):
        if relation.get("rel") == "System.LinkTypes.Hierarchy-Reverse":
            match = re.search(r"/workItems/(\d+)$", relation.get("url", ""))
            if match:
                return int(match.group(1))
    return None


def getDisplayName(field) -> str | None:
    if field is None:
        return None
    if isinstance(field, dict):
        return field.get("displayName")
    return str(field)


def parseTags(fields: dict) -> list[str]:
    tags = fields.get("System.Tags", "")
    return [tag.strip() for tag in tags.split(";") if tag.strip()] if tags else []


def mapWorkItemType(typeName: str, epicType: str) -> WorkItemType:
    if typeName.lower() == epicType.lower():
        return WorkItemType.EPIC
    elif typeName.lower() in ("feature", "story"):
        return WorkItemType.FEATURE
    elif typeName.lower() in ("pbi", "product backlog item"):
        return WorkItemType.ISSUE
    else:
        return None 


def parseWorkItem(baseURL: str, org: str, workItem: dict, epicType: str) -> WorkItem:
    fields = workItem.get("fields", {})
    project = fields.get("System.TeamProject", "")
    typeName = fields.get("System.WorkItemType", "")
    assignedTo = getDisplayName(fields.get("System.AssignedTo"))
    parentId = getParentId(workItem)

    return WorkItem(
        id=str(workItem["id"]),
        type=mapWorkItemType(typeName, epicType),
        parentId=str(parentId) if parentId else None,
        url=f"{baseURL}/{urllib.parse.quote(org)}/{urllib.parse.quote(project)}/_workitems/edit/{workItem['id']}",
        project=project,
        title=fields.get("System.Title", ""),
        descriptionLength=len(fields.get("System.Description") or ""),
        created=parseDate(fields.get("System.CreatedDate")),
        closed=parseDate(fields.get("Microsoft.VSTS.Common.ClosedDate")),
        author=getDisplayName(fields.get("System.CreatedBy")),
        assignees=[assignedTo] if assignedTo else [],
        labels=parseTags(fields)
    )


def parsePullRequest(baseURL: str, org: str, project: str, pr: dict) -> PullRequest:
    repo = pr.get("repository", {})
    repoName = repo.get("name", "")

    return PullRequest(
        id=str(pr["pullRequestId"]),
        url=f"{baseURL}/{urllib.parse.quote(org)}/{urllib.parse.quote(project)}/_git/{urllib.parse.quote(repoName)}/pullrequest/{pr['pullRequestId']}",
        project=project,
        title=pr.get("title", ""),
        created=parseDate(pr.get("creationDate")),
        closed=parseDate(pr.get("closedDate")),
        assignees=[],
        reviewers=[r["displayName"] for r in pr.get("reviewers", []) if r.get("displayName")]
    )


def exportAzureDevOpsData(baseURL: str, org: str, projects: list[str], start: str, epicType: str) -> IssueTrackerData:
    rawWorkItems = list(fetchWorkItems(baseURL, org, projects, start))
    workItems = [
        parsed for parsed in (parseWorkItem(baseURL, org, wi, epicType) for wi in rawWorkItems)
        if parsed.type is not None
    ]
    pullRequests = list(fetchPullRequests(baseURL, org, projects, start))
    return IssueTrackerData("Azure DevOps", datetime.now(), workItems, pullRequests)


if __name__ == "__main__":
    parser = ArgumentParser(description="Exports Azure DevOps work items into a format that can be analyzed by Sigrid.")
    parser.add_argument("--ado-api-url", type=str, default="https://dev.azure.com",
                        help="Azure DevOps base URL (default: https://dev.azure.com).")
    parser.add_argument("--org", type=str, required=True, help="Azure DevOps organization name.")
    parser.add_argument("--project", type=str, required=True,
                        help="Comma-separated list of Azure DevOps project names.")
    parser.add_argument("--exclude-labels", type=str, default="",
                        help="Comma-separated tags to be excluded.")
    parser.add_argument("--out", type=str, default=".sigrid/azure-devops-issues.json", help="Output file.")
    parser.add_argument("--start", type=str, default="1970-01-01",
                        help="Export work items created after (yyyy-mm-dd).")
    parser.add_argument("--anonymize", action="store_true", help="Anonymize author names.")
    parser.add_argument("--epic-type", type=str, default="Epic",
                        help="The work item type used for epics (default: Epic).")
    args = parser.parse_args()

    if "AZURE_DEVOPS_PAT" not in os.environ:
        print("Missing environment variable AZURE_DEVOPS_PAT")
        sys.exit(1)

    projects = [p.strip() for p in args.project.split(",") if p.strip()]
    excludeLabels = args.exclude_labels.split(",") if args.exclude_labels else []

    data = exportAzureDevOpsData(args.ado_api_url, args.org, projects, args.start, args.epic_type)
    filterIssueData(data, excludeLabels)
    outputFile = os.path.expanduser(args.out)
    serialize(data, outputFile, args.anonymize)
    print(f"Exported {len(data.workItems)} work items and {len(data.pullRequests)} pull requests to {outputFile}")
