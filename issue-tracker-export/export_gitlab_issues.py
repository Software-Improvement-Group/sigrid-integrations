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

from issue_data import Issue, IssueTrackerData
from issue_data_serializer import IssueDataSerializer


def sendMultipartRequest(url):
    for page in itertools.count(start=1):
        request = urllib.request.Request(f"{url}&page={page}&per_page=100")
        request.add_header("PRIVATE-TOKEN", os.environ["GITLAB_API_TOKEN"])
        with urllib.request.urlopen(request) as response:
            yield from json.loads(response.read().decode("utf8"))
            if not response.headers.get("X-Next-Page"):
                break


def fetchIssues(baseURL, groups, projects):
    for group in groups:
        slug = urllib.parse.quote_plus(group)
        for issue in sendMultipartRequest(f"{baseURL}/api/v4/groups/{slug}/issues?scope=all&state=all"):
            yield parseIssue(issue)

    for project in projects:
        slug = urllib.parse.quote_plus(project)
        for issue in sendMultipartRequest(f"{baseURL}/api/v4/projects/{slug}/issues?scope=all&state=all"):
            yield parseIssue(issue)
    

def parseDate(value):
    if value in (None, "", "None"):
        return None
    return dateutil.parser.isoparse(value)


def parseIssue(issue):
    return Issue(
        id=issue["id"],
        project=issue["references"]["full"].split("#")[0],
        title=issue["title"],
        status=issue["state"],
        created=parseDate(issue["created_at"]),
        closed=parseDate(issue["closed_at"]),
        author=issue["author"]["name"],
        assignee=issue["assignee"]["name"] if issue["assignee"] else None,
        epic=issue["epic"]["title"] if issue["epic"] else None,
        labels=issue["labels"]
    )


if __name__ == "__main__":
    parser = ArgumentParser(description="Exports GitLab issues into a format that can be analyzed by Sigrid.")
    parser.add_argument("--gitlab-base-url", type=str, required=True, help="GitLab base URL.")
    parser.add_argument("--group", type=str, default="", help="Comma-separated list of GitLab group paths.")
    parser.add_argument("--project", type=str, default="", help="Comma-separated list of GitLab project paths.")
    parser.add_argument("--out", type=str, default=".sigrid", help="Output directory.")
    args = parser.parse_args()

    if not "GITLAB_API_TOKEN" in os.environ:
        print("Missing environment variable GITLAB_API_TOKEN")
        sys.exit(1)

    groups = args.group.split("," if args.group else None)
    projects = args.project.split("," if args.project else None)
    outputDir = os.path.expanduser(args.out)

    issues = list(fetchIssues(args.gitlab_base_url, groups, projects))
    IssueDataSerializer.serialize("GitLab", issues, outputDir)
    print(f"Exported {len(issues)} issues to {outputDir}")
