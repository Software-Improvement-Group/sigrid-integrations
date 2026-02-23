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
# Import modules
# =====================================
$global:rootPath = $PSScriptRoot
$moduleUtilities = Join-Path -Path $rootPath -ChildPath "modules/Utilities.psm1"
$moduleJira = Join-Path -Path $rootPath -ChildPath "modules/JiraUtils.psm1"
$moduleEmail = Join-Path -Path $rootPath -ChildPath "modules/EmailUtils.psm1"

Import-Module $moduleUtilities -Force
Import-Module $moduleJira -Force
Import-Module $moduleEmail -Force

# =====================================
# declarations
# =====================================
$inputFile = Join-Path -Path $rootPath -ChildPath "input/input.txt"
$controlFile = Join-Path -Path $rootPath -ChildPath "input/control.json"

$config = Get-Content-From-File -path $inputFile
$sigRestAPIMain = $config.'sigRestAPIMain'
$sigRestAPISec = $config.'sigRestAPISec'
$sigToken = $config.'sigToken'
$xxxProxy = $config.'xxxProxy'
$jiraEnv = $config.'jiraEnv'
switch ($jiraEnv) {
    'P' {
        $jiraAPI = $config.'jiraAPI'
        $jiraToken = $config.'jiraToken'
    }
    Default {
        $jiraAPI = $config.'jiraAPI_TEST'
        $jiraToken = $config.'jiraToken_TEST'
    }
}
$jiraExternalIDField = $config.'jiraExternalIDField'
$emailSMTP = $config.'emailSMTP'
$emailTo = $config.'emailList'
$emailFrom = $config.'emailFrom'
$doDebug = $config.'doDebug'

# =====================================
# initialize and start clean
# =====================================
$global:startDateTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
$reportTable = @()
Move-Logs-To-Archive

# this block with aggregate tables is used for debugging purposes only
$aggrTable = $null
$aggrTableSev = $null
$aggrTableWithoutJira = $null
$aggrTableMultiJira = $null
$aggrTableWithJira = $null
$aggrTableWithJiraAdded = $null

# =====================================
# start main
# =====================================
Write-Log "=== Start (on Jira $jiraEnv environment) ==="

# =====================================
# invoke SIGRID Rest API and get Company XXX Portfolio applications
# =====================================
$sig = Invoke-RestMethod -Uri $sigRestAPIMain -Headers @{ 'Authorization' = "Bearer $sigToken"  } -Proxy $xxxProxy -ProxyUseDefaultCredentials

