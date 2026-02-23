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

# =====================================
# Check if Jira Issue exists (via API)
# =====================================
function Get-Jira-Issue{
    param(
        [String]$restAPI,
        [String]$tokenJira,
        [String]$searchField,
        [String]$searchValue
    )
    # Set up headers for authentication and content type
    $headers = @{ 
        #'Authorization' = "Basic $( [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($userName):$($tokenJira)")) )"
        'Authorization' = "Bearer $($tokenJira)"
        'Content-Type'  = 'application/json'
    }

    # Define body with JQL query parameters for POST request
    # The jql should be something like: 'External Issue ID'~ff4daf92-334a-4009-bdfa-3a342fcfe3eb
    $body = @{
        jql        = "$searchField~$searchValue"
        maxResults = 50
    } | ConvertTo-Json -Depth 3

    try {

        # Invoke REST method using POST
        $response = Invoke-RestMethod -Uri $restAPI/search? -Method Post -Headers $headers -Body $body
        
        # Check if the result
        if($response.total -lt 1){
            Write-Log "No result for jql = $searchField~$searchValue"
            return "NR"
        }
        elseif($response.total -gt 1){
            Write-Log "More than 1 result! Check the jql = $searchField~$searchValue"
            return "MT1"
        }
        else{
             Write-Log "Found Jira User Story for $searchField~$searchValue > $($response.issues.key) in JiraProject=$($response.issues.fields.project.key) with Status=$($response.issues.fields.status.name)"
             return $($response.issues.key)
        }
    } catch {
        Write-Log "ERROR: Error calling Jira API: $_.Exception.Message"
    }
}

# =====================================
# Create Jira Issue (via API)
# =====================================
function  New-Jira-US{
    param(
        [String]$restAPI,
        [String]$tokenJira,
        [String]$jiraProject,
        [PSCustomObject]$findingSIG,
        [PSCustomObject]$optionalFields
    )

    $findingApp = $findingSIG.app
    $findingUID = $findingSIG.uid
    $findingURL = $findingSIG.url
    $findingDate = $findingSIG.firstSeenAnalysisDate
    $findingSev = $findingSIG.severity
    $findingScore = $findingSIG.severityScore

    # Use default priority = Medium
    $jiraPrio = "Medium"

    # set some conditionals for Jira User Story
    if($findingSIG.severity -eq "1-CRITICAL"){
        $findingSevColoured = "{color:#de350b}1-CRITICAL{color}"
        $jiraPrio = "Highest"
    } elseif ($findingSIG.severity -eq "2-HIGH") {
        $findingSevColoured = "{color:#ff8b00}2-HIGH{color}"
        $jiraPrio = "High"
    } elseif ($findingSIG.severity -eq "3-MEDIUM") {
        $findingSevColoured = "{color:#0747a6}3-MEDIUM{color}"
    } else {
        $findingSevColoured = $findingSev
    }

    # Set up headers for authentication and content type
    $headers = @{ 
        #'Authorization' = "Basic $( [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($userName):$($tokenJira)")) )"
        'Authorization' = "Bearer $($tokenJira)"
        'Content-Type'  = 'application/json'
    }

    try {
        # Define body with content for the Jira US
        # First initialize an empty fields hashtable
        $fields = @{}

        # ==========
        # Conditionally add elements... not every Jira Project has these fields. Check with your Jira Administrator...
        # ==========

        # Thema field > if exists than it is always mandatory
        if ($optionalFields.PSObject.Properties.Name -contains "customfield_12001") {
            $fields['customfield_12001'] = @{value = "IT continuïteit"}
        }
        # FRN field > if exists than put "NVT"
        if ($optionalFields.PSObject.Properties.Name -contains "customfield_11600") {
            $fields['customfield_11600'] = "NVT"
        }
        # Risico field > if exists than put "-"
        if ($optionalFields.PSObject.Properties.Name -contains "customfield_12902") {
            $fields['customfield_12902'] = "-"
        }                
        # Testplan field > if exists than put "-"
        if ($optionalFields.PSObject.Properties.Name -contains "customfield_13100") {
            $fields['customfield_13100'] = "-"
        }       

        # ==========
        # The following fields should always be present, else contact Jira Administrator to add to the Jira Project
        # ==========

        $fields['project'] = @{key = $jiraProject}
        $fields['issuetype'] = @{name = "Story"}
        $fields['summary'] = "SIGRID: Security Issue - $findingSev ($findingUID)"
        $fields['labels'] = "SIGRID","Security","QA"
        $fields['priority'] = @{name = $jiraPrio}
        $fields['customfield_11503'] = $findingDate
        $fields['customfield_11402'] = $findingUID
        $fields['description'] = "{panel:bgColor=#dfeff1}
                                h2. User Story
                                As our development organization,
                                we want the system *$findingApp* to remain secure and of high quality,
                                so that we are compliant to our security and quality guidelines.
                                h2. Background
                                Sigrid has identified findings for the system *$findingApp*, with severity *$findingSevColoured* and CVSS *$findingScore*. This finding is known since *$findingDate*.
                                You can find the finding details in Sigrid, using the following link.
                                $findingURL
                                h2. Next steps
                                1. Open Sigrid and investigate the finding.
                                2. Implement a fix.
                                3. Update the finding status in Sigrid."
        
        # Wrap it into the body hashtable and convert to JSON
        $body = @{ fields = $fields } | ConvertTo-Json -Depth 10

        #Create the Jira US
        $response = Invoke-RestMethod -Uri $restAPI/issue -Method Post -Headers $headers -Body $body
        Write-Log "For finding $findingUID a new Jira US has been made = $($response.key)"
        return $response.key
    }
    catch {
        Write-Log "ERROR: Error calling Jira API: $_.Exception.Message"
        return "Error"
    }
}

