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
└── pyproject.toml                 # Python project config (uv)
```

## How it works

1. **Fetches schedule** from NTS Radio's API (`https://www.nts.live/api/v2/radio/schedule/{channel}`)
2. **Reorders** broadcasts so shows from the notification time onwards appear first, earlier shows at the end
3. **Formats** the schedule for both Channel 1 and Channel 2 into a readable message
4. **Sends notification** via ntfy.sh HTTP POST request with action buttons to open live streams

## Configuration

Settings are stored in `.env` file (copy from `.env.example`):
- `NTFY_TOPIC` - Your ntfy.sh topic name (required, keep secret)
- `NTFY_SERVER` - ntfy server URL (default: `https://ntfy.sh`)
- `NTFY_ACCESS_TOKEN` - Access token for ntfy authentication (optional, for protected servers)
- `NOTIFICATION_TIME` - Time in HH:MM format (default: `07:00`). Controls schedule ordering.

## Deployment on Raspberry Pi

### Quick setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and configure
cd ~
git clone <repo-url> nts-daily-schedule-notifier
cd nts-daily-schedule-notifier
cp .env.example .env
nano .env  # Set your NTFY_TOPIC (and optionally NTFY_ACCESS_TOKEN)

# Test the script (uv will auto-install dependencies)
uv run nts_schedule_notifier.py

# Schedule daily at 7am via crontab
crontab -e
# Add this line:
# 0 7 * * * cd /home/pi/nts-daily-schedule-notifier && /home/pi/.local/bin/uv run nts_schedule_notifier.py >> /home/pi/nts-daily-schedule-notifier/cron.log 2>&1

# Verify crontab
crontab -l
```

### Changing the notification time

1. Edit crontab (`crontab -e`) and change the schedule (e.g., `0 8 * * *` for 8am)
2. Update `NOTIFICATION_TIME` in `.env` to match (controls which shows appear first)

### Subscribe to notifications

On your phone/device, subscribe to your ntfy topic:
- Open ntfy app and subscribe to the topic you set in `.env`

## Timeline / Changelog

### 2026-01-19
- Added `NTFY_ACCESS_TOKEN` support for authenticated ntfy servers
- Switched from systemd to crontab for scheduling (simpler setup)

### 2026-01-14
- Initial implementation
- Python script fetching NTS API schedule
- ntfy.sh notification integration
- Using uv for Python package management
- Added `.env` file support for configuration (python-dotenv)
- Added `.gitignore`
- Added configurable `NOTIFICATION_TIME` setting
- Schedule now reorders shows: upcoming first, earlier shows at end
- Added action buttons to open Channel 1/2 live streams directly

## Future plans / Ideas

- [ ] Single interactive install script (`install.sh`) that handles everything:
  - Prompts for ntfy topic
  - Prompts for notification time
  - Auto-detects username and paths
  - Installs uv if needed
  - Sets up crontab entry
- [ ] Add show descriptions or genre tags to notifications
- [ ] Optional: filter by favorite shows
- [ ] Add timezone configuration for non-UTC setups