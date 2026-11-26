#Requires -Version 5.1
<#
.SYNOPSIS
    Detektor Arbitrary File Read (GET /api/storage) na dzialajacej aplikacji.
.DESCRIPTION
    Prosi o plik ../secret.txt (poza katalogiem instrukcji). Jesli API zwroci
    jego tresc z markerem FLAG -> podatnosc wykryta. Nie zmienia stanu (tylko odczyt).
    Kod wyjscia: 1 = wykryto, 0 = czysto, 2 = API nie odpowiada.
.EXAMPLE
    pwsh ./scripts/scan-fileio.ps1
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

$r = Invoke-Api -BaseUrl $BaseUrl -Method Get `
    -Path "/api/storage?name=$([uri]::EscapeDataString('../secret.txt'))" -TimeoutSec $TimeoutSec
$detected = [bool]($r.Ok -and $r.Data -and $r.Data.content -match 'FLAG\{')
$proof = if ($detected) {
    "odczyt pliku spoza katalogu (../secret.txt): $($r.Data.content.Trim())"
}
else { "odczyt zablokowany (HTTP $($r.Status))" }

Write-Finding -Name 'Arbitrary File Read' -Endpoint 'GET /api/storage' -Detected $detected -Proof $proof
if ($detected) { exit 1 } else { exit 0 }
