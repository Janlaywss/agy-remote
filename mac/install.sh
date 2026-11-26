#!/bin/sh
# Install this Mac's bridge and load the three per-user LaunchAgents.
set -eu

src=$(CDPATH= cd "$(dirname "$0")" && pwd)
bin="$HOME/.local/bin"
lib="$HOME/.local/share/agy-mac"
agents="$HOME/Library/LaunchAgents"
domain="gui/$(id -u)"

launchctl print "$domain" >/dev/null
build=$(mktemp -d)
trap 'rm -rf "$build"' EXIT
python3 "$src/build.py" --output "$build"
plutil -lint "$build"/*.plist

mkdir -p "$bin" "$agents"
install -d -m 700 "$lib"
install -m 600 "$build/connection.json" "$lib/connection.json"
install -m 755 "$src/bin/agy-mac" "$src/bin/agy-mac-job" "$bin/"
install -m 700 "$src/service/mac_tools.py" "$src/service/tunnel" "$build/read-png" "$lib/"

for name in tools clipboard tunnel; do
    label="local.agy-mac.$name"
    if launchctl print "$domain/$label" >/dev/null 2>&1; then
        launchctl bootout "$domain/$label"
    fi
    if [ "$name" = clipboard ] && [ -S "$lib/clipboard.sock" ]; then
        rm -f "$lib/clipboard.sock"
    fi
    install -m 600 "$build/$label.plist" "$agents/$label.plist"
    launchctl bootstrap "$domain" "$agents/$label.plist"
done
