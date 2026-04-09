---
description: "Slack 채널 일별 대화 수집 및 요약"
argument-hint: "<채널URL 또는 채널ID> [날짜]"
allowed-tools: ["mcp__slack__slack_get_channel_messages", "mcp__slack__slack_get_thread_replies", "mcp__slack__slack_get_user_profile", "mcp__slack__slack_get_channel_info", "Read", "Write"]
model: sonnet
---

# Slack 채널 일별 대화 수집기

특정 Slack 채널의 특정 날짜 대화를 수집하고 요약합니다. 스레드 답글도 개별 디렉토리에 저장합니다.

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

### Step 4: 채널 메시지 수집 → 원본 즉시 저장

`mcp__slack__slack_get_channel_messages`를 호출합니다:
- `channel`: 채널 ID
- `oldest`: Step 2에서 계산한 시작 timestamp
- `latest`: Step 2에서 계산한 종료 timestamp

**응답 JSON을 즉시 `raw_messages.json`에 저장합니다:**
```python
with open(f'{day_dir}/raw_messages.json', 'w') as f:
    json.dump(messages, f, ensure_ascii=False, indent=2)
```

메시지가 없으면: 빈 배열 `[]`로 저장 후 "해당 날짜에 대화 내용이 없습니다." 안내 후 종료합니다.

### Step 4.5: 스레드 수집 → 원본 즉시 저장

채널 메시지 중 `reply_count >= 1`인 메시지를 식별합니다.

**스레드 수집:**
- 각 스레드에 대해 `mcp__slack__slack_get_thread_replies`를 호출합니다:
  - `channel`: 채널 ID
  - `thread_ts`: 해당 메시지의 `ts`
- **응답 JSON을 즉시 `{thread_ts}/raw_replies.json`에 저장합니다**
- 스레드가 10개 이상이면 매 스레드 수집 시 "스레드 {current}/{total} 수집 중..." 진행 표시를 출력합니다.
- 스레드 답글에 등장하는 사용자 ID도 수집하여 Step 5의 프로필 조회 대상에 포함합니다.

**기존 스레드 확인:**
- `~/.slackbot/{CHANNEL_ID}/{thread_ts}/raw_replies.json`이 이미 존재하면:
  - 기존 `README.md`를 `README.{오늘날짜}.md`로 백업
  - 새로 수집한 데이터로 덮어씁니다.

### Step 5: 참여자 이름 확인

채널 메시지와 **스레드 답글 모두**에 등장하는 각 고유 사용자 ID에 대해 `mcp__slack__slack_get_user_profile`을 호출합니다.
- 동일한 사용자 ID는 한 번만 조회합니다.

### Step 6: 로컬 원본 기반 분석 및 요약

**로컬에 저장된 `raw_messages.json`, `raw_replies.json`을 읽어서** 분석합니다.
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
**스레드 수**: {스레드 개수} (답글 총 {N}개)

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
- 스레드가 있는 메시지(`reply_count` >= 1)는 답글 수와 스레드 디렉토리 참조를 표기:
  ```markdown
  **[HH:MM] 이름(Name)**
  메시지 내용
  💬 스레드 답글 {N}개 → [상세 보기](../../{thread_ts}/conversation.md)
  ```

#### 8-2. 분석 결과 저장
- 경로: `~/.slackbot/{CHANNEL_ID}/daily/{YYYY-MM-DD}/README.md`

#### 8-3. 스레드 개별 저장
각 스레드를 `~/.slackbot/{CHANNEL_ID}/{thread_ts}/` 디렉토리에 개별 저장합니다:

**conversation.md** — 스레드 전체 대화:
```markdown
# 원본 대화록

**채널**: #{channel_name}
**스레드 시작**: {YYYY-MM-DD HH:MM}

---

**[YYYY-MM-DD HH:MM] 이름(Name)**
메시지 내용

---
```

**README.md** — 스레드 요약:
```markdown
## 📋 스레드 요약

**채널**: #{channel_name}
**참여자**: {참여자 목록}
**날짜**: {스레드 시작 날짜}

### 논의 내용
{요약}

### 결정 사항
1. ...

### 액션 아이템
| # | 담당자 | 할 일 | 기한 | 우선순위 |
|---|--------|-------|------|----------|
```

**metadata.json**:
```json
{
  "last_analyzed_at": "{현재 시각 ISO 8601 KST}",
  "channel_id": "{CHANNEL_ID}",
  "thread_ts": "{thread_ts}",
  "date": "{YYYY-MM-DD}",
  "message_count": 5,
  "parent_message_preview": "{부모 메시지 앞 50자}"
}
```

#### 8-4. 메타데이터 저장
- 경로: `~/.slackbot/{CHANNEL_ID}/daily/{YYYY-MM-DD}/metadata.json`

```json
{
  "last_analyzed_at": "{현재 시각 ISO 8601 KST}",
  "channel_id": "{CHANNEL_ID}",
  "date": "{YYYY-MM-DD}",
  "message_count": 42,
  "thread_ids": ["1770877819.223349", "1770899999.111111"],
  "thread_count": 2,
  "total_reply_count": 15
}
```

#### 8-5. 저장 완료 안내
- 저장 완료 후 파일 경로를 사용자에게 알려줍니다.
- 스레드가 있었으면 "스레드 {N}개가 개별 디렉토리에 저장되었습니다." 안내합니다.

## 에러 처리

- 채널 ID 파싱 실패: "채널 URL 또는 채널 ID를 입력해주세요. 형식: https://xxx.slack.com/archives/CHANNEL_ID 또는 C0123456789"
- 날짜 형식 오류: "날짜 형식이 올바르지 않습니다. YYYY-MM-DD, 오늘, 어제 중 하나를 입력해주세요."
- MCP 호출 실패: "Slack MCP 서버 연결에 실패했습니다. SLACK_BOT_TOKEN이 .env에 설정되어 있는지 확인하세요."
- 메시지 없음: "해당 날짜({YYYY-MM-DD})에 #{channel_name} 채널의 대화 내용이 없습니다."
