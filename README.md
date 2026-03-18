# Slackbot — Slack 스레드 액션 아이템 추출기

Slack 스레드 URL을 붙여넣으면 대화를 자동 분석하여 **논의 내용, 결정 사항, 액션 아이템**을 추출해주는 Claude Code 플러그인입니다.

## 이런 분에게 추천합니다

- 긴 Slack 스레드를 다시 읽기 귀찮은 분
- 회의 후 액션 아이템을 깔끔하게 정리하고 싶은 분
- 스레드에서 "누가 뭘 하기로 했더라?" 를 자주 찾는 분
- 팀 내 논의 히스토리를 체계적으로 아카이빙하고 싶은 분

## 주요 기능

- **자동 스레드 분석**: Slack 스레드 URL만 붙여넣으면 전체 대화를 가져와 AI가 분석
- **참여자 자동 매핑**: 사용자 ID를 실제 이름으로 변환하여 가독성 높은 결과 제공
- **구조화된 요약**: 논의 내용, 결정 사항, 액션 아이템(담당자/기한/우선순위)을 테이블로 정리
- **원본 대화록 보존**: 분석 결과와 함께 원본 대화를 마크다운으로 저장
- **로컬 저장**: 결과를 `~/.slackbot/` 에 채널/스레드별로 자동 저장하여 나중에 참조 가능

## 사용법

### 1. 설치

```bash
claude plugins add git@github.com:asnisum/slackbot.git
```

### 2. Slack App 설정

[Slack App 설정 가이드](docs/slack-app-setup.md)를 따라 User Token을 발급받고 `.env` 파일에 설정합니다.

```bash
# 플러그인 디렉토리에 .env 파일 생성
SLACK_BOT_TOKEN=xoxp-your-token-here
```

### 3. 사용

**방법 A**: 슬래시 커맨드 사용

```
/slackbot:actions https://your-workspace.slack.com/archives/C0123456/p1234567890123456
```

**방법 B**: Slack 스레드 URL을 그냥 붙여넣기 — 자동으로 분석이 시작됩니다.

### 4. 결과 확인

분석이 완료되면 다음 파일이 생성됩니다:

```
~/.slackbot/{channel-id}/{thread-ts}/
├── README.md          # 요약 + 액션 아이템
└── conversation.md    # 원본 대화록
```

## 출력 예시

```markdown
## 📋 스레드 요약

**채널**: #project-discussion
**참여자**: 홍길동, 김철수, 이영희
**날짜**: 2026-03-18

### 논의 내용
API 스펙 변경에 따른 클라이언트 수정 범위 논의...

### 결정 사항
1. v2 API로 마이그레이션 진행
2. 하위호환 유지 기간 2주

### 액션 아이템
| # | 담당자 | 할 일 | 기한 | 우선순위 |
|---|--------|-------|------|----------|
| 1 | @홍길동 | API v2 스펙 문서 업데이트 | 2026-03-22 | 높음 |
| 2 | @김철수 | 클라이언트 마이그레이션 PR 생성 | 2026-03-25 | 높음 |
```

## 버전 관리

이 프로젝트는 [Semantic Versioning](https://semver.org/)을 따릅니다. 변경 내역은 [CHANGELOG.md](CHANGELOG.md)를 참고하세요.

```bash
# 플러그인 업데이트
claude plugins update slackbot
```

## 요구사항

- Claude Code CLI
- Python 3.10+
- Slack User Token (`xoxp-`)

## 라이선스

MIT
