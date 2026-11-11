<#
.SYNOPSIS
    Instaluje wybrany skill z repozytorium flowkit do katalogu Claude Code.
.PARAMETER SkillName
    Nazwa skilla (np. client-pt-prd-writer). Jeśli nie podano, wyświetla listę dostępnych skilli.
.PARAMETER TargetPath
    Katalog docelowy. Domyślnie ~/.claude/skills (instalacja globalna). Można podać np. ./.claude/skills.
.EXAMPLE
    .\scripts\install.ps1 -SkillName client-pt-prd-writer
.EXAMPLE
    .\scripts\install.ps1 -SkillName client-pt-prd-writer -TargetPath ./.claude/skills
#>
[CmdletBinding()]
param(
    [string]$SkillName,
    [string]$TargetPath
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SkillsDir = Join-Path $RepoRoot "skills"
if (-not $TargetPath) {
    $TargetDir = Join-Path $HOME ".claude\skills"
} else {
    $TargetDir = (Resolve-Path -Path $TargetPath -ErrorAction SilentlyContinue)
    if (-not $TargetDir) { $TargetDir = $TargetPath }
}

$AvailableSkills = Get-ChildItem -Path $SkillsDir -Directory | Where-Object { $_.Name -notlike "_*" } | Select-Object -ExpandProperty Name

if (-not $SkillName) {
    Write-Host "Dostępne skille w repozytorium:" -ForegroundColor Cyan
    foreach ($s in $AvailableSkills) {
        Write-Host "  - $s"
    }
    Write-Host ""
    $SkillName = Read-Host "Podaj nazwę skilla do zainstalowania"
}

if (-not ($AvailableSkills -contains $SkillName)) {
    Write-Error "Skill '$SkillName' nie istnieje w folderze skills/."
    exit 1
}

$SourcePath = Join-Path $SkillsDir $SkillName
$DestinationPath = Join-Path $TargetDir $SkillName

try {
    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Force -Path $TargetDir -ErrorAction Stop | Out-Null
    }

    Copy-Item -Path $SourcePath -Destination $DestinationPath -Recurse -Force -ErrorAction Stop
    Write-Host "Pomyślnie zainstalowano skill '$SkillName' w: $DestinationPath" -ForegroundColor Green
    Write-Host "Claude Code będzie miał teraz automatyczny dostęp do tego skilla." -ForegroundColor Gray
} catch {
    Write-Error "Błąd podczas instalacji: $_"
    exit 1
}