# =====================================
# loop over each Company XXX application
# =====================================
 $sig.systems | ForEach-Object -Process {
    $app = $_.system
    
    # =====================================
    # get info from control file
    # =====================================
    $getSIGFindings = Get-Control-Info -path $controlFile -searchId $app -paramCol "GetSIGFindings"
    if($getSIGFindings -ne "No Value"){
        $jiraProject = Get-Control-Info -path $controlFile -searchId $app -paramCol "JiraProject"
        $jiraAllowCreate = Get-Control-Info -path $controlFile -searchId $app -paramCol "AllowCreateJiraUS"
        $severityDepth = (Get-Control-Info -path $controlFile -searchId $app -paramCol "SevDepth")
    }

    $newTable = $null
    $newTableSev = @()
    $newTableWithoutJira = @()
    $newTableMultiJira = @()
    $newTableWithJira = @()
    $newTableWithJiraAdded = @()

    # =====================================
    # invoke SIGRID Security API
    # =====================================
    if($getSIGFindings -eq "Y"){
        Write-Log-Block "Start $app"
        $sigFindings = Get-SIG-Findings -uri $sigRestAPISec -application $app -token $sigToken -proxy $xxxProxy

        # =====================================
        # process the findings into a table and apply filtering on severity
        # =====================================
        $newTable = New-Table -application $app -apiResult $sigFindings -jiraProject $jiraProject
        $newTableSev = Select-Sev-Table -filterDepth $severityDepth -unfilteredTable $newTable

        # =====================================
        # for each findings check if Jira US exists, and store result in new temporary Objects
        # =====================================
        $processTable = $newTableSev

        foreach ($rowProcessTable in $processTable) {
            $jiraId = Get-Jira-Issue -restAPI $jiraAPI -tokenJira $jiraToken -searchField $jiraExternalIDField -searchValue $rowProcessTable.uid
            if($jiraId -eq 'NR'){
                $newTableWithoutJira += $rowProcessTable
            }elseif($jiraId -eq 'MT1'){
                $newTableMultiJira += $rowProcessTable
            }else{
                $newTableWithJira += Add-JiraUS-To-Table -rowId $rowProcessTable.uid -jiraId $jiraId -inputTable $processTable
            }
        }

        # =====================================
        # for each findings without Jira US, create new Jira US and store result in $newTableWithJiraNew
        # =====================================
        $userRightsJiraProject = Get-Rights-Jira-Project -restAPI $jiraAPI -tokenJira $jiraToken -projectName $jiraProject
        
        # Copy table without reference...
        $newTableWithoutJira_Copy = ($newTableWithoutJira | ConvertTo-Json -Depth 10 | ConvertFrom-Json)

        if($jiraAllowCreate -eq "Y" -and $userRightsJiraProject -eq $true ){
            Write-Log "Start create Jira User Stories in Project=$jiraProject. There will $(@($newTableWithoutJira_Copy).Count) User Stories be created."
            $optionalJiraFields = Get-Screen-Fields-Jira-Project -restAPI $jiraAPI -tokenJira $jiraToken -jiraProject $jiraProject
            foreach ($rowCreateJira in $newTableWithoutJira_Copy){
                $jiraCreatedId = New-Jira-US -restAPI $jiraAPI -tokenJira $jiraToken -jiraProject $jiraProject -findingSIG $rowCreateJira -optionalFields $optionalJiraFields
                if($jiraCreatedId -ne "Error"){
                    $newTableWithJiraAdded += Add-JiraUS-To-Table -rowId $rowCreateJira.uid -jiraId $jiraCreatedId -inputTable $newTableWithoutJira_Copy
                }
            }
        }else{
            Write-Log "No Jira User Stories create, beceause AllowCreateJiraUS = $jiraAllowCreate or the user does not have rights."
        }

        # =====================================
        # Gather info for reporting
        # =====================================
        $reportTable += [PSCustomObject]@{
            App = $App
            JiraProject = $JiraProject
            GetSIGFindings = $GetSIGFindings
            AllowCreateJiraUS = $jiraAllowCreate
            SevDepth = $severityDepth
            sigCount = @($newTableSev).Count
            JiraExist = @($newTableWithJira).Count
            JiraMissing = @($newTableWithoutJira).Count
            JiraAdded = @($newTableWithJiraAdded).Count
        }
        
        # Write some more info to the log
        Write-Log "For $app > Number findings in SIGRID = $(@($newTableSev).Count)"
        Write-Log "For $app > Number findings with already existing Jira User Story = $(@($newTableWithJira).Count)"
        Write-Log "For $app > Number findings without Jira User Story = $(@($newTableWithoutJira).Count)"
        Write-Log "For $app > Number new created Jira User Story = $(@($newTableWithJiraAdded).Count)"
        Write-Log-Block "Einde $app"

        # extend aggregate tables (for debugging purposes)
        $aggrTable += $newTable
        $aggrTableSev += $newTableSev
        $aggrTableWithoutJira += $newTableWithoutJira
        $aggrableMultiJira += $newTableMultiJira
        $aggrTableWithJira += $newTableWithJira
        $aggrTableWithJiraAdded += $newTableWithJiraAdded
    }
    else {
        Write-Log "Based on the control.json no action for application $app"
    }
 }
Write-Log "=== End. $(@($sig.systems).Count) applications processed ==="

# =====================================
# Print the tables for debugging purposes
# =====================================
if($doDebug -eq 'Y'){
    Write-Object -customObjectName "aggrTable" -customObject $aggrTable
    Write-Object -customObjectName "aggrTableSev" -customObject $aggrTableSev
    Write-Object -customObjectName "aggrTableWithoutJira" -customObject $aggrTableWithoutJira
    Write-Object -customObjectName "aggrTableMultiJira" -customObject $aggrTableMultiJira
    Write-Object -customObjectName "aggrTableWithJira" -customObject $aggrTableWithJira
    Write-Object -customObjectName "aggrTableWithJiraAdded" -customObject $aggrTableWithJiraAdded
}

# =====================================
# Prepare and send email
# =====================================
$countErrors = Get-Error-Count
$htmlTable = EmailTable_HTML -Data $reportTable

Send-Report -emailSMTP $emailSMTP -emailTo $emailTo -emailFrom $emailFrom -reportData $htmlTable -errorCount $countErrors
Write-Log "=== Report per Email verstuurd ==="