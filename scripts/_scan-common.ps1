<#
    Wspolne funkcje dla detektorow scan-*.ps1.
    Dot-source: . (Join-Path $PSScriptRoot '_scan-common.ps1')
    Nie uruchamiaj bezposrednio.
#>

function Invoke-Api {
    param(
        [Parameter(Mandatory)][string]$BaseUrl,
        [Parameter(Mandatory)][string]$Method,
        [Parameter(Mandatory)][string]$Path,
        [hashtable]$Body,
        [int]$TimeoutSec = 10
    )
    $uri = "$BaseUrl$Path"
    try {
        if ($PSBoundParameters.ContainsKey('Body')) {
            $json = $Body | ConvertTo-Json -Compress
            $resp = Invoke-RestMethod -Uri $uri -Method $Method -ContentType 'application/json' `
                -Body $json -TimeoutSec $TimeoutSec
        }
        else {
            $resp = Invoke-RestMethod -Uri $uri -Method $Method -TimeoutSec $TimeoutSec
        }
        return [pscustomobject]@{ Ok = $true; Status = 200; Data = $resp }
    }
    catch {
        $status = 0
        if ($_.Exception.PSObject.Properties['Response'] -and $_.Exception.Response) {
            try { $status = [int]$_.Exception.Response.StatusCode } catch { }
        }
        return [pscustomobject]@{ Ok = $false; Status = $status; Data = $null }
    }
}

function Test-ApiAlive {
    param(
        [Parameter(Mandatory)][string]$BaseUrl,
        [int]$TimeoutSec = 10
    )
    return (Invoke-Api -BaseUrl $BaseUrl -Method Get -Path '/api/modules' -TimeoutSec $TimeoutSec).Ok
}

function Write-Finding {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Endpoint,
        [Parameter(Mandatory)][bool]$Detected,
        [Parameter(Mandatory)][string]$Proof
    )
    if ($Detected) {
        Write-Host "[WYKRYTO] $Name  ($Endpoint)" -ForegroundColor Red
    }
    else {
        Write-Host "[  ok   ] $Name  ($Endpoint)" -ForegroundColor Green
    }
    Write-Host "          $Proof" -ForegroundColor DarkGray
}
