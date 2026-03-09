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
import hashlib
import os
from dataclasses import asdict
from datetime import datetime
from json import dump
from typing import Union

from issue_data_model import IssueTrackerData


def parseDate(value: Union[str, None]) -> Union[datetime, None]:
    if value in (None, "", "None"):
        return None
    return dateutil.parser.isoparse(value)


def serialize(data: IssueTrackerData, outputFile: str, anonymize: bool) -> None:
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)

    if anonymize:
        for workItem in data.workItems:
            workItem.author = anonymizeAuthorName(workItem.author) if workItem.author else None
            workItem.assignees = [anonymizeAuthorName(assignee) for assignee in workItem.assignees]
        for pr in data.pullRequests:
            pr.assignees = [anonymizeAuthorName(assignee) for assignee in pr.assignees]
            pr.reviewers = [anonymizeAuthorName(reviewer) for reviewer in pr.reviewers]

    with open(outputFile, "w", encoding="utf8") as f:
        dump(asdict(data), f, indent=4, ensure_ascii=False, default=serializeFieldToJSON)


def serializeFieldToJSON(field: str) -> str:
    if isinstance(field, datetime):
        return field.isoformat()
    raise TypeError(f"Cannot serialize field to JSON: {type(field)}")


def anonymizeAuthorName(name: str) -> str:
    return hashlib.sha256(name.encode("utf8")).hexdigest()


def filterIssueData(issueData: IssueTrackerData, excludeLabels: list[str]) -> None:
    def isExcluded(labels):
        return bool(set(labels) & set(excludeLabels))
    issueData.workItems = [workItem for workItem in issueData.workItems if not isExcluded(workItem.labels)]
