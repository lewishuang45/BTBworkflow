$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (-not (Test-Path '.env')) {
    throw 'Missing .env file in current folder.'
}

Get-Content '.env' -Encoding UTF8 | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
    $parts = $_.Split('=', 2)
    [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
}

python run_workflow.py --stage report

if (-not (Test-Path 'final_output.json')) {
    throw 'Report stage did not produce final_output.json.'
}

try {
    python run_workflow.py --stage image
}
catch {
    Write-Warning 'Image stage did not finish. Report JSON is already saved and you can rerun only the image stage with: python run_workflow.py --stage image'
    throw
}
