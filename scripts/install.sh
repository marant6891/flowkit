#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$REPO_ROOT/skills"
TARGET_DIR="$HOME/.claude/skills"

SKILL_NAME="$1"

if [ -z "$SKILL_NAME" ]; then
    echo "Dostępne skille w repozytorium:"
    for d in "$SKILLS_DIR"/*/; do
        name="$(basename "$d")"
        if [[ ! "$name" =~ ^_ ]]; then
            echo "  - $name"
        fi
    done
    echo ""
    read -rp "Podaj nazwę skilla do zainstalowania: " SKILL_NAME
fi

SOURCE_PATH="$SKILLS_DIR/$SKILL_NAME"

if [ ! -d "$SOURCE_PATH" ]; then
    echo "Błąd: Skill '$SKILL_NAME' nie istnieje w $SKILLS_DIR." >&2
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -r "$SOURCE_PATH" "$TARGET_DIR/"
echo "Pomyślnie zainstalowano skill '$SKILL_NAME' w: $TARGET_DIR/$SKILL_NAME"
echo "Claude Code ma teraz dostęp do tego skilla."
