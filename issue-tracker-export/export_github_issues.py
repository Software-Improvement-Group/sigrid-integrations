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
import re
import sys
import urllib.parse
import urllib.request
from argparse import ArgumentParser

from issue_data import Issue
from issue_data_serializer import IssueDataSerializer


def fetchIssues(apiBaseURL, org, repo):
    url = f"{apiBaseURL}/repos/{org}/{repo}/issues?state=all"
    while url is not None:
        request = urllib.request.Request(url)
        request.add_header("Authorization", f"Bearer: {os.environ['GITHUB_API_TOKEN']}")
        with urllib.request.urlopen(request) as response:
            issues = json.loads(response.read().decode("utf8"))
            for issue in issues:
                yield parseIssue(org, repo, issue)
            link = re.compile("<(\\S+?)>; rel=\"next\"").search(response.headers.get("link", ""))
            url = link.group(1) if link else None


def parseDate(value):
    if value in (None, "", "None"):
        return None
    return dateutil.parser.isoparse(value)


def parseIssue(org, repo, issue):
    return Issue(
        id=issue["id"],
        project=f"{org}/{repo}",
        title=issue["title"],
        status=issue["state"],
        created=parseDate(issue["created_at"]),
        closed=parseDate(issue["closed_at"]),
        author=issue["user"]["login"],
        assignee=issue["assignee"]["login"] if issue["assignee"] else None,
        epic=None,
        labels=[label["name"] for label in issue["labels"]]
    )


if __name__ == "__main__":
    parser = ArgumentParser(description="Exports GitHub issues into a format that can be analyzed by Sigrid.")
    parser.add_argument("--github-api-url", type=str, default="https://api.github.com")
    parser.add_argument("--org", type=str, required=True, help="GitHub organization name.")
    parser.add_argument("--repo", type=str, required=True, help="Comma-separated list of GitHub repository names.")
    parser.add_argument("--out", type=str, default=".sigrid", help="Output directory.")
    args = parser.parse_args()

    if not "GITHUB_API_TOKEN" in os.environ:
        print("Missing environment variable GITHUB_API_TOKEN")
        sys.exit(1)

    repoIssues = [list(fetchIssues(args.github_api_url, args.org, repo)) for repo in args.repo.split(",")]
    issues = list(itertools.chain(*repoIssues))
    outputDir = os.path.expanduser(args.out)

    IssueDataSerializer.serialize("GitHub", issues, outputDir)
    print(f"Exported {len(issues)} issues to {outputDir}")
