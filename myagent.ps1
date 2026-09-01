#!/usr/bin/env pwsh
# MyAgent Launcher Script
# Usage: .\myagent.ps1 main

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MyAgentExe = Join-Path $ScriptDir "venv\Scripts\myagent.exe"

if (Test-Path $MyAgentExe) {
    & $MyAgentExe @args
} else {
    Write-Host "Error: MyAgent not found. Please run: pip install -e ." -ForegroundColor Red
    exit 1
}
