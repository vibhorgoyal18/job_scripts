#!/bin/bash
# One-time setup: creates .env with credentials and installs the macOS LaunchAgent.
# Run once: bash install_launchagent.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.vibhorgoyal.naukri_refresh.plist"
PLIST_SRC="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

# ------------------------------------------------------------------
# 1. Credentials
# ------------------------------------------------------------------
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "Enter Naukri credentials (stored locally in .env, never committed to git):"
    read -rp "  Email: " NAUKRI_EMAIL
    read -rsp "  Password: " NAUKRI_PASSWORD
    echo
    printf 'NAUKRI_EMAIL=%s\nNAUKRI_PASSWORD=%s\n' "$NAUKRI_EMAIL" "$NAUKRI_PASSWORD" \
        > "$SCRIPT_DIR/.env"
    echo "[+] .env created."
else
    echo "[i] .env already exists — skipping credential setup."
fi

# ------------------------------------------------------------------
# 2. Permissions
# ------------------------------------------------------------------
chmod +x "$SCRIPT_DIR/run_naukri.sh"

# ------------------------------------------------------------------
# 3. Install plist
# ------------------------------------------------------------------
mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DEST"

# Unload any previously installed version, then load fresh
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load   "$PLIST_DEST"

echo ""
echo "[+] LaunchAgent installed. The script runs every day at 9:00 AM (Mac local time)."
echo "    Logs : $SCRIPT_DIR/naukri_refresh.log"
echo ""
echo "    Test now   : launchctl start com.vibhorgoyal.naukri_refresh"
echo "    View log   : tail -f $SCRIPT_DIR/naukri_refresh.log"
echo "    Uninstall  : launchctl unload $PLIST_DEST && rm $PLIST_DEST"
