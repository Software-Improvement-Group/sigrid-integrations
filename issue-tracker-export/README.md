## Sigrid issue tracker export

Exports issue tracker history into a format that can be analyzed by Sigrid. The issue tracker data is then used
to provide insights and metrics related to Development Efficiency.

This functionality is currently *experimental*, and is being used in collaboration with interested Sigrid partners
and customers. This functionality will eventually become available to all Sigrid customers.

The following issue trackers are supported:

- [GitHub](#usage-for-github)
- [GitLab](#usage-for-gitlab)
- [JIRA](#usage-for-jira)
- [Azure DevOps](#usage-for-azure-devops)

## Prerequisites

- These scripts require Python 3.9+. 
- There are no additional dependencies.

## Usage for GitHub

You can export your GitHub issues from your pipeline using these scripts. Depending on your environment, you can
either clone this repository and then run the script, or you can run the script via the Docker container.

    ./export_github_issues --github-api-url https://api.github.com --org mycompany --repo myrepo

The script requires an environment variable called `GITHUB_API_TOKEN`, which should be a
[fine-grained personal access token for GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#fine-grained-personal-access-tokens)
which has access to the issues you want to export.

These scripts will export the issue tracker data to a location where it can be picked up by 
[Sigrid CI](https://docs.sigrid-says.com/sigridci-integration/github-actions.html). Therefore, you should run this
step *before* you run the Sigrid CI step in your pipeline configuration.

## Usage for GitLab

You can export your GitLab issues from your pipeline using these scripts. Depending on your environment, you can
either clone this repository and then run the script, or you can run the script via the Docker container.

    ./export_gitlab_issues.py --gitlab-base-url https://code.example.com [--project namespace/name | --group group_name]

- `--gitlab-base-url`: Specify the base URL of your GitLab instance, including `https://`.
- `--project`: Provide a GitLab project name or ID. You can specify multiple projects using a comma-separated list.
- `--group`: Provide a GitLab group name or ID. You can specify multiple groups using a comma-separated list.
- You must provide at least one of `--project` or `--group`.

The script requires an environment variable called `GITLAB_API_TOKEN`, which should be a GitLab API token that is
allowed to access the project/group issues you want to export.

These scripts will export the issue tracker data to a location where it can be picked up by
[Sigrid CI](https://docs.sigrid-says.com/sigridci-integration/gitlab.html). Therefore, you should run this step 
*before* you run the Sigrid CI step in your pipeline configuration.

## Usage for JIRA

You can export your JIRA issues from your pipeline using these scripts. Depending on your environment, you can
either clone this repository and then run the script, or you can run the script via the Docker container.

Running this script requires two environment variables:

- `JIRA_API_TOKEN` containing a valid
  [JIRA personal access token](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html).
- `JIRA_API_USER` containing the email address of the JIRA user that owns the personal access token.

    ./export_jira_issues.py --jira-base-url jira.example.com --project AAP

The `--project` argument is used to control which projects should be exported. It should contain a comma-separated
list of [JIRA project keys](https://confluence.atlassian.com/adminjiraserver/editing-a-project-key-938847080.html).

## Usage for Azure DevOps

You can export your Azure DevOps work items from your pipeline using these scripts. Depending on your environment, you
can either clone this repository and then run the script, or you can run the script via the Docker container.

    ./export_azure_devops_issues.py --ado-api-url https://dev.azure.com --org myorganization --project myproject

- `--ado-api-url`: Specify the base URL of your Azure DevOps instance (default: `https://dev.azure.com`). Override this for Azure DevOps Server (on-premises) installations.
- `--org`: Provide your Azure DevOps organization name.
- `--project`: Provide one or more Azure DevOps project names as a comma-separated list.
- `--epic-type`: The work item type used for epics (default: `Epic`). Override this if your organization uses a custom type.
- `--exclude-labels`: Comma-separated list of tags to exclude from the export.
- `--start`: Only export work items created after this date (format: `yyyy-mm-dd`).

The script requires an environment variable called `AZURE_DEVOPS_PAT`, which should be a
[personal access token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)
with **Work Items (Read)** and **Code (Read)** scope.

## What issue tracker data is published to Sigrid?

The issue tracker integration exports issues in a generic format, which is then published to Sigrid.
The description of your issue will **not** be published to Sigrid. The export only contains metadata for each issue,
such as its type, its status, and the dates it was created and closed.

The issue data will contain the names of the authors and assignees. You can anonymize these names, meaning the
actual name will be replaced with a SHA-256 hash when exporting the data. This means the original names are never
published to Sigrid.

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
