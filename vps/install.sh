#!/bin/sh
# Run as the same user that runs agy on the VPS.
set -eu

src=$(CDPATH= cd "$(dirname "$0")" && pwd)
state="$HOME/.local/state/agy-mac"
rules="$HOME/.gemini/config/rules"
agy="$HOME/.local/bin/agy"
if [ ! -x "$agy" ]; then
    echo "Expected the Antigravity CLI at $agy." >&2
    exit 1
fi

install -d -m 700 "$state" "$state/clipboard-bin"
mkdir -p "$rules"
install -m 700 "$src/mac-cwd-proxy" "$state/mac-cwd-proxy"
install -m 600 "$src/mac-tools.json" "$state/mac-tools.json"
install -m 700 "$src/clipboard-bin/xclip" "$state/clipboard-bin/xclip"
install -m 600 "$src/config/rules/mac-default.md" "$rules/mac-default.md"
"$agy" mcp add mac "$state/mac-cwd-proxy"
