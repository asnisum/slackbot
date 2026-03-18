# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-03-18

### Added

- Slack 스레드 대화 분석 및 액션 아이템 추출 기능
- 로컬 Python Slack MCP 서버 (`slack_get_thread_replies`, `slack_get_user_profile`, `slack_get_channel_info`)
- `/slackbot:actions` 슬래시 커맨드
- Slack URL 자동 감지 스킬
- 분석 결과 `~/.slackbot/` 에 자동 저장 (요약 + 원본 대화록)
- User Token (`xoxp-`) 기반 인증 가이드
