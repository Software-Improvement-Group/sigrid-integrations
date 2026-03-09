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
import re
import sys
import urllib.parse
import urllib.request
from argparse import ArgumentParser
from datetime import datetime
from typing import Iterator

from issue_data_model import IssueTrackerData, PullRequest, WorkItem, WorkItemType
from issue_utils import parseDate, serialize


def fetchAll(apiBaseURL: str, org: str, repo: str, path: str) -> Iterator:
    url = f"{apiBaseURL}/repos/{org}/{repo}{path}&per_page=100&page=1"
    while url is not None:
        request = urllib.request.Request(url)
        request.add_header("Authorization", f"Bearer: {os.environ['GITHUB_API_TOKEN']}")
        with urllib.request.urlopen(request) as response:
            for element in json.loads(response.read().decode("utf8")):
                yield element
            link = re.compile("<(\\S+?)>; rel=\"next\"").search(response.headers.get("link", ""))
            url = link.group(1) if link else None


def fetchIssues(apiBaseURL: str, org: str, repo: str) -> list[WorkItem]:
    return [parseIssue(org, repo, issue) for issue in fetchAll(apiBaseURL, org, repo, "/issues?state=all")]


def parseIssue(org: str, repo: str, issue: dict) -> WorkItem:
    return WorkItem(
        id=issue["id"],
        type=WorkItemType.ISSUE,
        parentId=issue["milestone"]["id"] if issue["milestone"] else None,
        url=issue["html_url"],
        project=f"{org}/{repo}",
        title=issue["title"],
        descriptionLength=len(issue["body"] or ""),
        created=parseDate(issue["created_at"]),
        closed=parseDate(issue["closed_at"]),
        author=issue["user"]["login"],
        assignees=[assignee["login"] for assignee in issue["assignees"]],
        labels=[label["name"] for label in issue["labels"]]
    )


def fetchMilestones(apiBaseURL: str, org: str, repo: str) -> list[WorkItem]:
    return [parseMilestone(milestone) for milestone in fetchAll(apiBaseURL, org, repo, "/milestones?state=all")]


def parseMilestone(milestone: dict) -> WorkItem:
    return WorkItem(
        id=milestone["id"],
        type=WorkItemType.EPIC,
        parentId=None,
        url=milestone["html_url"],
        project=None,
        title=milestone["title"],
        descriptionLength=0,
        created=parseDate(milestone["created_at"]),
        closed=parseDate(milestone["closed_at"]),
        author=None,
        assignees=[],
        labels=[]
    )


def fetchPullRequests(apiBaseURL: str, org: str, repo: str) -> list[PullRequest]:
    return [parsePullRequest(org, repo, pr) for pr in fetchAll(apiBaseURL, org, repo, "/pulls?state=all")]


def parsePullRequest(org: str, repo: str, pr: dict) -> PullRequest:
    return PullRequest(
        id=pr["id"],
        url=pr["url"],
        project=f"{org}/{repo}",
        title=pr["title"],
        created=parseDate(pr["created_at"]),
        closed=parseDate(pr["merged_at"]),
        assignees=[assignee["login"] for assignee in pr["assignees"]],
        reviewers=[reviewer["login"] for reviewer in pr["requested_reviewers"]],
    )


def combine(repoData: list[list]) -> list:
    return list(itertools.chain(*repoData))


if __name__ == "__main__":
    parser = ArgumentParser(description="Exports GitHub issues into a format that can be analyzed by Sigrid.")
    parser.add_argument("--github-api-url", type=str, default="https://api.github.com")
    parser.add_argument("--org", type=str, required=True, help="GitHub organization name.")
    parser.add_argument("--repo", type=str, required=True, help="Comma-separated list of GitHub repository names.")
    parser.add_argument("--out", type=str, default=".sigrid/github-issues.json", help="Output file.")
    parser.add_argument("--anonymize", action="store_true", help="Anonymize author names.")
    args = parser.parse_args()

    if "GITHUB_API_TOKEN" not in os.environ:
        print("Missing environment variable GITHUB_API_TOKEN")
        sys.exit(1)

    repos = args.repo.split(",")
    repoIssues = [list(fetchIssues(args.github_api_url, args.org, repo)) for repo in repos]
    repoMilestones = [list(fetchMilestones(args.github_api_url, args.org, repo)) for repo in repos]
    repoPRs = [list(fetchPullRequests(args.github_api_url, args.org, repo)) for repo in repos]

    data = IssueTrackerData("GitHub", datetime.now(), combine(repoIssues) + combine(repoMilestones), combine(repoPRs))
    outputFile = os.path.expanduser(args.out)
    serialize(data, outputFile, args.anonymize)
    print(f"Exported {len(data.workItems)} work items to {outputFile}")
