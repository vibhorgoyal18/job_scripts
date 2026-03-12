# job_scripts

Automation scripts for job-related tasks.

---

## naukri_update.py

Logs into [Naukri.com](https://www.naukri.com), opens the profile summary editor, performs a no-op edit, and saves — which marks your profile as recently updated, improving its visibility to recruiters.

### How it works

1. Opens the Naukri login page in a Chrome window
2. Fills in credentials and submits
3. Navigates to the profile page
4. Clicks the Profile Summary edit button
5. Types a space then deletes it (no-op) to "dirty" the field
6. Clicks Save

### Requirements

- Python 3.9+
- Google Chrome installed
- macOS (for the LaunchAgent scheduler; the script itself runs on any OS)

### Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/vibhorgoyal18/job_scripts.git
cd job_scripts

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright's Chromium browser
playwright install chromium

# 5. Create .env with your Naukri credentials
cat > .env <<EOF
NAUKRI_EMAIL=you@example.com
NAUKRI_PASSWORD=yourpassword
EOF
```

### Run manually

```bash
source venv/bin/activate
python naukri_update.py --email you@example.com --password yourpassword
```

Credentials can also be passed via environment variables instead of CLI flags:

```bash
export NAUKRI_EMAIL=you@example.com
export NAUKRI_PASSWORD=yourpassword
python naukri_update.py
```

---

## Scheduling on macOS (LaunchAgent)

The `install_launchagent.sh` script installs a macOS LaunchAgent that runs the automation every day at **9:00 AM** (Mac local time).

> **Note:** Naukri is served behind Akamai CDN, which blocks requests from cloud/CI datacenter IPs. The script must run from a regular residential/home network — hence the local Mac scheduler instead of GitHub Actions.

### Install

```bash
bash install_launchagent.sh
```

This will:
- Prompt for credentials if `.env` doesn't exist yet
- Copy the plist to `~/Library/LaunchAgents/`
- Load it with `launchctl`

### Useful commands

```bash
# Trigger immediately (for testing)
launchctl start com.vibhorgoyal.naukri_refresh

# View live log
tail -f naukri_refresh.log

# Uninstall
launchctl unload ~/Library/LaunchAgents/com.vibhorgoyal.naukri_refresh.plist
rm ~/Library/LaunchAgents/com.vibhorgoyal.naukri_refresh.plist
```

### Files

| File | Purpose |
|------|---------|
| `naukri_update.py` | Main automation script |
| `run_naukri.sh` | Shell wrapper called by launchd (sources `.env`) |
| `com.vibhorgoyal.naukri_refresh.plist` | macOS LaunchAgent definition |
| `install_launchagent.sh` | One-time setup script |
| `requirements.txt` | Python dependencies |
| `.env` | Credentials — **gitignored, never committed** |
| `naukri_refresh.log` | Log output — **gitignored** |
