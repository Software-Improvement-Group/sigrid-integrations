#  Copyright Software Improvement Group
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from functools import cached_property
from report_generator.generator import sigrid_api
from report_generator.generator.data_models.portfolio.base import AbstractPortfolioModel

import pandas as pd
import numpy as np


class SigridHygienePortfolioData(AbstractPortfolioModel):
    def __init__(self):
        self.metadata_fields = ["softwareDistributionStrategy", "applicationType", "deploymentType", "targetIndustry",
                                "lifecyclePhase", "businessCriticality", "inProductionSince", "supplierNames", "teamNames", "divisionName"]

    @cached_property
    def get_metadata_fields(self):
        return ["Distribution strategy", "Application type", "Deployment type", "Target industry", "Lifecycle phase",
                "Business criticality", "In production since", "Supplier", "Team", "Division"]


    def _compute_metadata_dataframe(self):
        df = pd.DataFrame(columns=self.metadata_fields)
        metadata = {system["systemName"]: system for system in self.metadata}
        active_systems = [name for name, meta in metadata.items() if meta["active"] and not meta["isDevelopmentOnly"]]

        for system in active_systems:
            row = {}

            for field in self.metadata_fields:
                value_metadata = metadata[system][field]
                row[field] = 0 if not value_metadata else 1

            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

        return df


    def get_portfolio_metadata_completeness(self):
        metadata_df = self._compute_metadata_dataframe()
        column_completeness = metadata_df.sum().to_dict()
        total_systems = len(metadata_df)
        row = [[], []]

        for field in self.metadata_fields:
            complete = np.round(column_completeness[field] / total_systems * 100, 0).astype(int)
            row = np.hstack((row, [[complete], [100-complete]]))

        return row

    def get_number_systems_complete_metadata(self):
        metadata_df = self._compute_metadata_dataframe()
        fully_complete_count = (metadata_df.sum(axis=1) == len(self.metadata_fields)).sum()
        return fully_complete_count


sigrid_hygiene_portfolio_data = SigridHygienePortfolioData()

