#!/usr/bin/env bash
# Claude OS starter — one-command setup.
# Copies the vault + CLAUDE.md to ~/claude-os and installs the skills
# into ~/.claude/skills so Claude Code picks them up.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-$HOME/claude-os}"
SKILLS_DIR="$HOME/.claude/skills"

echo "==> Claude OS setup"
echo "    kit:    $HERE"
echo "    target: $TARGET"

# 1. Vault + CLAUDE.md
mkdir -p "$TARGET"
if [ -d "$TARGET/vault" ]; then
  echo "==> $TARGET/vault already exists — leaving your notes alone."
else
  cp -R "$HERE/vault" "$TARGET/vault"
  echo "==> Vault created at $TARGET/vault"
fi
if [ ! -f "$TARGET/CLAUDE.md" ]; then
  cp "$HERE/CLAUDE.md" "$TARGET/CLAUDE.md"
  echo "==> CLAUDE.md installed"
else
  echo "==> CLAUDE.md already exists — not overwriting."
fi

# 2. Skills
mkdir -p "$SKILLS_DIR"
for skill in brain plan-today tnc-video-factory; do
  mkdir -p "$SKILLS_DIR/$skill"
  cp "$HERE/skills/$skill/SKILL.md" "$SKILLS_DIR/$skill/SKILL.md"
  echo "==> Installed skill: /$skill"
done

# 3. Git safety net
if [ ! -d "$TARGET/.git" ]; then
  git -C "$TARGET" init -q
  cat > "$TARGET/.gitignore" <<'EOF'
.obsidian/workspace*
.DS_Store
EOF
  git -C "$TARGET" add -A
  git -C "$TARGET" -c user.name="${GIT_AUTHOR_NAME:-Claude OS Setup}" \
      -c user.email="${GIT_AUTHOR_EMAIL:-setup@localhost}" \
      commit -qm "Initial brain: vault + CLAUDE.md" || true
  echo "==> Git repo initialized (create a PRIVATE GitHub repo and push when ready)"
fi

echo ""
echo "Done. Next steps:"
echo "  1. Open Obsidian -> 'Open folder as vault' -> $TARGET/vault"
echo "  2. cd $TARGET && claude"
echo "  3. Restart Claude Code if it was open, then try: /brain what is my offer?"
