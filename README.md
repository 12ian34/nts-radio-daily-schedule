# NTS radio daily schedule

<a href="https://www.nts.live"><img src="NTS_Radio_logo.svg.png" alt="NTS Radio" width="150"></a>

Get a daily notification with the full NTS Radio schedule for Channel 1 and Channel 2. Shows are ordered starting from your notification time, with earlier shows listed at the end.

[**NTS**](https://www.nts.live) is an independent online radio station broadcasting 24/7 from London, Los Angeles, Shanghai, and Manchester. With hundreds of resident DJs and guest shows spanning every genre imaginable—from ambient to grime, jazz to techno, and everything in between—NTS is a home for music discovery and underground culture.

This project is not affiliated with NTS. Just a fan who wanted schedule notifications. 📻

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
git clone https://github.com/12ian34/nts-daily-schedule-notifier.git
cd nts-daily-schedule-notifier
```

### 3. Configure ntfy

```bash
# Copy the example config
cp .env.example .env

# Edit and set your secret ntfy topic name
nano .env
```

### 4. Subscribe to notifications

On your phone:
1. Install the [ntfy app](https://ntfy.sh)
2. Subscribe to the same topic you set in your `.env` file

### 5. Test the script

```bash
uv run nts_schedule_notifier.py
```

You should see output showing the schedule for both channels and a "Notification sent successfully" message.

### 6. Set up the daily timer

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

### 7. Test the service manually

```bash
sudo systemctl start nts-schedule-notifier.service
journalctl -u nts-schedule-notifier.service -f
```

## Configuration

Configuration is stored in a `.env` file in the project directory. Copy the example and edit as needed:

```bash
cp .env.example .env
nano .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `NTFY_TOPIC` | Yes | Your ntfy.sh topic name (pick something unique and secret) |
| `NTFY_SERVER` | No | ntfy server URL (default: `https://ntfy.sh`) |
| `NOTIFICATION_TIME` | No | Time in HH:MM format (default: `07:00`). Controls schedule ordering. |

## Customising the notification time

To change when notifications are sent, update **both** the `.env` file and systemd timer:

1. Edit `.env`:
```bash
NOTIFICATION_TIME=08:30
```

2. Edit `/etc/systemd/system/nts-schedule-notifier.timer`:
```ini
[Timer]
OnCalendar=*-*-* 08:30:00
```

3. Reload the timer:
```bash
sudo systemctl daemon-reload
sudo systemctl restart nts-schedule-notifier.timer
```

The `NOTIFICATION_TIME` setting controls how the schedule is ordered—shows starting from that time appear first, with earlier shows listed at the end under "earlier".

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

## Roadmap

- [ ] Single interactive install script (no manual steps)
- [ ] Show descriptions/genre tags in notifications
- [ ] Filter by favorite shows
- [ ] Timezone configuration

