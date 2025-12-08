"""
Custom Exception Hierarchy

게임 엔진 전체에서 사용할 커스텀 예외 클래스들을 정의합니다.
각 예외는 적절한 HTTP 상태 코드와 함께 정의되어 있습니다.
"""


class GameEngineException(Exception):
    """게임 엔진 전체의 기본 예외 클래스"""

    http_status_code = 500

    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        """예외를 JSON 직렬화 가능한 딕셔너리로 변환"""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


class SessionNotFoundException(GameEngineException):
    """세션 ID를 찾을 수 없을 때 발생"""

    http_status_code = 404

    def __init__(self, session_id: str = None):
        message = f"Session not found: {session_id}" if session_id else "Session not found"
        super().__init__(message, code="SESSION_NOT_FOUND", details={"session_id": session_id})


class ClaimValidationException(GameEngineException):
    """청구항 검증 실패 시 발생"""

    http_status_code = 400

    def __init__(self, message: str, errors: list = None):
        super().__init__(
            message,
            code="CLAIM_VALIDATION_ERROR",
            details={"validation_errors": errors or []},
        )


class EvaluationTimeoutException(GameEngineException):
    """LLM 평가 시간 초과 시 발생"""

    http_status_code = 504

    def __init__(self, message: str = None):
        default_msg = "LLM evaluation timed out. Please try again."
        super().__init__(message or default_msg, code="EVALUATION_TIMEOUT")


class PersistenceException(GameEngineException):
    """세션 저장/로드 실패 시 발생"""

    http_status_code = 500

    def __init__(self, message: str, operation: str = None):
        super().__init__(
            message, code="PERSISTENCE_ERROR", details={"operation": operation}
        )


class RAGQueryException(GameEngineException):
    """RAG 시스템 쿼리 실패 시 발생"""

    http_status_code = 500

    def __init__(self, message: str):
        super().__init__(message, code="RAG_QUERY_ERROR")


class VectorDatabaseException(GameEngineException):
    """벡터 데이터베이스 오류 시 발생"""

    http_status_code = 500

    def __init__(self, message: str, db_type: str = None):
        super().__init__(
            message, code="VECTOR_DB_ERROR", details={"db_type": db_type}
        )


class InvalidRequestException(GameEngineException):
    """잘못된 요청 형식 시 발생"""

    http_status_code = 400

    def __init__(self, message: str, field: str = None):
        super().__init__(
            message, code="INVALID_REQUEST", details={"field": field}
        )


class GameStateException(GameEngineException):
    """게임 상태 오류 시 발생 (예: 잘못된 상태 전이)"""

    http_status_code = 400

    def __init__(self, message: str, current_state: str = None, requested_state: str = None):
        super().__init__(
            message,
            code="INVALID_GAME_STATE",
            details={
                "current_state": current_state,
                "requested_state": requested_state,
            },
        )
