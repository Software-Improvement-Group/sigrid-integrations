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

from collections import defaultdict


class ArchitectureGraph:
    HIERARCHY_DEPENDENCIES = ["CONTAINS", "PROVIDES", "STORES"]
    CALL_DEPENDENCIES = ["CODE_CALL", "DATA_ACCESS", "INTERFACE_CALL"]

    def __init__(self, graph):
        self.graph = graph
        self.systemLevel = next(se for se in self.graph["systemElements"] if se["type"] == "SYSTEM")
        self.systemElements = {se["id"]: se for se in self.graph["systemElements"]}

        self.children = defaultdict(list)
        for dependency in graph["dependencies"]:
            if dependency["type"] in self.HIERARCHY_DEPENDENCIES:
                self.children[dependency["sourceElementId"]].append(dependency["targetElementId"])

    def crawlHierarchy(self, subjectId):
        hierarchy = {subjectId}
        for childId in self.children[subjectId]:
            hierarchy = hierarchy.union(self.crawlHierarchy(childId))
        return hierarchy

    def getTopLevelComponents(self):
        topLevel = [self.systemElements[childId] for childId in self.children[self.systemLevel["id"]]]
        return [se for se in topLevel if se["type"] == "CODE_COMPONENT"]

    def findDependencies(self, source, target):
        if source["id"] == target["id"]:
            return 0

        sourceHierarchy = self.crawlHierarchy(source["id"])
        targetHierarchy = self.crawlHierarchy(target["id"])

        for dependency in self.graph["dependencies"]:
            if dependency["type"] in self.CALL_DEPENDENCIES:
                if dependency["sourceElementId"] in sourceHierarchy and dependency["targetElementId"] in targetHierarchy:
                    yield dependency

    def countDependencies(self, source, target):
        return sum(dependency["count"] for dependency in self.findDependencies(source, target))
