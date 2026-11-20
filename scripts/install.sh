#!/usr/bin/env bash
# FlowKit Safe Installer — skille i agenty
# Obsługuje flagi: --dry-run, --force, --platform claude|vscode, --uninstall
#
# Przykłady:
#   ./scripts/install.sh skill flowkit-client-pt-prd-writer --dry-run
#   ./scripts/install.sh agent all --platform claude --force
#   ./scripts/install.sh agent agent-3x3 --platform vscode

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$REPO_ROOT/skills"
AGENTS_DIR="$REPO_ROOT/agents"

MODE=""
NAME=""
TARGET_DIR=""
DRY_RUN=false
FORCE=false
UNINSTALL=false
PLATFORM="claude"

# Parsowanie argumentów
while [[ $# -gt 0 ]]; do
    case "$1" in
        skill|agent)
            MODE="$1"
            shift
            if [[ $# -gt 0 && ! "$1" =~ ^-- ]]; then
                NAME="$1"
                shift
            fi
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --target)
            TARGET_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Użycie: $0 [skill|agent] [nazwa|all] [--platform claude|vscode] [--dry-run] [--force] [--uninstall]"
            exit 0
            ;;
        *)
            if [ -z "$TARGET_DIR" ]; then
                TARGET_DIR="$1"
            fi
            shift
            ;;
    esac
done

AVAILABLE_SKILLS=("flowkit-client-pt-prd-writer" "flowkit-client-meeting-recap" "flowkit-devops-incident-postmortem" "flowkit-sql-data-assistant" "flowkit-devops-sre-review")
AVAILABLE_AGENTS=("agent-3x3" "agent-3x3-analyzer" "agent-3x3-verifier" "agent-3x3-planner" "agent-3x3-implementer" "agent-3x3-devops" "agent-3x3-pm" "agent-3x3-diagnostics" "agent-3x3-analyst" "agent-3x3-validator")

if [ -z "$MODE" ]; then
    echo ""
    echo "=== FlowKit Safe Installer (Platform: $PLATFORM) ==="
    echo ""
    echo "Dostępne SKILLE:"
    for s in "${AVAILABLE_SKILLS[@]}"; do echo "  - $s"; done
    echo ""
    echo "Dostępne AGENTY:"
    for a in "${AVAILABLE_AGENTS[@]}"; do echo "  - $a"; done
    echo "  (użyj 'all' aby wybrać wszystkich agentów)"
    echo ""
    echo "Użycie: $0 skill <nazwa> | $0 agent <nazwa|all> [--dry-run] [--force]"
    exit 0
fi

# --- SKILLE ---
if [ "$MODE" = "skill" ]; then
    if [ -z "$TARGET_DIR" ]; then
        if [ "$PLATFORM" = "vscode" ]; then
            TARGET_DIR="$PWD/.github/skills"
        else
            TARGET_DIR="$HOME/.claude/skills"
        fi
    fi

    # Walidacja whitelist
    VALID=false
    for s in "${AVAILABLE_SKILLS[@]}"; do
        if [ "$s" = "$NAME" ]; then VALID=true; break; fi
    done
    if [ "$VALID" = false ]; then
        echo "Błąd: Nieprawidłowa nazwa skilla '$NAME'. Dozwolone: ${AVAILABLE_SKILLS[*]}" >&2
        exit 1
    fi

    DEST="$TARGET_DIR/$NAME"
    SRC="$SKILLS_DIR/$NAME"

    if [ "$UNINSTALL" = true ]; then
        echo "[UNINSTALL] Usuwanie skilla '$NAME' z: $DEST"
        if [ -d "$DEST" ]; then
            if [ "$DRY_RUN" = true ]; then
                echo "  [DRY-RUN] Usunięto by katalog $DEST"
            else
                rm -rf "$DEST"
                echo "  ✓ Skill odinstalowany pomyślnie"
            fi
        else
            echo "  Skill nie był zainstalowany w tej lokalizacji."
        fi
        exit 0
    fi

    echo "[INSTALL] Instalowanie skilla '$NAME' w: $DEST"
    if [ -d "$DEST" ] && [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
        read -rp "Katalog $DEST już istnieje. Nadpisać? (t/N) " confirm
        if [[ ! "$confirm" =~ ^[tTyY]$ ]]; then
            echo "Pominięto instalację."
            exit 0
        fi
    fi

    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] Skopiowano by $SRC/* do $DEST"
    else
        mkdir -p "$DEST"
        cp -r "$SRC/"* "$DEST/"
        echo "  ✓ Skill '$NAME' zainstalowany pomyślnie"
    fi

# --- AGENTY ---
elif [ "$MODE" = "agent" ]; then
    if [ -z "$TARGET_DIR" ]; then
        if [ "$PLATFORM" = "vscode" ]; then
            TARGET_DIR="$PWD/.github/agents"
        else
            TARGET_DIR="$HOME/.claude/agents"
        fi
    fi

    process_agent() {
        local a="$1"
        local src=""
        local dest=""

        if [ "$PLATFORM" = "vscode" ]; then
            src="$AGENTS_DIR/adapters/vscode/${a}.agent.md"
            if [ ! -f "$src" ]; then src="$AGENTS_DIR/${a}_agent.md"; fi
            dest="$TARGET_DIR/${a}.agent.md"
        else
            src="$AGENTS_DIR/adapters/claude-code/${a}.md"
            if [ ! -f "$src" ]; then src="$AGENTS_DIR/${a}_agent.md"; fi
            dest="$TARGET_DIR/${a}.md"
        fi

        if [ "$UNINSTALL" = true ]; then
            if [ -f "$dest" ]; then
                if [ "$DRY_RUN" = true ]; then
                    echo "  [DRY-RUN] Usunięto by $dest"
                else
                    rm -f "$dest"
                    echo "  ✓ Usunięto agenta: $a"
                fi
            fi
            return 0
        fi

        if [ ! -f "$src" ]; then
            echo "Błąd: Brak pliku źródłowego: $src" >&2
            return 1
        fi

        if [ -f "$dest" ] && [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
            read -rp "Plik $dest istnieje. Nadpisać agenta $a? (t/N) " confirm
            if [[ ! "$confirm" =~ ^[tTyY]$ ]]; then
                echo "  Pominięto agenta $a."
                return 0
            fi
        fi

        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY-RUN] Skopiowano by $src -> $dest"
        else
            mkdir -p "$TARGET_DIR"
            cp "$src" "$dest"
            echo "  ✓ Zainstalowano agenta: $a ($PLATFORM adapter)"
        fi
    }

    echo "Operacja na agentach w: $TARGET_DIR (Platforma: $PLATFORM)"
    if [ "$NAME" = "all" ]; then
        for a in "${AVAILABLE_AGENTS[@]}"; do
            process_agent "$a"
        done
    else
        VALID=false
        for a in "${AVAILABLE_AGENTS[@]}"; do
            if [ "$a" = "$NAME" ]; then VALID=true; break; fi
        done
        if [ "$VALID" = false ]; then
            echo "Błąd: Nieznany agent '$NAME'. Dostępne: ${AVAILABLE_AGENTS[*]}" >&2
            exit 1
        fi
        process_agent "$NAME"
    fi

    # Lokalna warstwa bezpieczeństwa jest wymagana przez agentów uruchamiających polecenia.
    if [ "$PLATFORM" = "vscode" ]; then
        RUNTIME_DIR="$(dirname "$TARGET_DIR")/flowkit/runtime"
    else
        RUNTIME_DIR="$HOME/.claude/flowkit/runtime"
    fi
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] Skopiowano by runtime -> $RUNTIME_DIR"
    elif [ "$UNINSTALL" = true ]; then
        if [ "$NAME" = "all" ]; then rm -rf "$RUNTIME_DIR"; fi
    else
        mkdir -p "$RUNTIME_DIR"
        cp -r "$REPO_ROOT/runtime/"* "$RUNTIME_DIR/"
        rm -rf "$RUNTIME_DIR/__pycache__"
        echo "  ✓ Zainstalowano lokalną warstwę bezpieczeństwa: $RUNTIME_DIR"
    fi
fi
