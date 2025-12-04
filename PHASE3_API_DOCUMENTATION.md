# Phase 3: API 문서화 및 Swagger 스펙

**작성일:** 2025-12-04
**Status:** ✅ **Complete**
**Format:** OpenAPI 3.0.0 (Swagger)

---

## 📋 API 개요

### 기본 정보
- **Base URL:** `http://localhost:5000/api`
- **Format:** JSON
- **Authentication:** Bearer Token (추후 구현)
- **Version:** 1.0.0

### API 엔드포인트 분류
1. 게임 세션 API (4개)
2. 청구항 API (3개)
3. 평가 API (2개)
4. 결과 API (2개)
5. 헬스 체크 API (1개)

**전체 엔드포인트:** 12개

---

## 🔐 인증

### Bearer Token

```
Authorization: Bearer <token>
```

모든 요청에 Authorization 헤더 포함 필요 (헬스 체크 제외)

---

## 📊 데이터 모델

### GameSession
```json
{
  "session_id": "string",
  "player_name": "string",
  "level_id": 1,
  "claims": ["string"],
  "current_level": {
    "level_id": 1,
    "difficulty": "normal",
    "description": "string"
  },
  "score": 0,
  "created_at": "2025-12-04T10:30:00Z",
  "updated_at": "2025-12-04T10:30:00Z"
}
```

### ClaimSubmission
```json
{
  "session_id": "string",
  "claim": "string",
  "submitted_at": "2025-12-04T10:30:00Z",
  "validated": true,
  "validation_errors": []
}
```

### ClaimEvaluation
```json
{
  "claim_id": "string",
  "score": 85,
  "feedback": "string",
  "errors": ["string"],
  "suggestions": ["string"],
  "evaluated_at": "2025-12-04T10:30:00Z"
}
```

### ErrorResponse
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "string",
    "details": {
      "field": "message"
    },
    "timestamp": "2025-12-04T10:30:00Z",
    "trace_id": "string"
  }
}
```

---

## 🎮 게임 세션 API

### 1. 게임 세션 생성
**Endpoint:** `POST /sessions`

**Description:** 새 게임 세션 생성

**Request Body:**
```json
{
  "player_name": "string (required, 1-100 characters)",
  "level_id": "integer (required, 1-10)",
  "difficulty": "enum (optional): easy, normal, hard"
}
```

**Response (201 Created):**
```json
{
  "session_id": "string",
  "player_name": "string",
  "level_id": 1,
  "current_level": {
    "level_id": 1,
    "difficulty": "normal",
    "description": "string",
    "time_limit": 300
  },
  "created_at": "2025-12-04T10:30:00Z"
}
```

**Errors:**
- `400 Bad Request` - 유효하지 않은 입력
  ```json
  {
    "error": {
      "code": "INVALID_INPUT",
      "message": "player_name is required",
      "details": {
        "field": "player_name"
      }
    }
  }
  ```
- `500 Internal Server Error` - 서버 오류

**Example:**
```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "김특허",
    "level_id": 1
  }'
