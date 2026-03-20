import json
import logging
import os
import time

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from slack_mcp.app import mcp

logger = logging.getLogger(__name__)

_token = os.environ.get("SLACK_BOT_TOKEN")
if not _token:
    import sys
    print("ERROR: SLACK_BOT_TOKEN is not set. See docs/slack-app-setup.md", file=sys.stderr)

client = WebClient(token=_token)

_MAX_RETRIES = 3
_DEFAULT_RETRY_AFTER = 5


def _call_with_retry(fn, **kwargs):
    """Call a Slack API method with rate-limit retry."""
    for attempt in range(_MAX_RETRIES + 1):
        try:
            return fn(**kwargs)
        except SlackApiError as e:
            if e.response.get("error") == "ratelimited" and attempt < _MAX_RETRIES:
                delay = int(e.response.headers.get("Retry-After", _DEFAULT_RETRY_AFTER))
                logger.warning("Rate limited. Retrying in %ds (attempt %d/%d)", delay, attempt + 1, _MAX_RETRIES)
                time.sleep(delay)
            else:
                raise


@mcp.tool()
def slack_get_thread_replies(channel: str, thread_ts: str) -> str:
    """Get all replies in a Slack thread.

    Args:
        channel: The channel ID (e.g., C0123456789)
        thread_ts: The thread timestamp (e.g., 1234567890.123456)
    """
    try:
        messages = []
        cursor = None
        while True:
            resp = _call_with_retry(
                client.conversations_replies,
                channel=channel,
                ts=thread_ts,
                cursor=cursor,
                limit=200,
            )
            messages.extend(resp["messages"])
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        return json.dumps(messages, ensure_ascii=False)
    except SlackApiError as e:
        return json.dumps({"error": str(e.response["error"])})


@mcp.tool()
def slack_get_channel_messages(channel: str, oldest: str, latest: str) -> str:
    """Get messages from a Slack channel within a time range.

    Args:
        channel: The channel ID (e.g., C0123456789)
        oldest: Start of time range as Unix timestamp (e.g., 1710000000.000000)
        latest: End of time range as Unix timestamp (e.g., 1710086399.999999)
    """
    try:
        messages = []
        cursor = None
        while True:
            resp = _call_with_retry(
                client.conversations_history,
                channel=channel,
                oldest=oldest,
                latest=latest,
                cursor=cursor,
                limit=200,
            )
            messages.extend(resp["messages"])
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        return json.dumps(messages, ensure_ascii=False)
    except SlackApiError as e:
        return json.dumps({"error": str(e.response["error"])})


@mcp.tool()
def slack_get_user_profile(user: str) -> str:
    """Get a Slack user's profile information.

    Args:
        user: The user ID (e.g., U0123456789)
    """
    try:
        resp = _call_with_retry(client.users_info, user=user)
        profile = resp["user"]["profile"]
        return json.dumps(
            {
                "user_id": user,
                "display_name": profile.get("display_name") or profile.get("real_name", ""),
                "real_name": profile.get("real_name", ""),
                "image_48": profile.get("image_48", ""),
            },
            ensure_ascii=False,
        )
    except SlackApiError as e:
        return json.dumps({"error": str(e.response["error"])})


@mcp.tool()
def slack_get_channel_info(channel: str) -> str:
    """Get information about a Slack channel.

    Args:
        channel: The channel ID (e.g., C0123456789)
    """
    try:
        resp = _call_with_retry(client.conversations_info, channel=channel)
        ch = resp["channel"]
        return json.dumps(
            {
                "id": ch["id"],
                "name": ch.get("name", ""),
                "topic": ch.get("topic", {}).get("value", ""),
                "purpose": ch.get("purpose", {}).get("value", ""),
            },
            ensure_ascii=False,
        )
    except SlackApiError as e:
        return json.dumps({"error": str(e.response["error"])})
