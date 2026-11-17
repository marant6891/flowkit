<#
.SYNOPSIS
    Bezpieczny instalator skilli i agentów z repozytorium FlowKit.
.PARAMETER SkillName
    Nazwa skilla do zainstalowania (np. client-pt-prd-writer).
.PARAMETER AgentName
    Nazwa agenta do zainstalowania (np. agent-3x3 lub 'all').
.PARAMETER Platform
    Docelowa platforma: 'claude' (domyślnie, ~/.claude/) lub 'vscode' (.github/agents/ w workspace).
.PARAMETER TargetPath
    Katalog docelowy dla skilli.
.PARAMETER AgentTargetPath
    Katalog docelowy dla agentów.
.PARAMETER DryRun
    Tryb symulacji: wyświetla planowane operacje bez zapisu na dysku.
.PARAMETER Force
    Wymusza nadpisanie istniejących plików bez pytania.
.PARAMETER Uninstall
    Usuwa wskazany skill lub agenta z katalogu docelowego.
.EXAMPLE
    .\scripts\install.ps1 -SkillName client-pt-prd-writer -DryRun
.EXAMPLE
    .\scripts\install.ps1 -AgentName all -Platform claude -Force
.EXAMPLE
    .\scripts\install.ps1 -AgentName all -Platform vscode -AgentTargetPath ./.github/agents
#>
[CmdletBinding()]
param(
    [string]$SkillName,
    [string]$AgentName,
    [ValidateSet('claude', 'vscode')]
    [string]$Platform = 'claude',
    [string]$TargetPath,
    [string]$AgentTargetPath,
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Uninstall
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SkillsDir = Join-Path $RepoRoot "skills"
$AgentsDir = Join-Path $RepoRoot "agents"

# Określenie domyślnych katalogów docelowych zależnie od platformy
if (-not $TargetPath) {
    if ($Platform -eq 'claude') {
        $TargetDir = Join-Path $HOME ".claude\skills"
    } else {
        $TargetDir = Join-Path $RepoRoot ".github\skills"
    }
} else {
    $TargetDir = (Resolve-Path -Path $TargetPath -ErrorAction SilentlyContinue)
    if (-not $TargetDir) { $TargetDir = $TargetPath }
}

if (-not $AgentTargetPath) {
    if ($Platform -eq 'claude') {
        $AgentTargetDir = Join-Path $HOME ".claude\agents"
    } else {
        $AgentTargetDir = Join-Path $RepoRoot ".github\agents"
    }
} else {
    $AgentTargetDir = (Resolve-Path -Path $AgentTargetPath -ErrorAction SilentlyContinue)
    if (-not $AgentTargetDir) { $AgentTargetDir = $AgentTargetPath }
}

# Whitelist dostępnych zasobów (zabezpieczenie przed path traversal)
$AvailableSkills = Get-ChildItem -Path $SkillsDir -Directory | Where-Object { $_.Name -notlike "_*" } | Select-Object -ExpandProperty Name
$AvailableAgents = @(
    "agent-3x3",
    "agent-3x3-analyzer",
    "agent-3x3-verifier",
    "agent-3x3-planner",
    "agent-3x3-implementer",
    "agent-3x3-devops",
    "agent-3x3-pm"
)

if (-not $SkillName -and -not $AgentName) {
    Write-Host ""
    Write-Host "=== FlowKit Safe Installer (Platform: $Platform) ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Dostępne SKILLE:" -ForegroundColor Yellow
    foreach ($s in $AvailableSkills) { Write-Host "  - $s" }
    Write-Host ""
    Write-Host "Dostępne AGENTY:" -ForegroundColor Yellow
    foreach ($a in $AvailableAgents) { Write-Host "  - $a" }
    Write-Host "  (użyj 'all' aby wybrać wszystkich agentów)" -ForegroundColor Gray
    Write-Host ""
    $choice = Read-Host "Wpisz nazwę skilla lub agenta do operacji"
    if (-not $choice) { exit 0 }
    if ($AvailableSkills -contains $choice) { $SkillName = $choice }
    elseif ($AvailableAgents -contains $choice -or $choice -eq "all") { $AgentName = $choice }
    else {
        Write-Error "Nieznana nazwa: '$choice'."
        exit 1
    }
}

# --- OBSŁUGA SKILLA ---
if ($SkillName) {
    if (-not ($AvailableSkills -contains $SkillName)) {
        Write-Error "Skill '$SkillName' nie istnieje na liście dozwolonych skilli."
        exit 1
    }
    $DestPath = Join-Path $TargetDir $SkillName

    if ($Uninstall) {
        Write-Host "[UNINSTALL] Usuwanie skilla '$SkillName' z: $DestPath" -ForegroundColor Yellow
        if (Test-Path $DestPath) {
            if ($DryRun) {
                Write-Host "  [DRY-RUN] Usunięto by katalog $DestPath" -ForegroundColor Gray
            } else {
                Remove-Item -Path $DestPath -Recurse -Force
                Write-Host "  ✓ Skill odinstalowany pomyślnie" -ForegroundColor Green
            }
        } else {
            Write-Host "  Skill nie był zainstalowany w tej lokalizacji." -ForegroundColor Gray
        }
    } else {
        $SrcPath = Join-Path $SkillsDir $SkillName
        Write-Host "[INSTALL] Kopiowanie skilla '$SkillName' do: $DestPath" -ForegroundColor Cyan
        if (Test-Path $DestPath) {
            if (-not $Force -and -not $DryRun) {
                Write-Warning "Katalog docelowy już istnieje: $DestPath"
                $ans = Read-Host "Czy nadpisać? (t/N)"
                if ($ans -ne 't' -and $ans -ne 'T') {
                    Write-Host "Pominięto instalację skilla." -ForegroundColor Gray
                    return
                }
            }
        }
        if ($DryRun) {
            Write-Host "  [DRY-RUN] Skopiowano by zawartość $SrcPath -> $DestPath" -ForegroundColor Gray
        } else {
            if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null }
            if (-not (Test-Path $DestPath)) { New-Item -ItemType Directory -Force -Path $DestPath | Out-Null }
            Copy-Item -Path (Join-Path $SrcPath "*") -Destination $DestPath -Recurse -Force
            Write-Host "  ✓ Skill '$SkillName' zainstalowany pomyślnie" -ForegroundColor Green
        }
    }
}

