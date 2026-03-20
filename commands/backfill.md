---
description: "Slack 채널 과거 대화 일괄 수집 (최대 3개월)"
argument-hint: "<채널URL 또는 채널ID> [시작날짜] [종료날짜]"
allowed-tools: ["mcp__slack__slack_get_channel_messages", "mcp__slack__slack_get_thread_replies", "mcp__slack__slack_get_user_profile", "mcp__slack__slack_get_channel_info", "Read", "Write"]
model: sonnet
---

# Slack 채널 과거 대화 일괄 수집기

특정 Slack 채널의 과거 대화를 날짜별로 일괄 수집합니다. 각 날짜에 대해 `/slackbot:daily`와 동일한 저장 형식을 사용합니다.

## 입력

사용자가 제공하는 인자: `$ARGUMENTS`

- 첫 번째 인자: 채널 URL (`https://{workspace}.slack.com/archives/{CHANNEL_ID}`) 또는 채널 ID
- 두 번째 인자 (선택): 시작 날짜 (기본: 3개월 전, `YYYY-MM-DD`)
- 세 번째 인자 (선택): 종료 날짜 (기본: 어제, `YYYY-MM-DD`)

## 실행 순서

### Step 1: 입력 파싱 및 검증

`$ARGUMENTS`에서 채널 ID, 시작일, 종료일을 추출합니다.

**채널 ID 추출**:
- URL 형식인 경우: `/archives/` 뒤의 경로 세그먼트에서 채널 ID 추출
- ID 형식인 경우: 그대로 사용

**날짜 범위 결정**:
- 시작일 미입력 시: 오늘로부터 3개월(90일) 전
- 종료일 미입력 시: 어제

**검증**:
- 시작일이 종료일보다 뒤이면 에러
- 범위가 90일을 초과하면: "최대 90일까지만 수집 가능합니다. 범위를 조정해주세요."
- 시작일이 미래이면 에러

### Step 2: 채널 정보 조회

`mcp__slack__slack_get_channel_info`를 호출하여 채널 이름을 확인합니다.

### Step 3: 기존 데이터 확인

`~/.slackbot/{CHANNEL_ID}/daily/` 디렉토리에서 이미 수집된 날짜를 확인합니다.

- 각 날짜 디렉토리의 `metadata.json`이 있으면 수집 완료로 간주
- 미수집 날짜만 처리 대상으로 분류
- "전체 {N}일 중 {M}일 이미 수집됨. {K}일 수집 예정." 안내

### Step 4: 날짜별 순차 수집

시작일부터 종료일까지 **하루씩** 순차 처리합니다. 각 날짜에 대해:

#### 4-1. 타임스탬프 변환
- `oldest`: 해당 날짜 00:00:00 KST → Unix timestamp
- `latest`: 해당 날짜 23:59:59 KST → Unix timestamp

#### 4-2. 채널 메시지 수집
- `mcp__slack__slack_get_channel_messages` 호출
- 메시지가 없으면 `metadata.json`만 저장 (`message_count: 0`) 후 다음 날짜로

#### 4-3. 스레드 수집
- `reply_count >= 1`인 메시지에 대해 `mcp__slack__slack_get_thread_replies` 호출
- 이미 `~/.slackbot/{CHANNEL_ID}/{thread_ts}/metadata.json`이 있는 스레드는 건너뜀

#### 4-4. 사용자 프로필 조회
- 새로 등장한 사용자 ID만 조회 (전체 기간 캐싱 — 같은 ID 중복 조회 안 함)

#### 4-5. 분석 및 저장
daily 커맨드와 동일한 형식으로 저장:
- `~/.slackbot/{CHANNEL_ID}/daily/{YYYY-MM-DD}/conversation.md` — 채널 메시지 원본 + 스레드 참조
- `~/.slackbot/{CHANNEL_ID}/daily/{YYYY-MM-DD}/README.md` — 일별 요약
- `~/.slackbot/{CHANNEL_ID}/daily/{YYYY-MM-DD}/metadata.json` — 메타데이터 (thread_ids 포함)
- `~/.slackbot/{CHANNEL_ID}/{thread_ts}/` — 각 스레드 개별 저장

#### 4-6. 진행 표시
매일 완료 시 출력:
```
✅ {YYYY-MM-DD} 완료 (메시지 {N}개, 스레드 {M}개) [{current}/{total}]
```

### Step 5: 최종 요약

모든 날짜 수집 완료 후 요약을 출력합니다:

```
## 📦 일괄 수집 완료

**채널**: #{channel_name}
**기간**: {시작일} ~ {종료일}
**수집 결과**:
- 수집 완료: {N}일
- 건너뜀 (이미 수집): {M}일
- 메시지 없음: {K}일
- 전체 메시지: {총 메시지 수}개
- 전체 스레드: {총 스레드 수}개

저장 위치: ~/.slackbot/{CHANNEL_ID}/
```

## 중단/재개

- `metadata.json`이 있는 날짜는 자동으로 건너뜁니다.
- 중단 후 같은 명령을 다시 실행하면 미수집 날짜부터 이어서 수집합니다.
- 특정 날짜를 강제로 다시 수집하려면 해당 날짜의 `metadata.json`을 삭제하세요.

## 에러 처리

- 채널 ID 파싱 실패: "채널 URL 또는 채널 ID를 입력해주세요."
- 날짜 범위 초과: "최대 90일까지만 수집 가능합니다."
- MCP 호출 실패: "Slack MCP 서버 연결에 실패했습니다. SLACK_BOT_TOKEN이 .env에 설정되어 있는지 확인하세요."
- 특정 날짜 수집 실패: 에러를 기록하고 다음 날짜로 진행합니다.
