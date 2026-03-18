---
description: "Slack 채널 일별 대화 수집 및 요약"
argument-hint: "<채널URL 또는 채널ID> [날짜]"
allowed-tools: ["mcp__slack__slack_get_channel_messages", "mcp__slack__slack_get_user_profile", "mcp__slack__slack_get_channel_info", "Read", "Write"]
model: sonnet
---

# Slack 채널 일별 대화 수집기

특정 Slack 채널의 특정 날짜 대화를 수집하고 요약합니다.

## 입력

사용자가 제공하는 인자: `$ARGUMENTS`

- 첫 번째 인자: 채널 URL (`https://{workspace}.slack.com/archives/{CHANNEL_ID}`) 또는 채널 ID (`C0123456789`)
- 두 번째 인자 (선택): 날짜
  - 미입력 시: 오늘
  - `오늘`: 오늘
  - `어제`: 어제
  - `YYYY-MM-DD`: 특정 날짜

## 실행 순서

### Step 1: 입력 파싱

`$ARGUMENTS`에서 채널 ID와 날짜를 추출합니다.

**채널 ID 추출**:
- URL 형식인 경우: `/archives/` 뒤의 경로 세그먼트에서 채널 ID 추출
- ID 형식인 경우: 그대로 사용

**날짜 결정**:
- 인자가 없거나 `오늘`이면: 오늘 날짜 사용
- `어제`이면: 어제 날짜 사용
- `YYYY-MM-DD` 형식이면: 해당 날짜 사용

### Step 2: 타임스탬프 변환

결정된 날짜를 KST 기준 Unix timestamp로 변환합니다:
- `oldest`: 해당 날짜 00:00:00 KST → Unix timestamp (UTC-9시간 = 전날 15:00 UTC)
- `latest`: 해당 날짜 23:59:59 KST → Unix timestamp (UTC-9시간 = 당일 14:59:59 UTC)

예: 2026-03-18 KST
- oldest: 2026-03-17T15:00:00Z → `1773975600.000000`
- latest: 2026-03-18T14:59:59Z → `1774061999.999999`

### Step 3: 채널 정보 조회

`mcp__slack__slack_get_channel_info`를 호출하여 채널 이름을 확인합니다.

### Step 4: 채널 메시지 수집

`mcp__slack__slack_get_channel_messages`를 호출합니다:
- `channel`: 채널 ID
- `oldest`: Step 2에서 계산한 시작 timestamp
- `latest`: Step 2에서 계산한 종료 timestamp

메시지가 없으면: "해당 날짜에 대화 내용이 없습니다." 안내 후 종료합니다.

### Step 5: 참여자 이름 확인

메시지에 등장하는 각 고유 사용자 ID에 대해 `mcp__slack__slack_get_user_profile`을 호출합니다.
- 동일한 사용자 ID는 한 번만 조회합니다.

### Step 6: 대화 분석 및 요약

수집한 대화를 분석하여 다음을 추출합니다:

1. **주요 논의 토픽**: 대화를 토픽별로 분류하여 정리
2. **참여자별 주요 발언**: 각 참여자가 어떤 주제에 기여했는지
3. **결정 사항**: 합의되거나 결정된 내용
4. **액션 아이템**: 누가 무엇을 해야 하는지

### Step 7: 결과 출력

다음 형식으로 출력합니다:

```
## 📅 채널 일별 요약

**채널**: #{channel_name}
**날짜**: {YYYY-MM-DD}
**참여자**: {참여자 이름 목록}
**메시지 수**: {전체 메시지 수}

### 주요 논의 토픽

#### 1. {토픽 제목}
{토픽 요약 - 2~3문장}
- 관련 참여자: @이름1, @이름2

#### 2. {토픽 제목}
...

### 결정 사항
1. {결정 사항}

### 액션 아이템
| # | 담당자 | 할 일 | 기한 | 우선순위 |
|---|--------|-------|------|----------|
| 1 | @이름 | 할 일 | 기한 | 우선순위 |
```

### Step 8: 결과 저장

결과를 파일로 저장합니다:

#### 8-1. 원본 대화록 저장
- 경로: `~/.slackbot/{CHANNEL_ID}/daily/{YYYY-MM-DD}/conversation.md`
- 참여자 이름이 매핑된 원본 대화를 시간순으로 정리
- 스레드가 있는 메시지(`reply_count` >= 1)는 답글 수와 스레드 링크를 표기:
  `💬 스레드 답글 {N}개 — [스레드 보기](https://{workspace}.slack.com/archives/{CHANNEL_ID}/p{ts에서 . 제거})`

#### 8-2. 분석 결과 저장
- 경로: `~/.slackbot/{CHANNEL_ID}/daily/{YYYY-MM-DD}/README.md`

#### 8-3. 메타데이터 저장
- 경로: `~/.slackbot/{CHANNEL_ID}/daily/{YYYY-MM-DD}/metadata.json`

```json
{
  "last_analyzed_at": "{현재 시각 ISO 8601 KST}",
  "channel_id": "{CHANNEL_ID}",
  "date": "{YYYY-MM-DD}",
  "message_count": {전체 메시지 수}
}
```

#### 8-4. 저장 완료 안내
- 저장 완료 후 파일 경로를 사용자에게 알려줍니다.

## 에러 처리

- 채널 ID 파싱 실패: "채널 URL 또는 채널 ID를 입력해주세요. 형식: https://xxx.slack.com/archives/CHANNEL_ID 또는 C0123456789"
- 날짜 형식 오류: "날짜 형식이 올바르지 않습니다. YYYY-MM-DD, 오늘, 어제 중 하나를 입력해주세요."
- MCP 호출 실패: "Slack MCP 서버 연결에 실패했습니다. SLACK_BOT_TOKEN이 .env에 설정되어 있는지 확인하세요."
- 메시지 없음: "해당 날짜({YYYY-MM-DD})에 #{channel_name} 채널의 대화 내용이 없습니다."
