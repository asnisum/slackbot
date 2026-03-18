# Slack App 생성 및 User Token 발급 가이드

로컬 Slack MCP 서버를 위한 Slack App 설정 가이드입니다.

## 1. Slack App 생성

1. [Slack API Apps](https://api.slack.com/apps) 페이지 접속
2. **"Create New App"** 클릭
3. **"From scratch"** 선택
4. 설정:
   - **App Name**: `slackbot-local` (원하는 이름)
   - **Workspace**: 사용할 워크스페이스 선택
5. **"Create App"** 클릭

## 2. User Token Scopes 추가

1. 왼쪽 메뉴에서 **"OAuth & Permissions"** 클릭
2. **"Scopes"** 섹션 → **"User Token Scopes"** → **"Add an OAuth Scope"** 클릭
3. 아래 스코프를 모두 추가:

| Scope | 용도 |
|-------|------|
| `channels:history` | 공개 채널 메시지 읽기 |
| `channels:read` | 공개 채널 정보 조회 |
| `groups:history` | 비공개 채널 메시지 읽기 |
| `groups:read` | 비공개 채널 정보 조회 |
| `users:read` | 사용자 프로필 조회 |

> Bot Token Scopes가 아닌 **User Token Scopes**에 추가해야 합니다. User Token은 봇을 채널에 초대하지 않아도 본인이 접근 가능한 모든 채널의 메시지를 읽을 수 있습니다.

## 3. 워크스페이스에 설치

1. 같은 페이지 상단의 **"Install to Workspace"** 클릭
2. 권한 승인 화면에서 **"Allow"** 클릭
3. **User OAuth Token** 을 복사 (`xoxp-`로 시작하는 토큰)

## 4. 토큰 설정

프로젝트 루트의 `.env` 파일에 토큰을 저장합니다:

```bash
SLACK_BOT_TOKEN=xoxp-your-token-here
```

> `.env` 파일은 `.gitignore`에 포함되어 있으므로 토큰이 저장소에 커밋되지 않습니다.

## 주의사항

- User Token은 본인 계정의 권한으로 동작하므로, 본인이 참여 중인 채널의 스레드를 별도 초대 없이 읽을 수 있습니다
- 토큰은 절대 코드나 저장소에 직접 포함하지 마세요
- 토큰이 노출된 경우 즉시 "OAuth & Permissions" 페이지에서 **"Rotate Token"** 으로 재발급하세요
