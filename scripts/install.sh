#!/usr/bin/env bash
# FlowKit Installer — skille i agenty
# Użycie:
#   ./scripts/install.sh skill <skill-name> [target-dir]
#   ./scripts/install.sh agent <agent-name|all> [target-dir]
#   ./scripts/install.sh skill <skill-name> && ./scripts/install.sh agent all
#
# Przykłady:
#   ./scripts/install.sh skill client-pt-prd-writer
#   ./scripts/install.sh agent all
#   ./scripts/install.sh agent agent-3x3

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$REPO_ROOT/skills"
AGENTS_DIR="$REPO_ROOT/agents"

MODE="${1:-}"
NAME="${2:-}"

list_available() {
    echo ""
    echo "=== FlowKit Installer ==="
    echo ""
    echo "Dostępne SKILLE:"
    for d in "$SKILLS_DIR"/*/; do
        base="$(basename "$d")"
        if [[ ! "$base" =~ ^_ ]]; then echo "  - $base"; fi
    done
    echo ""
    echo "Dostępne AGENTY:"
    for f in "$AGENTS_DIR"/*_agent.md; do
        base="$(basename "$f" _agent.md)"
        echo "  - $base"
    done
    echo "  (użyj 'all' aby zainstalować wszystkich agentów)"
    echo ""
}

if [ -z "$MODE" ]; then
    list_available
    echo "Użycie: $0 skill <nazwa> | $0 agent <nazwa|all>"
    exit 0
fi

# --- Instalacja skilla ---
if [ "$MODE" = "skill" ]; then
    TARGET_DIR="${3:-$HOME/.claude/skills}"

    if [ -z "$NAME" ]; then
        echo "Dostępne skille:"
        for d in "$SKILLS_DIR"/*/; do
            base="$(basename "$d")"
            if [[ ! "$base" =~ ^_ ]]; then echo "  - $base"; fi
        done
        read -rp "Podaj nazwę skilla: " NAME
    fi

    SOURCE_PATH="$SKILLS_DIR/$NAME"
    if [ ! -d "$SOURCE_PATH" ]; then
        echo "Błąd: Skill '$NAME' nie istnieje w $SKILLS_DIR." >&2
        exit 1
    fi

    mkdir -p "$TARGET_DIR"
    cp -r "$SOURCE_PATH" "$TARGET_DIR/"
    echo "✓ Skill '$NAME' zainstalowany w: $TARGET_DIR/$NAME"
    echo "  Claude Code ma teraz dostęp do tego skilla."

# --- Instalacja agenta/agentów ---
elif [ "$MODE" = "agent" ]; then
    TARGET_DIR="${3:-$HOME/.claude/agents}"

    install_agent() {
        local agent_name="$1"
        local src="$AGENTS_DIR/${agent_name}_agent.md"
        if [ ! -f "$src" ]; then
            echo "Błąd: Agent '$agent_name' nie istnieje (szukano: $src)" >&2
            return 1
        fi
        mkdir -p "$TARGET_DIR"
        cp "$src" "$TARGET_DIR/${agent_name}_agent.md"
        echo "  ✓ $agent_name"
    }

    echo "Instalacja agentów w: $TARGET_DIR"

    if [ "$NAME" = "all" ]; then
        echo "Instalowanie wszystkich agentów..."
        for f in "$AGENTS_DIR"/*_agent.md; do
            agent_name="$(basename "$f" _agent.md)"
            install_agent "$agent_name"
        done
    elif [ -z "$NAME" ]; then
        echo "Podaj nazwę agenta lub 'all'. Dostępne:"
        for f in "$AGENTS_DIR"/*_agent.md; do
            echo "  - $(basename "$f" _agent.md)"
        done
        exit 1
    else
        install_agent "$NAME"
    fi

    echo ""
    echo "Claude Code automatycznie wykryje agentów z ~/.claude/agents/"
    echo "Restart Claude Code może być wymagany do odświeżenia listy."

else
    echo "Nieznany tryb: '$MODE'. Użyj: skill | agent" >&2
    exit 1
fi
