<#
.SYNOPSIS
    Instaluje wybrane skille i/lub agentów z repozytorium flowkit.
.PARAMETER SkillName
    Nazwa skilla do zainstalowania (np. client-pt-prd-writer). Jeśli nie podano ani SkillName, ani AgentName, wyświetla listę dostępnych zasobów.
.PARAMETER AgentName
    Nazwa agenta do zainstalowania (np. agent-3x3). Użyj "all" aby zainstalować wszystkich agentów.
.PARAMETER TargetPath
    Katalog docelowy dla skilli. Domyślnie ~/.claude/skills.
.PARAMETER AgentTargetPath
    Katalog docelowy dla agentów. Domyślnie ~/.claude/agents (globalni agenci Claude Code).
.EXAMPLE
    # Instalacja skilla
    .\scripts\install.ps1 -SkillName client-pt-prd-writer
.EXAMPLE
    # Instalacja głównego orkiestratora + wszystkich subagentów
    .\scripts\install.ps1 -AgentName all
.EXAMPLE
    # Instalacja konkretnego agenta
    .\scripts\install.ps1 -AgentName agent-3x3
.EXAMPLE
    # Instalacja skilla i agenta jednocześnie
    .\scripts\install.ps1 -SkillName devops-incident-postmortem -AgentName agent-3x3
.EXAMPLE
    # Instalacja lokalna (w projekcie zamiast globalnie)
    .\scripts\install.ps1 -AgentName all -AgentTargetPath ./.claude/agents
#>
[CmdletBinding()]
param(
    [string]$SkillName,
    [string]$AgentName,
    [string]$TargetPath,
    [string]$AgentTargetPath
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SkillsDir = Join-Path $RepoRoot "skills"
$AgentsDir = Join-Path $RepoRoot "agents"

# Domyślne ścieżki docelowe
if (-not $TargetPath) {
    $TargetDir = Join-Path $HOME ".claude\skills"
} else {
    $TargetDir = (Resolve-Path -Path $TargetPath -ErrorAction SilentlyContinue)
    if (-not $TargetDir) { $TargetDir = $TargetPath }
}

if (-not $AgentTargetPath) {
    $AgentTargetDir = Join-Path $HOME ".claude\agents"
} else {
    $AgentTargetDir = (Resolve-Path -Path $AgentTargetPath -ErrorAction SilentlyContinue)
    if (-not $AgentTargetDir) { $AgentTargetDir = $AgentTargetPath }
}

$AvailableSkills = Get-ChildItem -Path $SkillsDir -Directory | Where-Object { $_.Name -notlike "_*" } | Select-Object -ExpandProperty Name
$AvailableAgents = Get-ChildItem -Path $AgentsDir -Filter "*_agent.md" | ForEach-Object {
    $_.BaseName -replace "_agent$", ""
}

# Jeśli nie podano żadnego argumentu — wyświetl listę i zapytaj
if (-not $SkillName -and -not $AgentName) {
    Write-Host ""
    Write-Host "=== FlowKit Installer ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Dostępne SKILLE:" -ForegroundColor Yellow
    foreach ($s in $AvailableSkills) { Write-Host "  - $s" }
    Write-Host ""
    Write-Host "Dostępne AGENTY:" -ForegroundColor Yellow
    foreach ($a in $AvailableAgents) { Write-Host "  - $a" }
    Write-Host "  (użyj 'all' aby zainstalować wszystkich agentów)" -ForegroundColor Gray
    Write-Host ""
    $choice = Read-Host "Co zainstalować? Wpisz nazwę skilla lub agenta (lub zostaw puste aby anulować)"
    if (-not $choice) { exit 0 }
    if ($AvailableSkills -contains $choice) { $SkillName = $choice }
    elseif ($AvailableAgents -contains $choice -or $choice -eq "all") { $AgentName = $choice }
    else {
        Write-Error "Nieznana nazwa: '$choice'. Sprawdź dostępne skille i agenty powyżej."
        exit 1
    }
}

# --- Instalacja skilla ---
if ($SkillName) {
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
        if (-not (Test-Path $DestinationPath)) {
            New-Item -ItemType Directory -Force -Path $DestinationPath -ErrorAction Stop | Out-Null
        }
        Copy-Item -Path (Join-Path $SourcePath "*") -Destination $DestinationPath -Recurse -Force -ErrorAction Stop
        Write-Host "✓ Skill '$SkillName' zainstalowany w: $DestinationPath" -ForegroundColor Green
    } catch {
        Write-Error "Błąd podczas instalacji skilla: $_"
        exit 1
    }
}

# --- Instalacja agenta/agentów ---
function Install-Agent {
    param([string]$Name)
    $SourceFile = Join-Path $AgentsDir "${Name}_agent.md"
    if (-not (Test-Path $SourceFile)) {
        Write-Error "Agent '$Name' nie istnieje (szukano: $SourceFile)"
        return $false
    }
    try {
        if (-not (Test-Path $AgentTargetDir)) {
            New-Item -ItemType Directory -Force -Path $AgentTargetDir -ErrorAction Stop | Out-Null
        }
        $DestFile = Join-Path $AgentTargetDir "${Name}_agent.md"
        Copy-Item -Path $SourceFile -Destination $DestFile -Force -ErrorAction Stop
        Write-Host "  ✓ $Name" -ForegroundColor Green
        return $true
    } catch {
        Write-Error "Błąd podczas instalacji agenta '$Name': $_"
        return $false
    }
}

if ($AgentName) {
    Write-Host ""
    Write-Host "Instalacja agentów w: $AgentTargetDir" -ForegroundColor Cyan

    if ($AgentName -eq "all") {
        Write-Host "Instalowanie wszystkich agentów..." -ForegroundColor Yellow
        foreach ($a in $AvailableAgents) {
            Install-Agent -Name $a | Out-Null
        }
    } else {
        if (-not ($AvailableAgents -contains $AgentName)) {
            Write-Error "Agent '$AgentName' nie istnieje. Dostępne: $($AvailableAgents -join ', ')"
            exit 1
        }
        Install-Agent -Name $AgentName | Out-Null
    }
    Write-Host ""
    Write-Host "Claude Code automatycznie wykryje agentów z ~/.claude/agents/" -ForegroundColor Gray
    Write-Host "Restart Claude Code może być wymagany do odświeżenia listy agentów." -ForegroundColor Gray
}