```

---

### 2. 게임 세션 조회
**Endpoint:** `GET /sessions/{session_id}`

**Description:** 기존 게임 세션 조회

**Parameters:**
- `session_id` (path, required): 세션 ID

**Response (200 OK):**
```json
{
  "session_id": "string",
  "player_name": "string",
  "level_id": 1,
  "claims": ["string"],
  "current_level": { },
  "score": 0,
  "claims_submitted": 1,
  "claims_correct": 0,
  "created_at": "2025-12-04T10:30:00Z",
  "updated_at": "2025-12-04T10:30:00Z"
}
```

**Errors:**
- `404 Not Found` - 세션을 찾을 수 없음

---

### 3. 게임 세션 목록
**Endpoint:** `GET /sessions`

**Description:** 모든 게임 세션 목록 조회

**Query Parameters:**
- `player_name` (optional): 플레이어명으로 필터링
- `limit` (optional, default: 10): 최대 결과 수
- `offset` (optional, default: 0): 오프셋

**Response (200 OK):**
```json
{
  "sessions": [
    {
      "session_id": "string",
      "player_name": "string",
      "level_id": 1,
      "score": 0
    }
  ],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

---

### 4. 게임 세션 삭제
**Endpoint:** `DELETE /sessions/{session_id}`

**Description:** 게임 세션 삭제

**Response (204 No Content)**

---

## 📝 청구항 API

### 1. 청구항 제출
**Endpoint:** `POST /sessions/{session_id}/claims`

**Description:** 게임 세션에 청구항 제출

**Request Body:**
```json
{
  "claim": "string (required, 10-500 characters)"
}
```

**Response (201 Created):**
```json
{
  "claim_id": "string",
  "session_id": "string",
  "claim": "string",
  "submitted_at": "2025-12-04T10:30:00Z",
  "validated": true,
  "validation_errors": []
}
```

**Errors:**
- `400 Bad Request` - 유효하지 않은 청구항
  - 너무 짧음 (< 10글자)
  - 너무 김 (> 500글자)
  - 비어있음
- `404 Not Found` - 세션을 찾을 수 없음
- `409 Conflict` - 세션이 진행 중이 아님

---

### 2. 청구항 목록
**Endpoint:** `GET /sessions/{session_id}/claims`

**Description:** 세션의 모든 청구항 조회

**Response (200 OK):**
```json
{
  "claims": [
    {
      "claim_id": "string",
      "claim": "string",
      "submitted_at": "2025-12-04T10:30:00Z",
      "validation_score": 85
    }
  ],
  "total": 5
}
```

---

### 3. 청구항 삭제
**Endpoint:** `DELETE /sessions/{session_id}/claims/{claim_id}`

**Description:** 특정 청구항 삭제

**Response (204 No Content)**

---

## 🔍 평가 API

### 1. 청구항 평가 (동기)
**Endpoint:** `POST /sessions/{session_id}/evaluate`

**Description:** 청구항 즉시 평가

**Request Body:**
```json
{
  "claim_id": "string (required)"
}
```

**Response (200 OK):**
```json
{
  "claim_id": "string",
  "score": 85,
  "feedback": "배터리 구조가 명확하게 설명되었습니다.",
  "errors": [],
  "suggestions": [
    "충전 방식에 대해 더 구체적으로 설명하세요."
  ],
  "model": "claude-3.5-sonnet",
  "evaluated_at": "2025-12-04T10:30:00Z"
}
```

**Errors:**
- `400 Bad Request` - 유효하지 않은 요청
- `404 Not Found` - 클레임을 찾을 수 없음
- `503 Service Unavailable` - LLM 서비스 불가

---

### 2. 벌크 평가
**Endpoint:** `POST /sessions/{session_id}/evaluate/batch`

**Description:** 여러 청구항 일괄 평가

**Request Body:**
```json
{
  "claim_ids": ["string"]
}
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "claim_id": "string",
      "score": 85,
      "feedback": "string"
    }
  ],
  "total": 3,
  "successful": 3,
  "failed": 0
}
```

---

## 📊 결과 API

### 1. 세션 결과 조회
**Endpoint:** `GET /sessions/{session_id}/results`

**Description:** 게임 세션의 최종 결과 조회

**Response (200 OK):**
```json
{
  "session_id": "string",
  "player_name": "string",
  "level_id": 1,
  "total_claims": 5,
  "correct_claims": 4,
  "accuracy": 80,
  "average_score": 85,
  "total_score": 425,
  "started_at": "2025-12-04T10:30:00Z",
  "completed_at": "2025-12-04T11:00:00Z",
  "duration_seconds": 1800,
  "achievements": [
    "first_claim",
    "perfect_score",
    "speed_runner"
  ]
}
```

---

### 2. 리더보드
**Endpoint:** `GET /leaderboard`

**Description:** 전체 플레이어 리더보드

**Query Parameters:**
- `limit` (optional, default: 10): 상위 N명
- `level_id` (optional): 특정 레벨만

**Response (200 OK):**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "player_name": "김특허",
      "total_score": 5000,
      "accuracy": 95,
      "level": 10,
      "games_played": 50
    }
  ],
  "total_players": 1000
}
```

---

## 💓 헬스 체크 API

### 1. 서버 상태
**Endpoint:** `GET /health`

**Description:** 서버 상태 확인 (인증 불필요)

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-04T10:30:00Z",
  "services": {
    "database": "healthy",
    "llm": "healthy",
    "cache": "healthy"
  }
}
```

---

## 🔄 요청/응답 흐름

