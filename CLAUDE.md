# NTS Daily Schedule Notifier

## Purpose

A Python script designed to run on a Raspberry Pi server that sends a daily notification via [ntfy.sh](https://ntfy.sh) every morning at 7am with the NTS Radio schedule for both Channel 1 and Channel 2.

## What's in this folder

```
nts-daily-schedule-notifier/
├── CLAUDE.md                      # This file (dev notes)
├── README.md                      # Setup instructions
├── nts_schedule_notifier.py       # Main Python script
├── pyproject.toml                 # Python project config (uv)
├── nts-schedule-notifier.service  # Systemd service unit
└── nts-schedule-notifier.timer    # Systemd timer (7am daily trigger)
```

## How it works

1. **Fetches schedule** from NTS Radio's API (`https://www.nts.live/api/v2/radio/schedule/{channel}`)
2. **Formats** the schedule for both Channel 1 and Channel 2 into a readable message
3. **Sends notification** via ntfy.sh HTTP POST request

## Configuration

Environment variables:
- `NTFY_TOPIC` - Your ntfy.sh topic name (default: `nts-daily-schedule`)
- `NTFY_SERVER` - ntfy server URL (default: `https://ntfy.sh`)

## Deployment on Raspberry Pi

### Quick setup

```bash
# Clone/copy to Pi
scp -r . pi@raspberrypi:~/nts-daily-schedule-notifier/

# SSH into Pi
ssh pi@raspberrypi

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Test the script (uv will auto-install dependencies)
cd ~/nts-daily-schedule-notifier
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
- Open ntfy app or visit `https://ntfy.sh/nts-daily-schedule` (or your custom topic)
- Tap "Subscribe to topic"

## Timeline / Changelog

### 2026-01-14
- Initial implementation
- Python script fetching NTS API schedule
- ntfy.sh notification integration
- Systemd service and timer for Raspberry Pi deployment
- Using uv for Python package management

## Future plans / Ideas

- [ ] Add show descriptions or genre tags to notifications
- [ ] Optional: filter by favorite shows
- [ ] Optional: multiple notification times (morning + evening preview)
- [ ] Add timezone configuration for non-UTC setups
