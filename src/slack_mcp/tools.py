import json
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from slack_mcp.app import mcp

_token = os.environ.get("SLACK_BOT_TOKEN")
if not _token:
    import sys
    print("ERROR: SLACK_BOT_TOKEN is not set. See docs/slack-app-setup.md", file=sys.stderr)

client = WebClient(token=_token)


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
            resp = client.conversations_replies(
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
def slack_get_user_profile(user: str) -> str:
    """Get a Slack user's profile information.

    Args:
        user: The user ID (e.g., U0123456789)
    """
    try:
        resp = client.users_info(user=user)
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
        resp = client.conversations_info(channel=channel)
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
