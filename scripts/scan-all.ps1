#Requires -Version 5.1
<#
.SYNOPSIS
    Odpala wszystkie detektory scan-*.ps1 z tego folderu i zbiera wynik.
.DESCRIPTION
    Uruchamia po kolei kazdy scan-*.ps1 (oprocz samego siebie). Kazdy zglasza
    swoja podatnosc [WYKRYTO] lub [ok]. Na koncu zbiorcze podsumowanie.
    Kod wyjscia: 1 = wykryto co najmniej jedna, 0 = czysto, 2 = API nie odpowiada.

    Uwaga: NIE uruchamia check-nosqli.ps1 - to osobne narzedzie regresyjne,
    ktore przelacza warianty w .env i przebudowuje kontener.
.EXAMPLE
    pwsh ./scripts/scan-all.ps1
#>
[CmdletBinding()]
param(
    [string]$BaseUrl = 'http://localhost:8000',
    [int]$TimeoutSec = 10
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '_scan-common.ps1')

Write-Host "== Skan wszystkich podatnosci :: $BaseUrl ==" -ForegroundColor Cyan

if (-not (Test-ApiAlive -BaseUrl $BaseUrl -TimeoutSec $TimeoutSec)) {
    Write-Host "API nie odpowiada pod $BaseUrl - uruchom: docker compose up -d" -ForegroundColor Red
    exit 2
}

$self = $MyInvocation.MyCommand.Name
$detectors = Get-ChildItem -Path $PSScriptRoot -Filter 'scan-*.ps1' |
    Where-Object { $_.Name -ne $self } | Sort-Object Name

if (-not $detectors) {
    Write-Host 'Brak detektorow scan-*.ps1 w folderze.' -ForegroundColor Yellow
    exit 0
}

$detected = @()
foreach ($d in $detectors) {
    Write-Host ''
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $d.FullName -BaseUrl $BaseUrl -TimeoutSec $TimeoutSec
    if ($LASTEXITCODE -eq 1) { $detected += ($d.BaseName -replace '^scan-', '') }
}

Write-Host ''
Write-Host '== Podsumowanie zbiorcze ==' -ForegroundColor Cyan
if ($detected.Count -eq 0) {
    Write-Host 'Nie wykryto zadnych podatnosci (wszystkie moduly secure).' -ForegroundColor Green
    exit 0
}
Write-Host "Wykryto podatnosci: $($detected.Count) ($($detected -join ', '))" -ForegroundColor Red
exit 1
