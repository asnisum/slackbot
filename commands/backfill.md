---
description: "Slack 채널 과거 대화 일괄 수집 (최대 3개월)"
argument-hint: "<채널URL 또는 채널ID> [시작날짜] [종료날짜]"
allowed-tools: ["mcp__slack__slack_get_channel_messages", "mcp__slack__slack_get_thread_replies", "mcp__slack__slack_get_user_profile", "mcp__slack__slack_get_channel_info", "Read", "Write", "Bash", "Agent", "Glob"]
model: sonnet
---

# Slack 채널 과거 대화 일괄 수집기

특정 Slack 채널의 과거 대화를 날짜별로 일괄 수집합니다. 각 날짜에 대해 `/slackbot:daily`와 동일한 저장 형식을 사용합니다.

## 핵심 원칙

> **원본 먼저 저장, 분석은 로컬 원본 기반**
> 1. MCP API 응답 원본(JSON)을 먼저 디스크에 저장한다
> 2. 모든 가공(conversation.md, README.md 등)은 로컬에 저장된 원본 JSON을 읽어서 수행한다
> 3. API 재호출 없이 원본 데이터로 재분석/재포맷이 가능해야 한다

## 입력

사용자가 제공하는 인자: `$ARGUMENTS`

- 첫 번째 인자: 채널 URL (`https://{workspace}.slack.com/archives/{CHANNEL_ID}`) 또는 채널 ID
- 두 번째 인자 (선택): 시작 날짜 (기본: 3개월 전, `YYYY-MM-DD`)
- 세 번째 인자 (선택): 종료 날짜 (기본: 어제, `YYYY-MM-DD`)

## 저장 구조

```
~/.slackbot/{CHANNEL_ID}/
├── cache/
│   └── users.json                          # 사용자 프로필 캐시
├── daily/
│   └── {YYYY-MM-DD}/
│       ├── raw_messages.json               # ★ MCP 응답 원본 (메시지)
│       ├── conversation.md                 # 포맷팅된 대화 원본
│       ├── README.md                       # 일별 요약
│       └── metadata.json                   # 메타데이터
└── {thread_ts}/
    ├── raw_replies.json                    # ★ MCP 응답 원본 (스레드)
    ├── conversation.md                     # 포맷팅된 스레드 대화
    └── metadata.json                       # 스레드 메타데이터
```

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

### Step 3: 기존 데이터 확인 및 사용자 캐시 로드

`~/.slackbot/{CHANNEL_ID}/daily/` 디렉토리에서 이미 수집된 날짜를 확인합니다.

- 각 날짜 디렉토리의 `raw_messages.json`이 있으면 수집 완료로 간주
- 미수집 날짜만 처리 대상으로 분류
- "전체 {N}일 중 {M}일 이미 수집됨. {K}일 수집 예정." 안내

**사용자 캐시 로드/초기화**:
- `~/.slackbot/{CHANNEL_ID}/cache/users.json` 파일이 있으면 로드
- 없으면 빈 dict로 초기화

### Step 4: 날짜별 순차 수집

시작일부터 종료일까지 **하루씩** 순차 처리합니다. 각 날짜에 대해:

#### 4-1. 타임스탬프 변환
```python
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))
dt = datetime(YYYY, MM, DD, tzinfo=KST)
oldest = int(dt.replace(hour=0, minute=0, second=0).timestamp())
latest = int(dt.replace(hour=23, minute=59, second=59).timestamp())
```

#### 4-2. 채널 메시지 수집 → 원본 즉시 저장
1. `mcp__slack__slack_get_channel_messages` 호출
2. **응답 JSON을 즉시 `raw_messages.json`에 저장**
3. 메시지가 없으면 빈 배열 `[]`로 저장 후 다음 날짜로

```python
# 즉시 저장
with open(f'{day_dir}/raw_messages.json', 'w') as f:
    json.dump(messages, f, ensure_ascii=False, indent=2)
```

