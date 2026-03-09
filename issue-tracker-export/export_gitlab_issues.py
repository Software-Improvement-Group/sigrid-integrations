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

import itertools
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from argparse import ArgumentParser
from datetime import datetime
from typing import Iterator

from issue_data_model import IssueTrackerData, PullRequest, WorkItem, WorkItemType
from issue_utils import parseDate, serialize, filterIssueData


def sendRequest(url):
    try:
        request = urllib.request.Request(f"{url}")
        request.add_header("PRIVATE-TOKEN", os.environ["GITLAB_API_TOKEN"])
        with urllib.request.urlopen(request) as response:
            yield json.loads(response.read().decode("utf8"))
    except urllib.error.HTTPError as e:
        print(f"Warning: Cannot access {url}, HTTP status {e.code}")


def sendMultipartRequest(url: str) -> Iterator:
    for page in itertools.count(start=1):
        request = urllib.request.Request(f"{url}&page={page}&per_page=100")
        request.add_header("PRIVATE-TOKEN", os.environ["GITLAB_API_TOKEN"])
        with urllib.request.urlopen(request) as response:
            yield from json.loads(response.read().decode("utf8"))
            if not response.headers.get("X-Next-Page"):
                break


def fetchIssues(
    baseURL: str, groups: list[str], projects: list[str], start: str
) -> Iterator[WorkItem]:
    groupURLs = [
        f"{baseURL}/api/v4/groups/{urllib.parse.quote_plus(group)}/issues"
        for group in groups
    ]
    projectURLs = [
        f"{baseURL}/api/v4/projects/{urllib.parse.quote_plus(project)}/issues"
        for project in projects
    ]

    for url in groupURLs + projectURLs:
        for issue in sendMultipartRequest(
            f"{url}?scope=all&state=all&created_after={start}"
        ):
            if not issue.get("moved_to_id"):
                yield parseIssue(issue)


def parseIssue(issue: dict) -> WorkItem:
    epicId = (
        f"{issue['epic']['group_id']}::{issue['epic']['id']}::{issue['epic']['iid']}"
        if issue["epic"]
        else None
    )

    return WorkItem(
        id=issue["id"],
        type=WorkItemType.ISSUE,
        parentId=epicId,
        url=issue["web_url"],
        project=issue["references"]["full"].split("#")[0],
        title=issue["title"],
        descriptionLength=len(issue["description"] or ""),
        created=parseDate(issue["created_at"]),
        closed=parseDate(issue["closed_at"]),
        author=issue["author"]["name"],
        assignees=[assignee["name"] for assignee in issue["assignees"]],
        labels=issue["labels"],
    )


def fetchEpics(baseURL: str, issues: list[WorkItem]) -> Iterator[WorkItem]:
    epicIds = set(issue.parentId for issue in issues if issue.parentId)

    for epicId in epicIds:
        groupId, id, iid = epicId.split("::")

        for epic in sendRequest(f"{baseURL}/api/v4/groups/{groupId}/epics/{iid}"):
            yield WorkItem(
                id=epicId,
                type=WorkItemType.EPIC,
                parentId=None,
                url=epic["web_url"],
                project=None,
                title=epic["title"],
                descriptionLength=len(epic["description"] or ""),
                created=parseDate(epic["created_at"]),
                closed=parseDate(epic["closed_at"]),
                author=None,
                assignees=[],
                labels=epic["labels"],
            )


def fetchPullRequests(
    baseURL: str, groups: list[str], projects: list[str], start: str
) -> Iterator[PullRequest]:
    groupURLs = [
        f"{baseURL}/api/v4/groups/{urllib.parse.quote_plus(group)}/merge_requests"
        for group in groups
    ]
    projectURLs = [
        f"{baseURL}/api/v4/projects/{urllib.parse.quote_plus(project)}/merge_requests"
        for project in projects
    ]

    for url in groupURLs + projectURLs:
        for pr in sendMultipartRequest(
            f"{url}?state=all&scope=all&include_subgroups=true&&created_after={start}"
        ):
            yield PullRequest(
                id=pr["id"],
                url=pr["web_url"],
                project=pr["references"]["full"].split("#")[0],
                title=pr["title"],
                created=parseDate(pr["created_at"]),
                closed=parseDate(pr["merged_at"]),
                assignees=[assignee["name"] for assignee in pr["assignees"]],
                reviewers=[reviewer["name"] for reviewer in pr["reviewers"]],
            )


def exportGitLabData(
    baseURL: str, groups: list[str], projects: list[str], start: str
) -> IssueTrackerData:
    issues = list(fetchIssues(baseURL, groups, projects, start))
    epics = list(fetchEpics(baseURL, issues))
    pullRequests = list(fetchPullRequests(baseURL, groups, projects, start))
    return IssueTrackerData("GitLab", datetime.now(), epics + issues, pullRequests)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Exports GitLab issues into a format that can be analyzed by Sigrid."
    )
    parser.add_argument(
        "--gitlab-base-url", type=str, required=True, help="GitLab base URL."
    )
    parser.add_argument(
        "--group",
        type=str,
        default="",
        help="Comma-separated list of GitLab group paths.",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="",
        help="Comma-separated list of GitLab project paths.",
    )
    parser.add_argument(
        "--exclude-labels",
        type=str,
        default="",
        help="Comma-separated labels to be excluded.",
    )
    parser.add_argument(
        "--out", type=str, default=".sigrid/gitlab-issues.json", help="Output file."
    )
    parser.add_argument(
        "--start",
        type=str,
        default="1970-01-01",
        help="Export issues created after (yyyy-mm-dd).",
    )
    parser.add_argument(
        "--anonymize", action="store_true", help="Anonymize author names."
    )
    args = parser.parse_args()

    if "GITLAB_API_TOKEN" not in os.environ:
        print("Missing environment variable GITLAB_API_TOKEN")
        sys.exit(1)

    groups = args.group.split("," if args.group else None)
    projects = args.project.split("," if args.project else None)
    excludeLabels = args.exclude_labels.split(",") if args.exclude_labels else []

    data = exportGitLabData(args.gitlab_base_url, groups, projects, args.start)
    filterIssueData(data, excludeLabels)
    outputFile = os.path.expanduser(args.out)
    serialize(data, outputFile, args.anonymize)
    print(f"Exported {len(data.workItems)} work items to {outputFile}")