# --- OBSŁUGA AGENTA ---
function Process-Agent {
    param([string]$Name)

    # Dobór źródłowego pliku w zależności od platformy
    if ($Platform -eq 'vscode') {
        $SourceFile = Join-Path $AgentsDir "adapters\vscode\${Name}.agent.md"
        if (-not (Test-Path $SourceFile)) {
            $SourceFile = Join-Path $AgentsDir "${Name}_agent.md"
        }
        $DestFile = Join-Path $AgentTargetDir "${Name}.agent.md"
    } else {
        # claude
        $SourceFile = Join-Path $AgentsDir "adapters\claude-code\${Name}.md"
        if (-not (Test-Path $SourceFile)) {
            $SourceFile = Join-Path $AgentsDir "${Name}_agent.md"
        }
        $DestFile = Join-Path $AgentTargetDir "${Name}.md"
    }

    if ($Uninstall) {
        if (Test-Path $DestFile) {
            if ($DryRun) {
                Write-Host "  [DRY-RUN] Usunięto by: $DestFile" -ForegroundColor Gray
            } else {
                Remove-Item -Path $DestFile -Force
                Write-Host "  ✓ Usunięto agenta: $Name" -ForegroundColor Green
            }
        }
        return
    }

    if (-not (Test-Path $SourceFile)) {
        Write-Error "Brak pliku źródłowego agenta: $SourceFile"
        return
    }

    if ((Test-Path $DestFile) -and -not $Force -and -not $DryRun) {
        Write-Warning "Plik docelowy agenta już istnieje: $DestFile"
        $ans = Read-Host "Czy nadpisać agenta '$Name'? (t/N)"
        if ($ans -ne 't' -and $ans -ne 'T') {
            Write-Host "  Pominięto agenta $Name." -ForegroundColor Gray
            return
        }
    }

    if ($DryRun) {
        Write-Host "  [DRY-RUN] Skopiowano by $SourceFile -> $DestFile" -ForegroundColor Gray
    } else {
        if (-not (Test-Path $AgentTargetDir)) { New-Item -ItemType Directory -Force -Path $AgentTargetDir | Out-Null }
        Copy-Item -Path $SourceFile -Destination $DestFile -Force
        Write-Host "  ✓ Zainstalowano agenta: $Name ($Platform adapter)" -ForegroundColor Green
    }
}

if ($AgentName) {
    Write-Host ""
    Write-Host "Operacja na agentach w: $AgentTargetDir (Platforma: $Platform)" -ForegroundColor Cyan
    if ($AgentName -eq "all") {
        foreach ($a in $AvailableAgents) {
            Process-Agent -Name $a
        }
    } else {
        if (-not ($AvailableAgents -contains $AgentName)) {
            Write-Error "Agent '$AgentName' nie istnieje. Dostępne: $($AvailableAgents -join ', ')"
            exit 1
        }
        Process-Agent -Name $AgentName
    }
}
