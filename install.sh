#!/usr/bin/env bash
# Installs now-playing.py into iTerm2's AutoLaunch folder.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/jackrayner/iterm2-spotify-nowplaying/main/install.sh | bash
# or, from a clone of this repo:
#   ./install.sh
set -euo pipefail

RAW_URL="https://raw.githubusercontent.com/jackrayner/iterm2-spotify-nowplaying/main/now-playing.py"
AUTOLAUNCH_DIR="$HOME/Library/Application Support/iTerm2/Scripts/AutoLaunch"
TARGET="$AUTOLAUNCH_DIR/now-playing.py"

mkdir -p "$AUTOLAUNCH_DIR"

# $0 only points at a real now-playing.py when this script is run from a
# clone (e.g. `./install.sh`); under `curl | bash` it's just "bash", so this
# falls through to downloading the file directly.
if [ -f "$0" ] && [ -f "$(dirname -- "$0")/now-playing.py" ]; then
    SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
    ln -sf "$SCRIPT_DIR/now-playing.py" "$TARGET"
    echo "Symlinked $SCRIPT_DIR/now-playing.py -> $TARGET"
else
    curl -fsSL "$RAW_URL" -o "$TARGET"
    echo "Installed now-playing.py -> $TARGET"
fi

API_SERVER_DOMAIN="com.googlecode.iterm2"
API_SERVER_KEY="EnableAPIServer"

print_enable_api_hint() {
    echo "Enable it in iTerm2 Preferences > General > Magic, or run:"
    echo "  defaults write $API_SERVER_DOMAIN $API_SERVER_KEY -bool true"
}

api_enabled=$(defaults read "$API_SERVER_DOMAIN" "$API_SERVER_KEY" 2>/dev/null || echo "0")

if [ "$api_enabled" = "1" ]; then
    echo "iTerm2's Python API is already enabled."
elif { exec 3<>/dev/tty; } 2>/dev/null; then
    # now-playing.py needs iTerm2's Python API to run at all, but it's off
    # by default; /dev/tty lets this prompt work even when this script is
    # itself being fed to bash over stdin (curl | bash).
    printf "iTerm2's Python API is disabled, but is required for this script to run. Enable it now? [y/N] " >&3
    read -r reply <&3
    exec 3<&-
    case "$reply" in
        [Yy]*)
            defaults write "$API_SERVER_DOMAIN" "$API_SERVER_KEY" -bool true
            echo "Enabled iTerm2's Python API."
            ;;
        *)
            echo "Skipped enabling iTerm2's Python API."
            print_enable_api_hint
            ;;
    esac
else
    echo "iTerm2's Python API is disabled and no terminal is available to prompt."
    print_enable_api_hint
fi

echo "Restart iTerm2 to load the script."
