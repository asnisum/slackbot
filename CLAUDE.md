# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Slackbot — Slack 채널/스레드 대화를 분석하고 업무 현황을 추적하는 Claude Code 플러그인.

## Architecture

```
사용자 → /slackbot:daily <채널> [날짜]      → 일별 수집 (스레드 포함)
       → /slackbot:actions <URL>            → 스레드 액션 아이템 추출
       → /slackbot:backfill <채널> [기간]   → 과거 일괄 수집 (최대 90일)
       → /slackbot:analysis <채널> [기간]   → 업무 분석 (로컬 데이터)
       → /slackbot:schedule <채널> [시각]   → 자동 수집 스케줄
                                       ↓
                             로컬 Slack MCP 서버 (stdio, Python)
                                       ↓
                             slack_get_channel_messages → conversations.history API
                             slack_get_thread_replies   → conversations.replies API
                             slack_get_user_profile     → users.info API
                             slack_get_channel_info     → conversations.info API
                                       ↓
                             AI 분석 → 요약/액션아이템/업무분석
                                       ↓
                             결과 출력 + ~/.slackbot/ 에 저장
```

## Storage Structure

```
~/.slackbot/
└── {CHANNEL_ID}/
    ├── daily/
    │   └── {YYYY-MM-DD}/
    │       ├── README.md          # 일별 요약
    │       ├── conversation.md    # 채널 메시지 원본 + 스레드 참조 링크
    │       └── metadata.json      # thread_ids, thread_count 포함
    ├── {thread_ts}/               # 스레드 개별 저장
    │   ├── README.md              # 스레드 요약
    │   ├── conversation.md        # 스레드 대화 원본
    │   └── metadata.json          # date, parent_message_preview 등
    └── analysis/
        └── {YYYY-MM-DD}/          # 분석 실행 날짜
            └── README.md          # 업무 분석 결과
```

## Plugin Structure

```
slackbot/
├── .claude-plugin/
│   ├── plugin.json              # 플러그인 메타데이터
│   └── marketplace.json         # 마켓플레이스 등록 정보
├── .mcp.json                    # 로컬 Slack MCP 서버 연결
├── skills/
│   ├── slack-actions/
│   │   └── SKILL.md             # Slack URL 감지 시 자동 트리거 스킬
│   ├── slack-daily/
│   │   └── SKILL.md             # 채널 일별 대화 자동 트리거 스킬
│   └── slack-analysis/
│       └── SKILL.md             # 업무 분석 자동 트리거 스킬
├── commands/
│   ├── actions.md               # /slackbot:actions 슬래시 커맨드
│   ├── daily.md                 # /slackbot:daily 슬래시 커맨드
│   ├── backfill.md              # /slackbot:backfill 슬래시 커맨드
│   ├── analysis.md              # /slackbot:analysis 슬래시 커맨드
│   └── schedule.md              # /slackbot:schedule 슬래시 커맨드
└── CLAUDE.md
```

## Usage

1. `/slackbot:actions <Slack-Thread-URL>` — 스레드 액션 아이템 추출
2. `/slackbot:daily <채널> [날짜]` — 일별 대화 수집 및 요약 (스레드 포함)
3. `/slackbot:backfill <채널> [시작일] [종료일]` — 과거 대화 일괄 수집
4. `/slackbot:analysis <채널> [기간] [분석유형]` — 업무 분석
5. `/slackbot:schedule <채널> [시각]` — 자동 수집 스케줄 설정
6. Slack 스레드 URL을 붙여넣으면 자동으로 스킬이 트리거됨

## Notes

- 로컬 Python Slack MCP 서버 사용 (stdio, `src/slack_mcp/`)
- `.env`에 `SLACK_BOT_TOKEN` 설정 필요 (발급 가이드: `docs/slack-app-setup.md`)
- 결과는 `~/.slackbot/` 하위에 저장됨
- analysis 커맨드는 Slack API를 호출하지 않고 로컬 저장 데이터만 사용
- schedule은 Claude Code 세션 내에서만 유효 (세션 종료 시 재설정 필요)
