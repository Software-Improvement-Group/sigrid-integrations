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
# Convert input table into HTML tabel
# =====================================
function EmailTable_HTML {
    param (
    [PSCustomObject[]]$Data
    )

    # convert the psCustomObject to HTML
    $htmlTable = $Data | ConvertTo-Html -Fragment

    # Adjust the HTML styling
    $htmlTable = $htmlTable -replace '<th>app</th>', '<th style="background-color:#D6DCE4; text-align: left;">Applicatie</th>'
    #$htmlTable = $htmlTable -replace '<tr><td>', '<tr><td style="text-align: left;">'

    foreach ($row in $Data){
        $htmlTable = $htmlTable -replace "<td>$($row.App)</td>", "<td style='text-align: left; width: 400px;'><a href='https://sigrid-says.com/xxx/$($row.App)/-/security'>$($row.App)</a></td>"
    }

    $htmlTable = $htmlTable -replace '<th>JiraProject</th>', '<th style="background-color:#9BC2E6;">JiraProject</th>'
    $htmlTable = $htmlTable -replace '<th>GetSIGFindings</th>', '<th style="background-color:#9BC2E6;">GetSIGFindings</th>'
    $htmlTable = $htmlTable -replace '<th>AllowCreateJiraUS</th>', '<th style="background-color:#9BC2E6;">AllowCreateJiraUS</th>'
    $htmlTable = $htmlTable -replace '<th>SevDepth</th>', '<th style="background-color:#9BC2E6;">SevDepth</th>'
    $htmlTable = $htmlTable -replace '<th>SIGCount</th>', '<th style="background-color:#FFD966;">SIGCount</th>'
    $htmlTable = $htmlTable -replace '<th>JiraExist</th>', '<th style="background-color:#ED7D31;">JiraExist</th>'
    $htmlTable = $htmlTable -replace '<th>JiraMissing</th>', '<th style="background-color:#ED7D31;">JiraMissing</th>'
    $htmlTable = $htmlTable -replace '<th>JiraAdded</th>', '<th style="background-color:#ED7D31;">JiraAdded</th>'

    # add styling to the $htmlTable
    $htmlContent = @"
    <html>
    <head>
        <style>
            table {
                border-collapse: collapse;
                margin: 2px 0;
                font-family: Verdana, sans-serif;
                font-size: 11px;
                text-align: left;
                border: 1px solid black;
            }
            th, td {
                padding: 2px 2px;
                border: 1px solid #ddd;
                text-align: center;
                width: 150px;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
        </style>
    </head>
    <body>
        $customHeaders
        $htmlTable
        </table>
    </body>
    </html>
"@

    return $htmlContent

}

# =====================================
# Make email report (for the admin of this tool)
# =====================================
function Send-Report{
    param(
        [String]$emailSMTP,
        [String]$emailTo,
        [String]$emailFrom,
        [String]$reportData,
        [String]$errorCount
    )

    $timeStampLogFile = $global:startDateTime -replace '[ :]','_'
    $logFile = Join-Path -Path $rootPath -ChildPath "/log/SIG-2-Jira_$timeStampLogFile.log"

    $emailSubject = "JIRA user stories for Sigrid security findings"
    $emailBody = "Hi,<br /><br />The table below lists the systems for which JIRA stories have been created based on Sigrid security findings.<br /><br />"
    $emailBody += "$reportData<br /><br />"
    $emailBody += "This process encountered $errorCount errors. Please check the attached logs.<br /><br />"
    $emailBody += "The remaining XXX systems have been excluded from this process.<br /><br />"
    $emailBody += "This email was sent automatically."
    $emailBody = "<html><body style='font-family: Verdana, sans-serif;font-size: 11px;'>" + $emailBody + "</body></html>"
    
    Send-MailMessage -SmtpServer $emailSMTP -Port 25 -To $emailTo.split(',') -From $emailFrom -Subject $emailSubject -Body $emailBody -BodyAsHtml -Attachments $logFile
}