---
description: "Slack 채널 자동 일별 수집 스케줄 설정"
argument-hint: "<채널URL 또는 채널ID> [시각]"
allowed-tools: ["CronCreate", "CronDelete", "CronList"]
model: sonnet
---

# Slack 채널 자동 수집 스케줄

특정 Slack 채널의 일별 대화를 자동으로 수집하는 스케줄을 설정합니다.

## 입력

사용자가 제공하는 인자: `$ARGUMENTS`

- 첫 번째 인자: 채널 URL (`https://{workspace}.slack.com/archives/{CHANNEL_ID}`) 또는 채널 ID
- 두 번째 인자 (선택): 실행 시각 (기본: `23:50`, KST 기준, 24시간 형식)

## 실행 순서

### Step 1: 입력 파싱

`$ARGUMENTS`에서 채널 ID와 실행 시각을 추출합니다.

**채널 ID 추출**:
- URL 형식인 경우: `/archives/` 뒤의 경로 세그먼트에서 채널 ID 추출
- ID 형식인 경우: 그대로 사용

**시각 결정**:
- 미입력 시: 23:50 KST (기본)
- `HH:MM` 형식: 해당 시각 사용

### Step 2: 기존 스케줄 확인

`CronList`를 호출하여 해당 채널에 대한 기존 스케줄이 있는지 확인합니다.
- 이미 등록된 스케줄이 있으면: "기존 스케줄이 있습니다. 교체하시겠습니까?" 안내

### Step 3: 스케줄 등록

`CronCreate`를 호출하여 cron 작업을 등록합니다:

- **cron 표현식**: KST 시각을 UTC로 변환하여 설정
  - 예: KST 23:50 → UTC 14:50 → `50 14 * * 1-5` (평일만)
- **prompt**: `/slackbot:daily {CHANNEL_ID} 오늘`

### Step 4: 등록 확인

`CronList`로 등록이 완료되었는지 확인합니다.

### Step 5: 결과 안내

```
## ⏰ 자동 수집 스케줄 설정 완료

**채널**: {CHANNEL_ID}
**실행 시각**: 매 평일 {HH:MM} KST
**수집 명령**: /slackbot:daily {CHANNEL_ID} 오늘

⚠️ 참고: 이 스케줄은 Claude Code 세션 내에서만 유효합니다.
세션이 종료되면 스케줄도 함께 종료됩니다.
```

## 스케줄 삭제

`$ARGUMENTS`가 `삭제` 또는 `delete`인 경우:
1. `CronList`로 등록된 스케줄 목록 표시
2. 사용자에게 삭제할 스케줄 확인
3. `CronDelete`로 삭제

## 에러 처리

- 채널 ID 파싱 실패: "채널 URL 또는 채널 ID를 입력해주세요."
- 시각 형식 오류: "시각 형식이 올바르지 않습니다. HH:MM (24시간) 형식으로 입력해주세요."