#### 4-3. 스레드 수집 → 원본 즉시 저장
- `reply_count >= 1`이고 `thread_ts == ts`인 메시지에 대해 `mcp__slack__slack_get_thread_replies` 호출
- **응답 JSON을 즉시 `{thread_ts}/raw_replies.json`에 저장**
- 이미 `raw_replies.json`이 있는 스레드는 건너뜀
- 대용량 스레드: MCP 결과가 파일로 저장된 경우, 해당 파일을 Read로 읽어서 `raw_replies.json`으로 복사

```python
# 스레드 원본 즉시 저장
thread_dir = f'{base}/{thread_ts}'
os.makedirs(thread_dir, exist_ok=True)
with open(f'{thread_dir}/raw_replies.json', 'w') as f:
    json.dump(replies, f, ensure_ascii=False, indent=2)
```

#### 4-4. 사용자 프로필 조회
- 채널 메시지 + 스레드 답글에서 새로 등장한 사용자 ID만 조회 (캐시에 없는 ID만)
- `mcp__slack__slack_get_user_profile` 호출 후 `display_name` 추출
- 캐시 파일(`cache/users.json`)에 즉시 저장

#### 4-5. 로컬 원본 기반 가공 및 저장

**로컬에 저장된 `raw_messages.json`, `raw_replies.json`을 읽어서** 가공합니다:

1. **스레드 가공** — `{thread_ts}/conversation.md`, `metadata.json`
   - `raw_replies.json`을 읽어서 사용자 이름 치환 후 conversation.md 생성

2. **일별 대화 가공** — `daily/{YYYY-MM-DD}/conversation.md`
   - `raw_messages.json`을 읽어서 사용자 이름 치환 후 conversation.md 생성
   - 스레드 참조 링크 포함

3. **일별 요약** — `daily/{YYYY-MM-DD}/README.md`

4. **메타데이터** — `daily/{YYYY-MM-DD}/metadata.json`

#### 4-6. 진행 표시
```
✅ {YYYY-MM-DD} 완료 (메시지 {N}개, 스레드 {M}개) [{current}/{total}]
```

### Step 5: 최종 요약

```
## 일괄 수집 완료

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

## 병렬 처리 가이드

### 메시지 수집 병렬화
- 채널 메시지는 **7일 단위**로 병렬 호출 가능
- 각 날짜의 `raw_messages.json` 저장은 독립적

### 스레드 수집 병렬화
- 동일 날짜 내 스레드는 **8개씩** 병렬 호출
- 각 스레드의 `raw_replies.json` 저장은 독립적

### 에이전트 활용
- 전체 기간을 **2~3개 에이전트**로 분할 가능
- 에이전트에게 Bash 사용 필요 명시 (settings.json에 `Bash(python3 *)` 허용)
- 에이전트 프롬프트에 **원본 JSON 즉시 저장** 단계를 반드시 포함

## 중단/재개

- `raw_messages.json`이 있는 날짜는 자동으로 건너뜁니다.
- `raw_replies.json`이 있는 스레드는 자동으로 건너뜁니다.
- conversation.md/README.md가 없더라도 원본이 있으면 가공만 재실행하면 됩니다.
- 특정 날짜를 강제로 다시 수집하려면 해당 날짜의 `raw_messages.json`을 삭제하세요.

## 에러 처리

- 채널 ID 파싱 실패: "채널 URL 또는 채널 ID를 입력해주세요."
- 날짜 범위 초과: "최대 90일까지만 수집 가능합니다."
- MCP 호출 실패: "Slack MCP 서버 연결에 실패했습니다."
- MCP 결과 크기 초과: 파일로 저장된 경로에서 Read로 읽어서 raw_replies.json으로 저장
- 에이전트 Bash 권한 거부: settings.json에 permissions 추가 안내
- 특정 날짜 수집 실패: 에러를 기록하고 다음 날짜로 진행
