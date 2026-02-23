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
# Get SIG findings
# =====================================
function Get-SIG-Findings{
    param (
        [String]$uri,
        [String]$application,
        [String]$token,
        [String]$proxy
    )
    try {
        $response = Invoke-RestMethod -Uri $uri"/"$app -Headers @{ 'Authorization' = "Bearer $token"  } -Proxy $proxy -ProxyUseDefaultCredentials
        Write-Log "Valid connection established with SIGRID op $uri"/"$app"
        return $response
    }
    catch {
        Write-Log "ERROR: No valid connection can be made with SIGRID on $uri"
        Write-Log $_.Exception.Message
        throw
    }
}

# =====================================
# Make tabel with only relevant info
# =====================================
function New-Table{
    param (
        [String]$application,
        [PSCustomObject]$apiResult,
        [String]$jiraProject
    )
    $output = @()

    foreach ($item in $apiResult) {
        $newItem = [PSCustomObject]@{
        app = $application
        uid = $item.id
        url = $item.href
        firstSeenAnalysisDate = $item.firstSeenAnalysisDate
        severity = Rename-Sev -String $item.severity
        severityScore = $item.severityScore
        jiraProject = $jiraProject
        jiraUS = ""
        }
        $output += $newItem
    }
    Write-Log "Total $(@($output).Count) findings for $application"
    return  $output 
 }

# =====================================
# Filter Tabel based on severity level (the control.json used severity levels 1 to 4 for Crtitical to Low
# =====================================
function  Select-Sev-Table{
     param (
        [Int]$filterDepth,
        [PSCustomObject]$unfilteredTable
    )
    
    $severityArray = @("1-CRITICAL", "2-HIGH", "3-MEDIUM", "4-LOW", "5-INFORMATION")
    if($filterDepth -ge 1 -and $filterDepth -le $severityArray.Count){
        $filterSevArray =  $severityArray[0..($filterDepth-1)]
        $output = $unfilteredTable | Where-Object{ $_.severity -in $filterSevArray}
        Write-Log "Total $(@($output).Count) findings with Severity = $filterSevArray"
        return  $output
    }
    else {
        Write-Log "Error: Invalid filterDepth $filterDepth"
    }
}

# =====================================
# Filter Tabel based on date (not used...)
# =====================================
function Select-Date-Table {
    param (
        [String]$filterDate,
        [PSCustomObject]$unfilteredTable
    )
    
    $filterDateObject = [datetime]::ParseExact($filterDate, 'yyyy-MM-dd', $null)
    
    $output = $unfilteredTable | Where-Object { 
        [datetime]::ParseExact($_.firstSeenAnalysisDate, 'yyyy-MM-dd', $null) -gt $filterDateObject 
    }
    Write-Log "Total $(@($output).Count) findings with firstSeenAnalysisDate > $filterDate"
    return $output
}

# =====================================
# Add the Tabel the Jira US number
# =====================================
function Add-JiraUS-To-Table{
    param(
        [String]$rowId,
        [String]$jiraId,
        [PSCustomObject]$inputTable
    )

    $rowFromTable = $inputTable | Where-Object { $_.uid -eq $rowId}
    if ($rowFromTable){
       $rowFromTable.jiraUS = $jiraId
    }
    return $rowFromTable
}

# =====================================
# Clean up a String
# =====================================
function Format-Remark {
    param (
        [string]$String,
        [int]$MaxLength = 200
    )
    
    # Replace carriage returns and newlines by a space
    $cleanString = $String -replace '[\r\n]+', ' '

    # Trim string to max length
    if ($cleanString.Length -gt $MaxLength) {
        return $cleanString.Substring(0, $MaxLength)
    }
    return $cleanString
}

# =====================================
# Rename Severity (practical for sorting later on)
# =====================================
function Rename-Sev {
    param (
        [string]$String
    )
    $severityMap = @{ 
        'CRITICAL'     = '1-CRITICAL'
        'HIGH'         = '2-HIGH'
        'MEDIUM'       = '3-MEDIUM'
        'LOW'          = '4-LOW'
        'INFORMATION'  = '5-INFORMATION'
    }
    return $severityMap[$String]
}

# =====================================
# Get content from input file (name/value pair)
# =====================================
function Get-Content-From-File {
    param (
        [String]$path
    )
    try {
        $file_content = Get-Content ($path)
        $file_content = $file_content -join [Environment]::NewLine
        return ConvertFrom-StringData($file_content)
    }
    catch {
        Write-Log "ERROR: Cannot open or find file: $path"
        Write-Log $_.Exception.Message
        throw    
    }
}

# =====================================
# Get info from control file (json)
# =====================================
function Get-Control-Info{
    param(
        [String]$path,
        [String]$searchId,
        [String]$paramCol        
    )
    try {
        $fileContent = Get-Content -Path ($path) -Raw
        $jsonContent = $fileContent | ConvertFrom-Json

        $rowId = $jsonContent | Where-Object { $_.App -eq $searchId}

        if($rowId){
            return $rowId.$paramCol
        }
        else{
            Write-Log "ERROR: Entry for App = $searchId not found in $path. Check the controle file."
            return "No Value"
        }
    }
    catch {
        Write-Log "ERROR: Something went wrong with reading $path"
        Write-Log $_.Exception.Message
    }
}

# =====================================
# Log function
# =====================================
function Write-Log {
    param (
        [String]$Message
    )
    
    $timeStampLogFile = $global:startDateTime -replace '[ :]','_'
    $caller = (Get-PSCallStack)[1].FunctionName
    $logLine = "[$((Get-Date).ToString("yyyy-MM-dd HH:mm:ss"))] Function: $caller > $Message"

    Write-Host $logLine
    $logFile = Join-Path -Path $rootPath -ChildPath "log/SIG-2-Jira_$timeStampLogFile.log"
    Add-Content -Path $logFile -Value $logLine
}
# =====================================
# Log function for a Block (to improve readability of the log file)
# =====================================
function Write-Log-Block {
    param (
        [String]$Message
    )
    Write-Log "---"
    Write-Log "--- $Message"
    Write-Log "---"
}
# =====================================
# Count number of lines with an Error
# =====================================
function Get-Error-Count{
    $timeStampLogFile = $global:startDateTime -replace '[ :]','_'
    $logFile = Join-Path -Path $rootPath -ChildPath "log/SIG-2-Jira_$timeStampLogFile.log"
    return Get-Content $logFile | Select-String -Pattern "error" -CaseSensitive:$false | Measure-Object | Select-Object -ExpandProperty Count
}

# =====================================
# Debug function
# =====================================
function Write-Object {
    param (
        [String]$customObjectName,
        [Object]$customObject
    )
    $logFile = Join-Path -Path $rootPath -ChildPath "log/$customObjectName.txt"
    Set-Content -Path $logFile -Value $customObject
}

# =====================================
# Archive the logs (cleanup)
# =====================================
function Move-Logs-To-Archive{

    $logFolder = Join-Path -Path $rootPath -ChildPath "log"
    $archiveFolder = Join-Path -Path $rootPath -ChildPath "log/archive"

    try {
        if(-not (Test-Path $archiveFolder)){
            New-Item -Path $archiveFolder -ItemType Directory | Out-Null
        }

        $logFiles = Get-ChildItem -Path $logFolder -Filter *.log -File

        foreach ($file in $logFiles){
            $destination = Join-Path $archiveFolder $file.Name
            Move-Item -Path $file.FullName -Destination $destination
        }
    }
    catch {
        Write-Log $_.Exception.Message
    }
}
