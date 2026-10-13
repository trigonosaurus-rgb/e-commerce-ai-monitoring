# Registers a Windows scheduled task that runs due price checks without the web server.
#
#   powershell -ExecutionPolicy Bypass -File scripts\schedule-checks.ps1           # register
#   powershell -ExecutionPolicy Bypass -File scripts\schedule-checks.ps1 -Remove   # remove
#
# The task wakes every 2 hours while the PC is on; a run missed while the PC was off or
# asleep happens right after it starts. Pages are only downloaded when they are due
# (CHECK_INTERVAL_HOURS), so most runs finish in a second without any network calls.
# Log: data\logs\check-due.log

param([switch]$Remove)

$TaskName = "Rivalscope price checks"

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed '$TaskName'."
    exit
}

$Project = Split-Path -Parent $PSScriptRoot
# uvw = uv without a console window, so nothing flashes on screen
$Uvw = Join-Path (Split-Path -Parent (Get-Command uv).Source) "uvw.exe"

$Action = New-ScheduledTaskAction -Execute $Uvw `
    -Argument "run --project `"$Project`" python -m backend.cli check-due" `
    -WorkingDirectory $Project
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddHours(8) `
    -RepetitionInterval (New-TimeSpan -Hours 2)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Description "Due price checks for Rivalscope ($Project)" -Force | Out-Null
Write-Host "Registered '$TaskName': every 2 hours while the PC is on. Log: data\logs\check-due.log"
