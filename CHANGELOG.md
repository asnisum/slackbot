# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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
