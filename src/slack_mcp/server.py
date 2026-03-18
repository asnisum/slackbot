import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)

# Logging must go to stderr (stdout is used for JSON-RPC over stdio)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

from slack_mcp.app import mcp  # noqa: E402
import slack_mcp.tools  # noqa: E402, F401 — registers tools on import


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
