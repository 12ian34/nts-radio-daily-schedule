#!/usr/bin/env python3
"""
NTS Radio Daily Schedule Notifier

Fetches the daily schedule for NTS Radio (Channel 1 & 2) and sends
a notification via ntfy.sh. Designed to run on a Raspberry Pi at 7am daily.
"""

import html
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

import requests
from dotenv import load_dotenv

# Load .env file from the same directory as this script
load_dotenv(Path(__file__).parent / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Configuration via .env file
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
if not NTFY_TOPIC:
    raise RuntimeError("NTFY_TOPIC must be set in .env file")
NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
NOTIFICATION_TIME = os.environ.get("NOTIFICATION_TIME", "07:00")
NTS_API_BASE = "https://www.nts.live/api/v2"
REQUEST_TIMEOUT = 30


class Broadcast(TypedDict):
    name: str
    start_time: str
    end_time: str


class ChannelSchedule(TypedDict):
    channel_name: str
    broadcasts: list[Broadcast]


def fetch_channel_schedule(channel: int, target_date: datetime) -> ChannelSchedule:
    """
    Fetch the NTS schedule for a specific channel and date.

    Args:
        channel: 1 or 2
        target_date: The date to get schedule for

    Returns:
        ChannelSchedule with broadcasts for the day
    """
    url = f"{NTS_API_BASE}/radio/schedule/{channel}"
    channel_name = f"Channel {channel}"
    target_date_str = target_date.strftime("%Y-%m-%d")

    logger.info(f"Fetching {channel_name} schedule from {url}")

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {channel_name} schedule: {e}")
        raise

    broadcasts: list[Broadcast] = []

    # Find the schedule for the target date
    for day_schedule in data.get("results", []):
        schedule_date = day_schedule.get("date", "")
        if schedule_date == target_date_str:
            for broadcast in day_schedule.get("broadcasts", []):
                title = html.unescape(broadcast.get("broadcast_title", "Unknown"))
                start_ts = broadcast.get("start_timestamp", "")
                end_ts = broadcast.get("end_timestamp", "")

                # Parse timestamps to get time
                start_time = ""
                end_time = ""
                if start_ts:
                    start_dt = datetime.fromisoformat(start_ts.replace("Z", "+00:00"))
                    start_time = start_dt.strftime("%H:%M")
                if end_ts:
                    end_dt = datetime.fromisoformat(end_ts.replace("Z", "+00:00"))
                    end_time = end_dt.strftime("%H:%M")

                broadcasts.append(Broadcast(name=title, start_time=start_time, end_time=end_time))
            break

    logger.info(f"Found {len(broadcasts)} broadcasts for {channel_name} on {target_date_str}")
    return ChannelSchedule(channel_name=channel_name, broadcasts=broadcasts)


def fetch_all_schedules(target_date: datetime) -> dict[str, ChannelSchedule]:
    """Fetch schedules for both NTS channels."""
    schedules: dict[str, ChannelSchedule] = {}

    for channel in [1, 2]:
        try:
            schedule = fetch_channel_schedule(channel, target_date)
            schedules[schedule["channel_name"]] = schedule
        except Exception as e:
            logger.error(f"Failed to fetch Channel {channel}: {e}")

    return schedules


def reorder_broadcasts(broadcasts: list[Broadcast], from_time: str) -> tuple[list[Broadcast], list[Broadcast]]:
    """
    Split broadcasts into upcoming and earlier shows.

    Args:
        broadcasts: List of broadcasts for the day
        from_time: Time string in HH:MM format (e.g., "07:00")

    Returns:
        Tuple of (upcoming broadcasts, earlier broadcasts)
    """
    upcoming: list[Broadcast] = []
    earlier: list[Broadcast] = []

    for broadcast in broadcasts:
        if broadcast["start_time"] >= from_time:
            upcoming.append(broadcast)
        else:
            earlier.append(broadcast)

    return upcoming, earlier


def format_schedule_message(schedules: dict[str, ChannelSchedule], date: datetime, from_time: str) -> str:
    """Format the schedule data into a readable notification message."""
    date_str = date.strftime("%a %d %b").lower()
    lines = [f"🎵 {date_str}", ""]

    for channel_name in sorted(schedules.keys()):
        channel = schedules[channel_name]
        lines.append(f"{channel_name.upper()}")

        if not channel["broadcasts"]:
            lines.append("  No broadcasts scheduled")
        else:
            upcoming, earlier = reorder_broadcasts(channel["broadcasts"], from_time)

            # Show upcoming broadcasts first
            for broadcast in upcoming:
                time_range = f"{broadcast['start_time']}-{broadcast['end_time']}"
                lines.append(f"  {time_range}  {broadcast['name']}")

            # Show earlier broadcasts (already passed) after a separator
            if earlier:
                lines.append("  ┄┄┄ earlier ┄┄┄")
                for broadcast in earlier:
                    time_range = f"{broadcast['start_time']}-{broadcast['end_time']}"
                    lines.append(f"  {time_range}  {broadcast['name']}")

        lines.append("")

    return "\n".join(lines)


def send_notification(message: str, title: str = "NTS Daily Schedule") -> bool:
    """Send a notification via ntfy.sh."""
    url = f"{NTFY_SERVER}/{NTFY_TOPIC}"

    headers = {
        "Title": title,
        "Priority": "default",
        "Tags": "radio,music",
        "Actions": "view, Channel 1, https://www.nts.live/1; view, Channel 2, https://www.nts.live/2",
    }

    logger.info(f"Sending notification to {url}")

    try:
        response = requests.post(
            url,
            data=message.encode("utf-8"),
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        logger.info("Notification sent successfully")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send notification: {e}")
        return False


def main() -> int:
    """Main entry point."""
    logger.info("NTS Schedule Notifier starting")
    logger.info(f"NTFY_TOPIC: {NTFY_TOPIC}")
    logger.info(f"NTFY_SERVER: {NTFY_SERVER}")
    logger.info(f"NOTIFICATION_TIME: {NOTIFICATION_TIME}")

    try:
        today = datetime.now(timezone.utc)
        schedules = fetch_all_schedules(today)

        if not schedules:
            logger.warning("No schedule data returned")
            send_notification(
                "⚠️ Could not fetch NTS schedule - no data returned",
                title="NTS Schedule Error",
            )
            return 1

        message = format_schedule_message(schedules, today, NOTIFICATION_TIME)
        logger.info(f"Formatted message:\n{message}")

        if send_notification(message):
            logger.info("Schedule notification sent successfully")
            return 0
        else:
            logger.error("Failed to send notification")
            return 1

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        send_notification(
            f"⚠️ NTS Schedule Notifier error: {e}",
            title="NTS Schedule Error",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
