# NTS Daily Schedule Notifier

## Purpose

A Python script designed to run on a Raspberry Pi server that sends a daily notification via [ntfy.sh](https://ntfy.sh) with the NTS Radio schedule for both Channel 1 and Channel 2. Notification time is configurable.

## What's in this folder

```
nts-daily-schedule-notifier/
├── .env                           # Local config (git-ignored)
├── .env.example                   # Example config template
├── .gitignore                     # Git ignore rules
├── CLAUDE.md                      # This file (dev notes)
├── README.md                      # Setup instructions
├── nts_schedule_notifier.py       # Main Python script
├── pyproject.toml                 # Python project config (uv)
├── nts-schedule-notifier.service  # Systemd service unit
└── nts-schedule-notifier.timer    # Systemd timer (daily trigger)
```

## How it works

1. **Fetches schedule** from NTS Radio's API (`https://www.nts.live/api/v2/radio/schedule/{channel}`)
2. **Reorders** broadcasts so shows from the notification time onwards appear first, earlier shows at the end
3. **Formats** the schedule for both Channel 1 and Channel 2 into a readable message
4. **Sends notification** via ntfy.sh HTTP POST request

## Configuration

Settings are stored in `.env` file (copy from `.env.example`):
- `NTFY_TOPIC` - Your ntfy.sh topic name (required, keep secret)
- `NTFY_SERVER` - ntfy server URL (default: `https://ntfy.sh`)
- `NOTIFICATION_TIME` - Time in HH:MM format (default: `07:00`). Controls schedule ordering.

## Deployment on Raspberry Pi

### Quick setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure .env
cd ~/nts-daily-schedule-notifier
cp .env.example .env
nano .env  # Set your NTFY_TOPIC

# Test the script (uv will auto-install dependencies)
uv run nts_schedule_notifier.py

# Install systemd service and timer
sudo cp nts-schedule-notifier.service /etc/systemd/system/
sudo cp nts-schedule-notifier.timer /etc/systemd/system/

# Edit service file if needed (change paths/user)
sudo nano /etc/systemd/system/nts-schedule-notifier.service

# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable --now nts-schedule-notifier.timer

# Verify timer is active
systemctl list-timers nts-schedule-notifier.timer
```

### Subscribe to notifications

On your phone/device, subscribe to your ntfy topic:
- Open ntfy app and subscribe to the topic you set in `.env`

## Timeline / Changelog

### 2026-01-14
- Initial implementation
- Python script fetching NTS API schedule
- ntfy.sh notification integration
- Systemd service and timer for Raspberry Pi deployment
- Using uv for Python package management
- Added `.env` file support for configuration (python-dotenv)
- Added `.gitignore`
- Added configurable `NOTIFICATION_TIME` setting
- Schedule now reorders shows: upcoming first, earlier shows at end

## Future plans / Ideas

- [ ] Single interactive install script (`install.sh`) that handles everything:
  - Prompts for ntfy topic
  - Prompts for notification time
  - Auto-detects username and paths
  - Installs uv if needed
  - Sets up systemd service and timer
- [ ] Add show descriptions or genre tags to notifications
- [ ] Optional: filter by favorite shows
- [ ] Add timezone configuration for non-UTC setups
- [ ] Uninstall script to cleanly remove service/timer