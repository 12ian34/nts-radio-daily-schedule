# NTS Daily Schedule Notifier

Get a daily notification at 7am with the full NTS Radio schedule for Channel 1 and Channel 2.

![ntfy notification example](https://ntfy.sh/static/img/ntfy.png)

## Requirements

- Raspberry Pi (or any Linux server)
- Internet connection
- [ntfy](https://ntfy.sh) app on your phone (iOS/Android)

## Quick Start

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart your terminal
```

### 2. Clone the repo

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/nts-daily-schedule-notifier.git
cd nts-daily-schedule-notifier
```

### 3. Test the script

```bash
uv run nts_schedule_notifier.py
```

You should see output showing the schedule for both channels and a "Notification sent successfully" message.

### 4. Subscribe to notifications

On your phone:
1. Install the [ntfy app](https://ntfy.sh)
2. Subscribe to the topic: `nts-daily-schedule`

Or use a custom topic by setting `NTFY_TOPIC` environment variable.

### 5. Set up the daily timer

```bash
# Copy service and timer files
sudo cp nts-schedule-notifier.service /etc/systemd/system/
sudo cp nts-schedule-notifier.timer /etc/systemd/system/

# Edit paths if your username isn't 'pi' or repo is in a different location
sudo nano /etc/systemd/system/nts-schedule-notifier.service

# Reload systemd and enable the timer
sudo systemctl daemon-reload
sudo systemctl enable --now nts-schedule-notifier.timer

# Verify it's scheduled
systemctl list-timers nts-schedule-notifier.timer
```

### 6. Test the service manually

```bash
sudo systemctl start nts-schedule-notifier.service
journalctl -u nts-schedule-notifier.service -f
```

## Configuration

Set environment variables in the service file (`/etc/systemd/system/nts-schedule-notifier.service`):

| Variable | Default | Description |
|----------|---------|-------------|
| `NTFY_TOPIC` | `nts-daily-schedule` | Your ntfy.sh topic name |
| `NTFY_SERVER` | `https://ntfy.sh` | ntfy server URL (use your own if self-hosted) |

## Customising the schedule time

Edit `/etc/systemd/system/nts-schedule-notifier.timer`:

```ini
[Timer]
OnCalendar=*-*-* 07:00:00  # Change to your preferred time
```

Then reload:

```bash
sudo systemctl daemon-reload
sudo systemctl restart nts-schedule-notifier.timer
```

## Updating

```bash
cd ~/nts-daily-schedule-notifier
git pull
```

No need to restart anything - the timer will use the updated script on next run.

## Troubleshooting

**Check timer status:**
```bash
systemctl list-timers nts-schedule-notifier.timer
```

**Check service logs:**
```bash
journalctl -u nts-schedule-notifier.service --since today
```

**Run manually with debug output:**
```bash
cd ~/nts-daily-schedule-notifier
uv run nts_schedule_notifier.py
```

**Service file paths wrong?**

If your username isn't `pi` or repo is elsewhere, edit the service file:
```bash
sudo nano /etc/systemd/system/nts-schedule-notifier.service
```

Update these lines:
```ini
ExecStart=/home/YOUR_USER/.local/bin/uv run /home/YOUR_USER/nts-daily-schedule-notifier/nts_schedule_notifier.py
WorkingDirectory=/home/YOUR_USER/nts-daily-schedule-notifier
User=YOUR_USER
```

## License

MIT
