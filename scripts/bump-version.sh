#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/bump-version.sh <major|minor|patch>
# Bumps version across all config files and creates a git tag.

BUMP_TYPE="${1:-}"

if [[ -z "$BUMP_TYPE" || ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
  echo "Usage: $0 <major|minor|patch>"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Read current version from plugin.json
CURRENT=$(python3 -c "
import json
with open('$ROOT/.claude-plugin/plugin.json') as f:
    print(json.load(f)['version'])
")

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP_TYPE" in
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
  minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
  patch) PATCH=$((PATCH + 1)) ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"

echo "Bumping version: $CURRENT -> $NEW_VERSION"

# Update plugin.json
python3 -c "
import json, pathlib
p = pathlib.Path('$ROOT/.claude-plugin/plugin.json')
d = json.loads(p.read_text())
d['version'] = '$NEW_VERSION'
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
"

# Update marketplace.json
python3 -c "
import json, pathlib
p = pathlib.Path('$ROOT/.claude-plugin/marketplace.json')
d = json.loads(p.read_text())
for plugin in d.get('plugins', []):
    if plugin['name'] == 'slackbot':
        plugin['version'] = '$NEW_VERSION'
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
"

# Update pyproject.toml
sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" "$ROOT/pyproject.toml"

echo "Updated files:"
echo "  .claude-plugin/plugin.json"
echo "  .claude-plugin/marketplace.json"
echo "  pyproject.toml"
echo ""
echo "Next steps:"
echo "  1. Update CHANGELOG.md"
echo "  2. git add -A && git commit -m \"chore: bump version to $NEW_VERSION\""
echo "  3. git tag v$NEW_VERSION"
echo "  4. git push origin main --tags"
