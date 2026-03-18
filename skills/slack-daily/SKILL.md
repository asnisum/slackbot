---
name: slack-daily
description: >
  This skill should be used when the user asks for a daily channel summary,
  or mentions "채널 오늘 대화", "오늘 뭐 얘기했어", "daily summary",
  "채널 요약", "일별 대화", or provides a channel URL with a date.
version: 1.0.0
---

# Slack 채널 일별 대화 수집

사용자가 특정 채널의 특정 날짜 대화를 요약해달라고 요청하면 이 스킬이 자동으로 트리거됩니다.

## 트리거 조건

- "채널 오늘 대화 정리해줘"
- "daily summary"
- "오늘 뭐 얘기했어"
- "어제 대화 요약"
- 채널 URL + 날짜 언급 (예: "C09GA007AFK 오늘")

## 워크플로우

### 1. 입력 파싱

사용자 메시지에서 채널 ID(또는 URL)와 날짜를 추출합니다.

**채널 ID 추출**:
- Slack 채널 URL에서 추출: `https://{workspace}.slack.com/archives/{CHANNEL_ID}` → `CHANNEL_ID`
- 채널 ID 직접 언급: `C0123456789` 형태
- 채널 ID를 알 수 없는 경우 사용자에게 물어봅니다.

**날짜 결정**:
- "오늘", "today" → 오늘
- "어제", "yesterday" → 어제
- `YYYY-MM-DD` 형식 → 해당 날짜
- 날짜 미언급 → 오늘로 간주

### 2. 타임스탬프 변환

결정된 날짜를 KST 기준 Unix timestamp로 변환합니다:
- `oldest`: 해당 날짜 00:00:00 KST
- `latest`: 해당 날짜 23:59:59 KST

### 3. 채널 정보 조회

`mcp__slack__slack_get_channel_info`를 호출하여 채널 이름을 확인합니다.

### 4. 채널 메시지 수집

`mcp__slack__slack_get_channel_messages`를 호출합니다:
- `channel`: 채널 ID
- `oldest`: 시작 timestamp
- `latest`: 종료 timestamp

메시지가 없으면 사용자에게 안내 후 종료합니다.

### 5. 참여자 이름 확인

메시지에 등장하는 각 고유 사용자 ID에 대해 `mcp__slack__slack_get_user_profile`을 호출합니다.
- 동일한 사용자 ID는 한 번만 조회합니다.

### 6. 대화 분석 및 요약

수집한 대화를 토픽별로 분류하여 분석합니다:

- **주요 논의 토픽**: 대화 흐름을 주제별로 정리
- **참여자별 주요 발언**: 각 참여자의 기여
- **결정 사항**: 합의되거나 결정된 내용
- **액션 아이템**: 누가 무엇을 해야 하는지

### 7. 결과 출력

다음 형식으로 결과를 출력합니다:

```markdown
## 📅 채널 일별 요약

**채널**: #{channel_name}
**날짜**: {YYYY-MM-DD}
**참여자**: {참여자 이름 목록}
**메시지 수**: {전체 메시지 수}

### 주요 논의 토픽

#### 1. {토픽 제목}
{토픽 요약 - 2~3문장}
- 관련 참여자: @이름1, @이름2

### 결정 사항
1. {결정 사항}

### 액션 아이템
| # | 담당자 | 할 일 | 기한 | 우선순위 |
|---|--------|-------|------|----------|
| 1 | @이름 | 할 일 | 기한 | 우선순위 |
```

### 8. 결과 저장

`~/.slackbot/{channel-id}/daily/{YYYY-MM-DD}/` 디렉토리에 저장합니다:

#### 8-1. 원본 대화록 (`conversation.md`)

참여자 이름이 매핑된 원본 대화를 시간순으로 정리하여 저장합니다.

```markdown
# 원본 대화록

**채널**: #{channel_name}
**날짜**: {YYYY-MM-DD}

---

**[HH:MM] 이름(Name)**
메시지 내용
💬 스레드 답글 3개 — [스레드 보기](https://{workspace}.slack.com/archives/{CHANNEL_ID}/p{ts})

---
```

- 각 메시지의 타임스탬프를 `HH:MM` (KST) 형식으로 변환합니다.
- `<@U12345>` 형태의 멘션을 `@이름`으로 치환합니다.
- 메시지에 `reply_count`가 1 이상이면 스레드 답글 수와 스레드 링크를 표기합니다.
  - 스레드 링크 형식: `https://{workspace}.slack.com/archives/{CHANNEL_ID}/p{ts에서 . 제거}`

#### 8-2. 분석 결과 (`README.md`)

7단계에서 생성한 요약을 저장합니다.

#### 8-3. 메타데이터 (`metadata.json`)

```json
{
  "last_analyzed_at": "2026-03-18T15:10:00+09:00",
  "channel_id": "{CHANNEL_ID}",
  "date": "{YYYY-MM-DD}",
  "message_count": 42
}
```

- 저장 후 파일 경로를 사용자에게 알려줍니다.

## 주의사항

- 한국어와 영어가 혼합된 대화를 모두 처리할 수 있어야 합니다.
- 결과는 항상 한국어로 출력합니다.
- 메시지가 매우 많은 경우 (200개 이상) 토픽별 정리가 특히 중요합니다.
- 스레드 답글 내용은 수집하지 않고 채널 레벨 메시지만 수집합니다. 스레드가 있는 메시지는 답글 수와 스레드 링크를 표기합니다.
