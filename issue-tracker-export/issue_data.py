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

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Issue:
    id: str
    project: str
    title: str
    status: str
    created: datetime
    closed: datetime
    author: str
    assignee: str
    epic: str
    labels: list[str]


@dataclass
class IssueTrackerData:
    platform: str
    exported: datetime
    issues: list[Issue]
