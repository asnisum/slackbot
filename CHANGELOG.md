# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.3.0] - 2026-03-19

### Added

- 스레드 포함 일별 수집: `/slackbot:daily`가 스레드 답글도 수집하여 개별 `{thread_ts}/` 디렉토리에 저장
- 일괄 수집 커맨드: `/slackbot:backfill` — 최대 90일 과거 데이터 일괄 수집, 중단/재개 지원
- 업무 분석 커맨드: `/slackbot:analysis` — 로컬 데이터 기반 팀/개인/프로젝트별 업무 분석
- 업무 분석 스킬: `slack-analysis` — "업무 분석", "팀 현황" 등 자연어 트리거
- 자동 수집 스케줄: `/slackbot:schedule` — CronCreate 기반 평일 자동 수집 설정
- 분리 저장 구조: daily는 채널 메시지 + 스레드 참조, 스레드는 개별 디렉토리
- daily metadata.json에 `thread_ids`, `thread_count`, `total_reply_count` 필드 추가
- 스레드 metadata.json에 `date`, `channel_id`, `parent_message_preview` 필드 추가
- analysis 결과 저장: `~/.slackbot/{CHANNEL_ID}/analysis/{YYYY-MM-DD}/README.md`

### Changed

- daily conversation.md에서 스레드 링크가 Slack URL 대신 로컬 디렉토리 참조로 변경
- daily 커맨드의 `allowed-tools`에 `mcp__slack__slack_get_thread_replies` 추가

## [0.2.0] - 2026-03-18

### Added

- 스레드 업데이트 기능: 이미 분석한 스레드 재분석 시 기존 README를 날짜별 백업
- `metadata.json` 도입: 분석 메타데이터 (마지막 분석 시각, 마지막 메시지 ts, 메시지 수) 저장
- 채널 일별 대화 수집 기능: 특정 채널의 특정 날짜 대화를 수집/분석
- `slack_get_channel_messages` MCP 도구: `conversations.history` API 기반 채널 메시지 조회
- `/slackbot:daily` 슬래시 커맨드: 채널 일별 대화 수집 및 요약
- `slack-daily` 스킬: "채널 오늘 대화", "daily summary" 등 자연어 트리거

## [0.1.0] - 2026-03-18

### Added

- Slack 스레드 대화 분석 및 액션 아이템 추출 기능
- 로컬 Python Slack MCP 서버 (`slack_get_thread_replies`, `slack_get_user_profile`, `slack_get_channel_info`)
- `/slackbot:actions` 슬래시 커맨드
- Slack URL 자동 감지 스킬
- 분석 결과 `~/.slackbot/` 에 자동 저장 (요약 + 원본 대화록)
- User Token (`xoxp-`) 기반 인증 가이드
