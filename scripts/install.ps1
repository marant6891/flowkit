<#
.SYNOPSIS
    Instaluje wybrany skill z repozytorium flowkit do katalogu Claude Code (~/.claude/skills).
.PARAMETER SkillName
    Nazwa skilla (np. client-pt-prd-writer). Jeśli nie podano, wyświetla listę dostępnych skilli.
.EXAMPLE
    .\scripts\install.ps1 -SkillName client-pt-prd-writer
#>
[CmdletBinding()]
param(
    [string]$SkillName
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SkillsDir = Join-Path $RepoRoot "skills"
$TargetDir = Join-Path $HOME ".claude\skills"

$AvailableSkills = Get-ChildItem -Path $SkillsDir -Directory | Where-Object { $_.Name -notlike "_*" } | Select-Object -ExpandProperty Name

if (-not $SkillName) {
    Write-Host "Dostepne skille w repozytorium:" -ForegroundColor Cyan
    foreach ($s in $AvailableSkills) {
        Write-Host "  - $s"
    }
    Write-Host ""
    $SkillName = Read-Host "Podaj nazwe skilla do zainstalowania"
}

if (-not ($AvailableSkills -contains $SkillName)) {
    Write-Error "Skill '$SkillName' nie istnieje w folderze skills/."
    exit 1
}

$SourcePath = Join-Path $SkillsDir $SkillName
$DestinationPath = Join-Path $TargetDir $SkillName

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
}

Copy-Item -Path $SourcePath -Destination $DestinationPath -Recurse -Force
Write-Host "Pomyslnie zainstalowano skill '$SkillName' w: $DestinationPath" -ForegroundColor Green
Write-Host "Claude Code bedzie mial teraz automatyczny dostep do tego skilla." -ForegroundColor Gray
