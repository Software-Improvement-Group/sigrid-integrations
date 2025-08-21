## Sigrid issue tracker export

Exports issue tracker history into a format that can be analyzed by Sigrid. The issue tracker data is then used
to provide insights and metrics related to Development Efficiency.

This functionality is currently *experimental*, and is being used in collaboration with interested Sigrid partners
and customers. This functionality will eventually become available to all Sigrid customers.

The following issue trackers are supported:

- [GitHub](#usage-for-github)
- [GitLab](#usage-for-gitlab)
- [JIRA](#usage-for-jira)

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
Running this script requires the environment variable `JIRA_API_TOKEN` containing a valid
[JIRA personal access token](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html).

    ./export_jira_issues.py --jira-base-url jira.example.com --project AAP

The `--project` argument is used to control which projects should be exported. It should contain a comma-separated
list of [JIRA project keys](https://confluence.atlassian.com/adminjiraserver/editing-a-project-key-938847080.html).

## What issue tracker data is published to Sigrid?

The issue tracker integration exports issues in a generic format, which is then published to Sigrid. 
The following information is exported for each issue:

  - Project name
  - Title
  - Status
  - Created date
  - Closed date
  - Author
  - Assignee
  - Epic title
  - List of labels

The name of the author and assignee are anonymized into an SHA-256 hash. This means the original names are never
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
