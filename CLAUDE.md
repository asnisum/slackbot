# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Slackbot — Slack 스레드 대화를 분석하여 액션 아이템을 추출하는 Claude Code 플러그인.

## Architecture

```
사용자 → /slackbot:actions <URL>  → Command가 워크플로우 제어
                                       ↓
                             로컬 Slack MCP 서버 (stdio, Python)
                                       ↓
                             slack_get_thread_replies → conversations.replies API
                             slack_get_user_profile  → users.info API
                             slack_get_channel_info  → conversations.info API
                                       ↓
                             AI 분석 → 액션 아이템 추출
                                       ↓
                             결과 출력 + ~/.slackbot/ 에 저장
```

## Plugin Structure

```
slackbot/
├── .claude-plugin/
│   ├── plugin.json              # 플러그인 메타데이터
│   └── marketplace.json         # 마켓플레이스 등록 정보
├── .mcp.json                    # 공식 Slack MCP 서버 연결
├── skills/
│   └── slack-actions/
│       └── SKILL.md             # Slack URL 감지 시 자동 트리거 스킬
├── commands/
│   └── actions.md               # /slackbot:actions 슬래시 커맨드
└── CLAUDE.md
```

## Usage

1. `/slackbot:actions <Slack-Thread-URL>` — 스레드 액션 아이템 추출
2. Slack 스레드 URL을 붙여넣으면 자동으로 스킬이 트리거됨

## Notes

- 로컬 Python Slack MCP 서버 사용 (stdio, `src/slack_mcp/`)
- `.env`에 `SLACK_BOT_TOKEN` 설정 필요 (발급 가이드: `docs/slack-app-setup.md`)
- 결과는 `~/.slackbot/{channel-id}/{thread-ts}/README.md`에 저장됨
