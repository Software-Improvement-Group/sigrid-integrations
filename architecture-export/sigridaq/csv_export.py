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

import csv


def exportCsv(architectureGraph, csvFile):
    with open(csvFile, "w", encoding="utf8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["from", "to", "weight", "type"])
        for source in architectureGraph.getTopLevelComponents():
            for target in architectureGraph.getTopLevelComponents():
                counts = architectureGraph.countDependenciesByType(source, target)
                for dependencyType, weight in counts.items():
                    writer.writerow([componentName(source), componentName(target), weight, dependencyType])


def componentName(component):
    return component.get("shortName") or component["name"]
