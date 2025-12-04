"""
Game Interface - 청구항 작성 게임

사용자가 청구항을 작성하고 검증받는 게임식 인터페이스입니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime

# Import validators and evaluators
from ..dsl.grammar.claim_validator import ClaimValidator, ClaimType
from ..dsl.logic.evaluator import PatentabilityEvaluator
from ..dsl.vocabulary.patent_law_database import get_patent_law_database


class Difficulty(Enum):
    """난이도"""

    EASY = "easy"  # 쉬움
    NORMAL = "normal"  # 보통
    HARD = "hard"  # 어려움


class GameStatus(Enum):
    """게임 상태"""

    IDLE = "idle"  # 대기 중
    IN_PROGRESS = "in_progress"  # 진행 중
    COMPLETED = "completed"  # 완료
    FAILED = "failed"  # 실패


@dataclass
class GameLevel:
    """게임 레벨"""

    level_id: int
    title: str
    description: str
    difficulty: Difficulty
    target_claims: int  # 작성해야 할 청구항 개수
    time_limit: int = 300  # 초 단위
    success_criteria: Dict[str, any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """레벨 검증"""
        if self.level_id <= 0:
            raise ValueError("level_id는 양수여야 합니다")
        if not self.title or not self.title.strip():
            raise ValueError("title은 비어있지 않아야 합니다")
        if self.target_claims <= 0:
            raise ValueError("target_claims는 양수여야 합니다")

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return f"GameLevel(level_id={self.level_id}, title='{self.title}')"

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return f"레벨 {self.level_id}: {self.title} ({self.difficulty.value})"


@dataclass
class PlayerProgress:
    """플레이어 진행 상황"""

    player_name: str
    current_level: int = 1
    completed_levels: List[int] = field(default_factory=list)
    total_score: int = 0
    created_claims: List[str] = field(default_factory=list)
    accuracy: float = 0.0  # 0.0 ~ 1.0

    def __post_init__(self) -> None:
        """플레이어 정보 검증"""
        if not self.player_name or not self.player_name.strip():
            raise ValueError("player_name은 비어있지 않아야 합니다")

    def add_score(self, score: int) -> None:
        """점수 추가"""
        if score < 0:
            raise ValueError("score는 음수가 아니어야 합니다")
        self.total_score += score

    def complete_level(self, level_id: int) -> None:
        """레벨 완료"""
        if level_id not in self.completed_levels:
            self.completed_levels.append(level_id)

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"PlayerProgress(player_name='{self.player_name}', "
            f"current_level={self.current_level}, "
            f"score={self.total_score})"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return f"{self.player_name}: 레벨 {self.current_level}, 점수 {self.total_score}"


@dataclass
class GameSession:
    """게임 세션"""

    session_id: str
    player: PlayerProgress
    current_level: GameLevel
    status: GameStatus = GameStatus.IDLE
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    submitted_claims: List[str] = field(default_factory=list)
    feedback: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """세션 검증"""
        if not self.session_id or not self.session_id.strip():
            raise ValueError("session_id는 비어있지 않아야 합니다")

    def start_game(self, start_time: float) -> None:
        """게임 시작"""
        self.status = GameStatus.IN_PROGRESS
        self.start_time = start_time

    def submit_claim(self, claim: str) -> None:
        """청구항 제출"""
        if not claim or not claim.strip():
            raise ValueError("claim은 비어있지 않아야 합니다")
        self.submitted_claims.append(claim)

    def add_feedback(self, feedback: str) -> None:
        """피드백 추가"""
        if feedback and feedback.strip():
            self.feedback.append(feedback)

    def complete_game(self, end_time: float, success: bool = True) -> None:
        """게임 종료"""
        self.end_time = end_time
        self.status = GameStatus.COMPLETED if success else GameStatus.FAILED

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"GameSession("
            f"session_id='{self.session_id}', "
            f"player='{self.player.player_name}', "
            f"status={self.status.value})"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return (
            f"세션 {self.session_id}: {self.player.player_name} - "
            f"{self.status.value}"
        )


class GameEngine:
    """게임 엔진"""

    def __init__(self) -> None:
        """GameEngine 초기화"""
        self.levels: Dict[int, GameLevel] = {}
        self.sessions: Dict[str, GameSession] = {}
        self.validator = ClaimValidator()
        self.evaluator = PatentabilityEvaluator()
        self.patent_law_db = get_patent_law_database()
        self._create_default_levels()

    def _create_default_levels(self) -> None:
        """기본 레벨 생성"""
        self.levels[1] = GameLevel(
            level_id=1,
            title="기본 청구항 작성",
            description="간단한 독립항을 작성하세요",
            difficulty=Difficulty.EASY,
            target_claims=1,
            time_limit=300,
        )

        self.levels[2] = GameLevel(
            level_id=2,
            title="종속항 작성",
            description="독립항을 기반으로 종속항을 작성하세요",
            difficulty=Difficulty.NORMAL,
            target_claims=3,
            time_limit=600,
        )

        self.levels[3] = GameLevel(
            level_id=3,
            title="복합 청구항 세트",
            description="여러 독립항과 종속항을 포함한 청구항 세트를 작성하세요",
            difficulty=Difficulty.HARD,
            target_claims=5,
            time_limit=900,
        )

    def get_level(self, level_id: int) -> Optional[GameLevel]:
        """레벨 조회"""
        return self.levels.get(level_id)

    def create_session(
        self, session_id: str, player_name: str, level_id: int
    ) -> Optional[GameSession]:
        """게임 세션 생성"""
        level = self.get_level(level_id)
        if level is None:
            raise ValueError(f"유효하지 않은 레벨: {level_id}")

        player = PlayerProgress(player_name=player_name, current_level=level_id)
        session = GameSession(
            session_id=session_id,
            player=player,
            current_level=level,
        )

        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[GameSession]:
        """세션 조회"""
        return self.sessions.get(session_id)

    def evaluate_claims(
        self, session_id: str
    ) -> Tuple[bool, List[str], Dict[str, any]]:
        """청구항 평가 (검증 + 평가 엔진 통합)

        검증 단계:
        1. ClaimValidator로 각 청구항의 문법/구조 검증
        2. PatentabilityEvaluator로 신규성/진보성 평가

        Returns:
            (통과 여부, 피드백 리스트, 상세 결과)
        """
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")

        feedback = []
        details = {
            "total_submitted": len(session.submitted_claims),
            "required": session.current_level.target_claims,
            "validation_results": [],
            "evaluation_results": [],
            "patent_law_references": [],
        }

        # 1단계: 청구항 개수 확인
        if len(session.submitted_claims) < session.current_level.target_claims:
            feedback.append(
                f"⚠️ 청구항 개수 부족: {session.current_level.target_claims}개 필요 "
                f"(현재: {len(session.submitted_claims)}개)"
            )
            success = False
            return success, feedback, details

        feedback.append(
            f"✅ 청구항 {len(session.submitted_claims)}개 제출됨"
        )

        # 2단계: 각 청구항의 문법/구조 검증 (ClaimValidator 사용)
        all_valid = True
        valid_count = 0

        for i, claim in enumerate(session.submitted_claims, 1):
            # 청구항 타입 결정 (첫 번째는 독립항, 나머지는 종속항)
            claim_type = "independent" if i == 1 else "dependent"

            # 검증 실행
            validation_result = self.validator.validate_claim_content(
                claim_number=i,
                claim_type=claim_type,
                content=claim
            )

            details["validation_results"].append({
                "claim_number": i,
                "claim_type": claim_type,
                "is_valid": validation_result.is_valid,
                "errors": [str(e) for e in validation_result.errors],
                "warnings": [str(w) for w in validation_result.warnings],
            })

            if validation_result.is_valid:
                feedback.append(f"✅ 청구항 {i}: 검증 통과")
                valid_count += 1
            else:
                all_valid = False
                feedback.append(f"❌ 청구항 {i}: 검증 실패")
                for error in validation_result.errors:
                    feedback.append(f"   • {error.message}")
                for warning in validation_result.warnings:
                    feedback.append(f"   ⚠️  {warning.message}")

        # 3단계: 신규성/진보성 평가 (PatentabilityEvaluator 사용)
        if valid_count >= session.current_level.target_claims:
            feedback.append("\n📊 신규성/진보성 평가 진행 중...")

            # 발명 특징 추출 (간단한 키워드 기반)
            invention_features = []
            for claim in session.submitted_claims:
                # 기술적 특징 추출 (더 정교한 파싱 가능)
                features = claim.split()
                invention_features.extend(features)

            # 평가 실행 (tuple 반환: novelty_result, inventive_step_result, overall_opinion)
            novelty_result, inventive_step_result, overall_opinion = self.evaluator.evaluate(
                invention_features=list(set(invention_features)),  # 중복 제거
                technical_field="전자기술",  # 기본값
                prior_art_count=0  # 선행기술 데이터가 없으므로 0
            )

            details["evaluation_results"] = {
                "has_inventive_step": inventive_step_result.has_inventive_step,
                "is_novel": novelty_result.is_novel,
                "level": inventive_step_result.level,
                "reasoning": overall_opinion,
            }

            feedback.append(f"   신규성 평가: {novelty_result}")
            feedback.append(f"   진보성 평가: {inventive_step_result}")

            # 관련 특허법 조항 참조
            patent_law_refs = self.patent_law_db.search_by_requirement("명확성")
            if patent_law_refs:
                feedback.append(f"\n📚 관련 특허법:")
                for ref in patent_law_refs[:3]:  # 최대 3개
                    feedback.append(f"   • {ref.article_number}: {ref.title}")
                    details["patent_law_references"].append({
                        "article_number": ref.article_number,
                        "title": ref.title,
                    })

        # 최종 판정
        success = all_valid and valid_count >= session.current_level.target_claims

        if success:
            feedback.append("\n🎉 모든 검증을 통과했습니다!")
            # 점수 계산 (기본값: 100점 + 보너스)
            bonus = min(50, valid_count * 10)  # 최대 50점
            score = 100 + bonus
            details["score"] = score
            session.player.add_score(score)
        else:
            feedback.append("\n❌ 검증 실패. 다시 시도해주세요.")
            details["score"] = 0

        return success, feedback, details


class GameInterface:
    """게임 사용자 인터페이스"""

    def __init__(self) -> None:
        """GameInterface 초기화"""
        self.engine = GameEngine()

    def display_welcome(self) -> str:
        """환영 메시지 표시"""
        return "=" * 60 + "\n" "🎮 청구항 작성 게임에 오신 것을 환영합니다!\n" "=" * 60

    def display_level_info(self, level: GameLevel) -> str:
        """레벨 정보 표시"""
        return (
            f"\n📋 {level}\n"
            f"설명: {level.description}\n"
            f"필요한 청구항: {level.target_claims}개\n"
            f"시간 제한: {level.time_limit}초\n"
        )

    def display_progress(self, player: PlayerProgress) -> str:
        """플레이어 진행 상황 표시"""
        return (
            f"\n📊 진행 상황\n"
            f"플레이어: {player.player_name}\n"
            f"현재 레벨: {player.current_level}\n"
            f"누적 점수: {player.total_score}\n"
            f"완료한 레벨: {player.completed_levels}\n"
        )

    def display_result(self, success: bool, feedback: List[str], details: Dict) -> str:
        """결과 표시"""
        result_str = "\n" + "=" * 60 + "\n"

        if success:
            result_str += "🎉 축하합니다! 레벨을 통과했습니다!\n"
        else:
            result_str += "❌ 아직 요구사항을 충족하지 못했습니다\n"

        result_str += "=" * 60 + "\n"
        result_str += "📝 피드백:\n"

        for fb in feedback:
            result_str += f"  {fb}\n"

        return result_str
