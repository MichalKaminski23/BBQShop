#Requires -Version 5.1
<#
.SYNOPSIS
    Detektor NoSQL Injection (POST /api/login) na dzialajacej aplikacji.
.DESCRIPTION
    Wysyla operator {"$ne": null} zamiast hasla. Jesli API loguje jako admin
    bez hasla -> podatnosc wykryta. Nie zmienia stanu aplikacji.
    Kod wyjscia: 1 = wykryto, 0 = czysto, 2 = API nie odpowiada.
.EXAMPLE
    pwsh ./scripts/scan-nosqli.ps1
#>
[CmdletBinding()]
param(
    [string]$BaseUrl = 'http://localhost:8000',
    [int]$TimeoutSec = 10
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '_scan-common.ps1')

if (-not (Test-ApiAlive -BaseUrl $BaseUrl -TimeoutSec $TimeoutSec)) {
    Write-Host "API nie odpowiada pod $BaseUrl (uruchom: docker compose up -d)." -ForegroundColor Red
    exit 2
}

$r = Invoke-Api -BaseUrl $BaseUrl -Method Post -Path '/api/login' `
    -Body @{ username = 'admin'; password = @{ '$ne' = $null } } -TimeoutSec $TimeoutSec
$detected = [bool]($r.Ok -and $r.Data -and $r.Data.role)
$proof = if ($detected) {
    "logowanie BEZ hasla jako '$($r.Data.username)' (rola=$($r.Data.role))"
}
else { "atak odrzucony (HTTP $($r.Status))" }

Write-Finding -Name 'NoSQL Injection' -Endpoint 'POST /api/login' -Detected $detected -Proof $proof
if ($detected) { exit 1 } else { exit 0 }