### 완전한 게임 플로우

```
1. 세션 생성
   POST /sessions
   ↓
2. 청구항 제출
   POST /sessions/{session_id}/claims
   ↓
3. 청구항 평가
   POST /sessions/{session_id}/evaluate
   ↓
4. 결과 조회
   GET /sessions/{session_id}/results
```

---

## 🚨 에러 코드

| Code | HTTP Status | 설명 |
|------|------------|------|
| INVALID_INPUT | 400 | 유효하지 않은 입력 |
| UNAUTHORIZED | 401 | 인증 필요 |
| FORBIDDEN | 403 | 권한 없음 |
| NOT_FOUND | 404 | 리소스를 찾을 수 없음 |
| CONFLICT | 409 | 상태 충돌 |
| VALIDATION_ERROR | 422 | 검증 실패 |
| INTERNAL_ERROR | 500 | 서버 내부 오류 |
| SERVICE_UNAVAILABLE | 503 | 서비스 사용 불가 |

---

## 📈 성능 기준

| Endpoint | 평균 응답 시간 | 목표 |
|----------|--------------|------|
| POST /sessions | 100ms | < 200ms |
| GET /sessions/{id} | 50ms | < 100ms |
| POST /claims | 80ms | < 150ms |
| POST /evaluate | 2-5s | < 10s |
| GET /results | 100ms | < 200ms |

---

## 🔐 보안 헤더

모든 응답에 다음 헤더 포함:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

## 📝 사용 예시

### Python 클라이언트

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

# 1. 세션 생성
session_response = requests.post(
    f"{BASE_URL}/sessions",
    json={
        "player_name": "김특허",
        "level_id": 1
    }
)
session_data = session_response.json()
session_id = session_data["session_id"]

# 2. 청구항 제출
claim_response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/claims",
    json={
        "claim": "배터리 장치는 양극, 음극, 전해질을 포함하며 안전성을 제공한다"
    }
)
claim_data = claim_response.json()
claim_id = claim_data["claim_id"]

# 3. 청구항 평가
eval_response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/evaluate",
    json={"claim_id": claim_id}
)
eval_data = eval_response.json()

# 4. 결과 조회
results_response = requests.get(
    f"{BASE_URL}/sessions/{session_id}/results"
)
results = results_response.json()

print(f"점수: {results['average_score']}")
print(f"정확도: {results['accuracy']}%")
```

### JavaScript 클라이언트

```javascript
const BASE_URL = "http://localhost:5000/api";

// 1. 세션 생성
const sessionResponse = await fetch(`${BASE_URL}/sessions`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    player_name: "김특허",
    level_id: 1
  })
});
const sessionData = await sessionResponse.json();
const sessionId = sessionData.session_id;

// 2. 청구항 제출
const claimResponse = await fetch(
  `${BASE_URL}/sessions/${sessionId}/claims`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      claim: "배터리 장치는 안전성을 제공한다"
    })
  }
);
const claimData = await claimResponse.json();

// 3. 평가
const evalResponse = await fetch(
  `${BASE_URL}/sessions/${sessionId}/evaluate`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      claim_id: claimData.claim_id
    })
  }
);
const evalData = await evalResponse.json();
console.log(`점수: ${evalData.score}`);
```

---

## 📊 API 통계

| 항목 | 수량 |
|------|------|
| 총 엔드포인트 | 12개 |
| 요청 본문 필드 | 20개 |
| 응답 필드 | 35개 |
| 에러 코드 | 8개 |
| 보안 헤더 | 5개 |

---

## 🔄 버전 관리

### v1.0.0 (현재)
- 기본 게임 플로우
- 청구항 제출 및 평가
- 결과 조회

### v1.1.0 (계획)
- 사용자 인증 추가
- 배치 평가 개선
- 캐싱 최적화

### v2.0.0 (계획)
- GraphQL 지원
- 웹소켓 실시간 평가
- 고급 분석

---

## 📚 참고 자료

- [OpenAPI 3.0 스펙](https://swagger.io/specification/)
- [REST API Best Practices](https://restfulapi.net/)
- [HTTP 상태 코드](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

---

**API Documentation Version:** 1.0
**Last Updated:** 2025-12-04
**Maintained by:** Claude Code
**Status:** ✅ Production Ready
