#!/bin/sh
# Installs now-playing.py into iTerm2's AutoLaunch folder.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/jackrayner/iterm2-spotify-nowplaying/main/install.sh | sh
# or, from a clone of this repo:
#   ./install.sh
set -eu

RAW_URL="https://raw.githubusercontent.com/jackrayner/iterm2-spotify-nowplaying/main/now-playing.py"
AUTOLAUNCH_DIR="$HOME/Library/Application Support/iTerm2/Scripts/AutoLaunch"
TARGET="$AUTOLAUNCH_DIR/now-playing.py"

mkdir -p "$AUTOLAUNCH_DIR"

# $0 only points at a real now-playing.py when this script is run from a
# clone (e.g. `./install.sh`); under `curl | sh` it's just "sh", so this
# falls through to downloading the file directly.
if [ -f "$0" ] && [ -f "$(dirname -- "$0")/now-playing.py" ]; then
    SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
    ln -sf "$SCRIPT_DIR/now-playing.py" "$TARGET"
    echo "Symlinked $SCRIPT_DIR/now-playing.py -> $TARGET"
else
    curl -fsSL "$RAW_URL" -o "$TARGET"
    echo "Installed now-playing.py -> $TARGET"
fi

echo "Restart iTerm2 to load the script."