# =====================================
# Check if user has the rights to create User Story on Jira Project (via API)
# =====================================
function Get-Rights-Jira-Project {
    param (
        [String]$restAPI,
        [String]$tokenJira,
        [String]$projectName
    )

    # Set up headers for authentication and content type
    $headers = @{ 
        #'Authorization' = "Basic $( [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($userName):$($tokenJira)")) )"
        'Authorization' = "Bearer $($tokenJira)"
        'Content-Type'  = 'application/json'
    }

    try {
        # Invoke REST method to retrieve the rights
        $response = Invoke-RestMethod -Uri $restAPI/mypermissions?$projectName -Method Get -Headers $headers
        Write-Log "The JiraUser=$userName has for Project=$projectName the 'Create Issue' rights (True/False) = $($response.permissions."CREATE_ISSUES".havePermission)"
        return $response.permissions."CREATE_ISSUES".havePermission
    } 
    catch {
        Write-Log "ERROR: Error calling Jira API: $_.Exception.Message"
    }
}

# =====================================
# Get list of all fields of the specific Jira Project (via API). Because not all Jira Projects have been set-up the same; some may have more of less fields.
# =====================================
function Get-Screen-Fields-Jira-Project{
    param (
        [String]$restAPI,
        [String]$tokenJira,
        [String]$jiraProject
    )
    # Set up headers for authentication and content type
    $headers = @{ 
        #'Authorization' = "Basic $( [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($userName):$($tokenJira)")) )"
        'Authorization' = "Bearer $($tokenJira)"
        'Accept'  = 'application/json'
    }
    $jqlQuery = "project=$jiraProject AND issuetype=Story ORDER BY created DESC"

    try {
        # Invoke REST method to retrieve the rights
        $response = Invoke-RestMethod -Uri "$restAPI/search?jql=$jqlQuery&maxResults=1" -Headers $headers -Method Get
        Write-Log "Get the screen fields from Project=$jiraProject"
        return $response.issues.fields
    } 
    catch {
        Write-Log "ERROR: Error calling Jira API: $_.Exception.Message"
    }
}