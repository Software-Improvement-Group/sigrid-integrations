# Create JIRA issues based on Sigrid findings in Azure DevOps

This script can automatically create [JIRA](https://www.atlassian.com/software/jira) issues for all Sigrid findings
that match certain criteria. This script is implemented in PowerShell, and needs to run as part of an Azure DevOps
pipeline.

## Configuration

Configuration is done using two files:

- **[input.txt](input/input.txt)**
  - `sigRestAPIMain`: URL for retrieving Sigrid maintainability findings.
  - `sigRestAPISec`: URL for retrieving Sigrid security findings.
  - `sigRestAPIOSH`: URL for retrieving Sigrid Open Source Health findings.
  - `sigToken`: Sigrid API token.
  - `xxxProxy`: Proxy URL for connecting to the internet.
  - `jiraEnv`: JIRA environment, "P" indicates production.
  - `jiraAPI`: JIRA API URL, for example "https://jira.xxx.nl/rest/api/2".
  - `jiraToken`: JIRA API token.
  - `jiraExternalIDField`: JIRA external issue field, for example "External Issue ID".
  - `emailSMTP`: When sending emails, use the following SMTP server, for example "smtpsrv.xxx.nl".
  - `emailList`: When sending emails, send the emails to the following recipients, for example "developer@xxx.nl".
  - `mailFrom`: When sending emails, use the following email address as the sender, for example "noreply@xxx.nl".
- **[control.json](input/control.json)**
  - This JSON file contains an array of system/project entries.
    - `App`: Name of the Sigrid system.
    - `JiraProject`: Name of the JIRA project corresponding to the Sigrid system.
    - `GetSIGFindings`: Whether the integration is enabled, either "Y" or "N".
    - `AllowCreateJiraUS`: Whether the integration is allowed to create JIRA user stories, either "Y" or "N".
    - `SevDepth`: Severity filter, "1" means critical findings only, "2" means high, "3" means medium.

## License

Copyright Software Improvement Group

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
