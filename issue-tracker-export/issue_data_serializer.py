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

import hashlib
import os
from dataclasses import asdict, replace
from datetime import datetime
from json import dump, JSONEncoder

from issue_data import Issue, IssueTrackerData


class IssueDataSerializer(JSONEncoder):
    def default(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, Issue):
            return self.anonymizeIssue(value)
        else:
            return JSONEncoder.default(self, value)

    @staticmethod
    def serialize(platform, issues, outputDir):
        os.makedirs(outputDir, exist_ok=True)
        outputFile = f"{outputDir}/{platform.lower()}-issues.json"
        with open(outputFile, "w", encoding="utf8") as f:
            anonymizedIssues = [IssueDataSerializer.anonymizeIssue(issue) for issue in issues]
            data = IssueTrackerData(platform, datetime.now(), anonymizedIssues)
            dump(asdict(data), f, indent=4, cls=IssueDataSerializer)

    @staticmethod
    def anonymizeIssue(issue):
        anonymized = replace(issue)
        if issue.author:
            anonymized.author = hashlib.sha256(issue.author.encode("utf8")).hexdigest()
        if issue.assignee:
            anonymized.assignee = hashlib.sha256(issue.assignee.encode("utf8")).hexdigest()
        return anonymized
