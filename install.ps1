<#
.SYNOPSIS
  Install ASR CLI for the current user.

.DESCRIPTION
  - Creates an isolated virtual environment
  - Installs this project in editable mode
  - Creates lightweight shims in a user bin directory
  - Optionally adds that bin directory to the user PATH

.PARAMETER Prefix
  Install prefix. Shims are placed in <Prefix>\bin.
  Default: $env:LOCALAPPDATA\asr

.PARAMETER VenvDir
  Virtual environment directory.
  Default: <Prefix>\venv

.PARAMETER NoModifyPath
  Do not modify user PATH.

.PARAMETER DryRun
  Print actions without making changes.
#>

[CmdletBinding()]
param(
  [string]$Prefix = (Join-Path $env:LOCALAPPDATA "asr"),
  [string]$VenvDir = "",
  [switch]$NoModifyPath,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($VenvDir)) {
  $VenvDir = (Join-Path $Prefix "venv")
}

$ScriptDir = $PSScriptRoot
$BinDir = Join-Path $Prefix "bin"

function Invoke-Step([string]$Label, [scriptblock]$Block) {
  if ($DryRun) {
    Write-Host "dry-run: $Label"
    return
  }
  & $Block
}

function Get-VenvPython {
  $py = Join-Path $VenvDir "Scripts\\python.exe"
  if (Test-Path $py) { return $py }
  throw "venv python not found at $py"
}

function Ensure-Venv {
  if (Test-Path (Join-Path $VenvDir "Scripts\\python.exe")) { return }

  if (Get-Command uv -ErrorAction SilentlyContinue) {
    Invoke-Step "uv venv $VenvDir" { uv venv $VenvDir | Out-Host }
    return
  }

  $py = (Get-Command python -ErrorAction SilentlyContinue)?.Source
  if (-not $py) { $py = (Get-Command python3 -ErrorAction SilentlyContinue)?.Source }
  if (-not $py) { throw "python/python3 not found (install Python or uv)" }

  Invoke-Step "$py -m venv $VenvDir" { & $py -m venv $VenvDir }
}

function Install-Project {
  $vpy = Get-VenvPython
  if (-not $DryRun) {
    try {
      & $vpy -c "import pip" | Out-Null
    } catch {
      & $vpy -m ensurepip --upgrade | Out-Host
    }
  }
  Invoke-Step "$vpy -m pip install --upgrade pip" { & $vpy -m pip install --upgrade pip | Out-Host }
  Invoke-Step "$vpy -m pip install -e $ScriptDir" { & $vpy -m pip install -e $ScriptDir | Out-Host }
}

function Write-Shim([string]$Name) {
  $cmdPath = Join-Path $BinDir "$Name.cmd"
  $ps1Path = Join-Path $BinDir "$Name.ps1"
  $exePath = Join-Path $VenvDir "Scripts\\$Name.exe"

  if (-not $DryRun -and -not (Test-Path $exePath)) {
    throw "expected CLI at $exePath (install may have failed)"
  }

  Invoke-Step "Create shim $cmdPath" {
    @"
@echo off
\"$exePath\" %*
"@ | Set-Content -Path $cmdPath -Encoding ASCII
  }

  Invoke-Step "Create shim $ps1Path" {
    @"
& \"$exePath\" @args
"@ | Set-Content -Path $ps1Path -Encoding UTF8
  }
}

function Ensure-Path {
  if ($NoModifyPath) { return }

  $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
  if (-not $userPath) { $userPath = "" }

  $parts = $userPath -split ';' | Where-Object { $_ -and $_.Trim() -ne "" }
  if ($parts -contains $BinDir) {
    return
  }

  $newPath = if ($userPath.Trim().Length -eq 0) { $BinDir } else { "$userPath;$BinDir" }
  Invoke-Step "Add $BinDir to user PATH" {
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    $env:Path = "$env:Path;$BinDir"
  }
}

function Migrate-Data {
  # Safely migrate from ~/.skills/ to ~/.oasr/
  # Only moves oasr-managed files: manifests/, registry.toml, config.toml
  
  $oldDir = Join-Path $env:USERPROFILE ".skills"
  $newDir = Join-Path $env:USERPROFILE ".oasr"
  
  # If new directory already exists and has data, skip migration
  if ((Test-Path $newDir) -and (Test-Path (Join-Path $newDir "registry.toml"))) {
    return
  }
  
  # If old directory doesn't exist, nothing to migrate
  if (-not (Test-Path $oldDir)) {
    return
  }
  
  # Check if there's anything to migrate
  $hasOasrData = $false
  if (Test-Path (Join-Path $oldDir "manifests")) { $hasOasrData = $true }
  if (Test-Path (Join-Path $oldDir "registry.toml")) { $hasOasrData = $true }
  if (Test-Path (Join-Path $oldDir "config.toml")) { $hasOasrData = $true }
  
  if (-not $hasOasrData) {
    return
  }
  
  Write-Host "Migrating oasr data from ~/.skills/ to ~/.oasr/ ..."
  
  if ($DryRun) {
    Write-Host "dry-run: would migrate oasr files from $oldDir to $newDir"
    return
  }
  
  # Create new directory
  New-Item -ItemType Directory -Force -Path $newDir | Out-Null
  
  # Move only oasr-managed files
  $manifestsPath = Join-Path $oldDir "manifests"
  if (Test-Path $manifestsPath) {
    Write-Host "  Moving manifests/ ..."
    Move-Item -Path $manifestsPath -Destination $newDir -Force
  }
  
  $registryPath = Join-Path $oldDir "registry.toml"
  if (Test-Path $registryPath) {
    Write-Host "  Moving registry.toml ..."
    Move-Item -Path $registryPath -Destination $newDir -Force
  }
  
  $configPath = Join-Path $oldDir "config.toml"
  if (Test-Path $configPath) {
    Write-Host "  Moving config.toml ..."
    Move-Item -Path $configPath -Destination $newDir -Force
  }
  
  Write-Host "  ✓ Migration complete"
  Write-Host "  Note: ~/.skills/ directory preserved (may contain other files)"
}

Write-Host "Installing ASR from: $ScriptDir"
Write-Host "Venv: $VenvDir"
Write-Host "Shims: $BinDir"

Invoke-Step "Create directories" { New-Item -ItemType Directory -Force -Path $BinDir | Out-Null }
Ensure-Venv
Install-Project
Write-Shim -Name "asr"
Write-Shim -Name "skills"
Migrate-Data
Ensure-Path

Write-Host ""
Write-Host "Done."
Write-Host "Try: asr --version"
