#!/bin/bash
# Wrapper script called by the macOS LaunchAgent.
# Loads credentials from .env and runs the automation in headless mode.

cd /Users/vibhorgoyal/PersonalWorkspace/job_scripts

# Source .env so NAUKRI_EMAIL and NAUKRI_PASSWORD are available
if [ -f .env ]; then
    set -a
    # shellcheck source=.env
    source .env
    set +a
fi

exec venv/bin/python naukri_update.py
