---
description: "Slack 스레드 액션 아이템 추출"
argument-hint: "<Slack-Thread-URL>"
allowed-tools: ["mcp__slack__slack_get_thread_replies", "mcp__slack__slack_get_user_profile", "mcp__slack__slack_get_channel_info", "Read", "Write"]
model: sonnet
---

# Slack 스레드 액션 아이템 추출기

사용자가 제공한 Slack 스레드 URL에서 대화 내용을 가져와 액션 아이템을 추출합니다.

## 입력

사용자가 제공하는 인자: `$ARGUMENTS`

## 실행 순서

### Step 1: URL 파싱

`$ARGUMENTS`에서 Slack 스레드 URL을 파싱합니다.

**URL 형식**: `https://{workspace}.slack.com/archives/{CHANNEL_ID}/p{TIMESTAMP}`

파싱 규칙:
- `CHANNEL_ID`: `/archives/` 뒤의 경로 세그먼트 (예: `C0123456789`)
- `thread_ts`: `p` 뒤의 숫자에서 **뒤에서 6자리 앞에 `.`을 삽입**
  - 예: `p1710000000123456` → `1710000000.123456`

URL이 유효하지 않으면 사용자에게 올바른 형식을 안내합니다.

### Step 2: 스레드 대화 로드

`mcp__slack__slack_get_thread_replies` 도구를 호출합니다:
- `channel`: 파싱한 CHANNEL_ID
- `thread_ts`: 파싱한 thread_ts

### Step 3: 참여자 이름 확인

대화에 등장하는 각 고유 사용자 ID에 대해 `mcp__slack__slack_get_user_profile`을 호출합니다.
- 동일한 사용자 ID는 한 번만 조회합니다.
- display_name이 있으면 display_name, 없으면 real_name을 사용합니다.

### Step 4: 대화 분석 및 액션 아이템 추출

가져온 대화 내용을 분석하여 다음을 추출합니다:

1. **논의 내용 요약** (3~5문장)
2. **결정 사항** (번호 목록)
3. **액션 아이템** (표 형식):
   - 담당자 (실제 이름)
   - 할 일 (구체적 설명)
   - 기한 (명시되지 않으면 "미정")
   - 우선순위 (높음/중간/낮음)

### Step 5: 결과 출력

다음 형식으로 출력합니다:

```
## 📋 스레드 요약

**채널**: #{channel_name}
**참여자**: {참여자 이름 목록}
**날짜**: {스레드 시작 날짜}

### 논의 내용
{요약}

### 결정 사항
1. ...

### 액션 아이템
| # | 담당자 | 할 일 | 기한 | 우선순위 |
|---|--------|-------|------|----------|
| 1 | @이름 | 할 일 | 기한 | 우선순위 |
```

### Step 6: 결과 저장

결과를 파일로 저장합니다:
- 경로: `~/.slackbot/{CHANNEL_ID}/{thread_ts}/README.md`
- `Write` 도구를 사용하여 저장합니다.
- 저장 완료 후 파일 경로를 사용자에게 알려줍니다.

## 에러 처리

- URL 파싱 실패: "올바른 Slack 스레드 URL을 입력해주세요. 형식: https://xxx.slack.com/archives/CHANNEL_ID/pTIMESTAMP"
- MCP 호출 실패: "Slack MCP 서버 연결에 실패했습니다. SLACK_BOT_TOKEN이 .env에 설정되어 있는지 확인하세요."
- 빈 스레드: "해당 스레드에 대화 내용이 없습니다."
