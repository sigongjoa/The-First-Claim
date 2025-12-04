"""
Property-Based Testing - Phase 5

Hypothesis를 이용한 Property-based 테스트입니다.
생성된 임의의 입력으로 불변성(invariant)을 검증합니다.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from src.ui.game import GameEngine, GameStatus, Difficulty
from src.utils.logger import get_logger


logger_instance = get_logger("test_property_based")


class TestPropertyBasedInvariants:
    """불변성 기반 프로퍼티 테스트"""

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        return GameEngine()

    @given(
        session_id=st.text(min_size=1, max_size=100, alphabet="abcdefghijklmnopqrstuvwxyz0123456789_"),
        player_name=st.text(min_size=1, max_size=100, alphabet="가나다라마바사아가나다라마바사아0123456789 "),
        level_id=st.integers(min_value=1, max_value=3)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    def test_session_creation_always_returns_valid_session(self, session_id, player_name, level_id):
        """세션 생성은 항상 유효한 세션을 반환한다"""
        engine = GameEngine()

        try:
            session = engine.create_session(
                session_id=session_id,
                player_name=player_name,
                level_id=level_id
            )

            # 불변성: 세션은 항상 초기 상태여야 함
            assert session is not None
            assert session.session_id == session_id
            assert session.player.player_name == player_name
            assert session.player.current_level == level_id
            assert session.status == GameStatus.IDLE

            # 불변성: 초기 청구항은 항상 0개
            assert len(session.submitted_claims) == 0
            assert len(session.feedback) == 0

        except ValueError as e:
            # 유효하지 않은 입력은 예외 발생
            logger_instance.info(
                "유효하지 않은 입력 감지",
                context={"error": str(e)[:100]}
            )

    @given(
        claim_text=st.text(min_size=30, max_size=1000),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    def test_valid_claim_always_accepted(self, claim_text):
        """유효한 청구항(30-1000자)은 항상 수락된다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="property_valid_001",
            player_name="프로퍼티테스터",
            level_id=1
        )

        initial_count = len(session.submitted_claims)

        # 불변성: 유효한 청구항은 항상 True를 반환
        result = session.submit_claim(claim_text)
        assert result is True

        # 불변성: 클레임 카운트는 정확히 1 증가
        assert len(session.submitted_claims) == initial_count + 1

        # 불변성: 제출된 클레임이 일치
        assert session.submitted_claims[-1] == claim_text

    @given(
        claim_text=st.text(max_size=29),  # 30자 미만
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    def test_invalid_short_claim_always_rejected(self, claim_text):
        """짧은 청구항(< 30자)은 항상 거부된다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="property_invalid_short_001",
            player_name="프로퍼티테스터",
            level_id=1
        )

        initial_count = len(session.submitted_claims)

        # 불변성: 짧은 청구항은 항상 False를 반환
        result = session.submit_claim(claim_text)
        assert result is False

        # 불변성: 클레임 카운트는 변하지 않음
        assert len(session.submitted_claims) == initial_count

    @given(
        score=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100)
    def test_score_accumulation_is_monotonic(self, score):
        """점수 누적은 항상 단조증가한다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="property_score_001",
            player_name="점수테스터",
            level_id=1
        )

        player = session.player
        initial_score = player.total_score

        # 불변성: 점수는 절대 감소하지 않음
        player.add_score(score)
        assert player.total_score >= initial_score

        # 불변성: 점수 증가량은 정확함
        assert player.total_score == initial_score + score

    @given(
        levels=st.lists(st.integers(min_value=1, max_value=10), min_size=1, max_size=10, unique=True)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    def test_level_completion_no_duplicates(self, levels):
        """레벨 완료 목록에는 중복이 없다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="property_levels_001",
            player_name="레벨테스터",
            level_id=1
        )

        player = session.player

        # 불변성: 중복 완료 시도해도 리스트는 유일함
        for level in levels:
            player.complete_level(level)
            player.complete_level(level)  # 중복 완료

        # 불변성: 완료된 레벨 수 = 유일한 레벨 수
        assert len(player.completed_levels) == len(set(levels))
        assert len(player.completed_levels) == len(player.completed_levels)  # 중복 없음


class TestPropertyBasedBoundaries:
    """경계값 프로퍼티 테스트"""

    @given(
        claim_text=st.just("a" * 30)  # 정확히 30자 (최소)
    )
    @settings(max_examples=10)
    def test_boundary_minimum_length_claim(self, claim_text):
        """최소 길이(30자) 청구항은 수락된다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="boundary_min_001",
            player_name="경계테스터",
            level_id=1
        )

        result = session.submit_claim(claim_text)
        assert result is True
        assert len(session.submitted_claims) == 1

    @given(
        claim_text=st.just("a" * 1000)  # 정확히 1000자 (최대)
    )
    @settings(max_examples=10)
    def test_boundary_maximum_length_claim(self, claim_text):
        """최대 길이(1000자) 청구항은 수락된다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="boundary_max_001",
            player_name="경계테스터",
            level_id=1
        )

        result = session.submit_claim(claim_text)
        assert result is True
        assert len(session.submitted_claims) == 1

    @given(
        claim_text=st.just("a" * 29)  # 29자 (최소 - 1)
    )
    @settings(max_examples=10)
    def test_boundary_below_minimum_length(self, claim_text):
        """최소 길이 미만(29자) 청구항은 거부된다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="boundary_below_min_001",
            player_name="경계테스터",
            level_id=1
        )

        result = session.submit_claim(claim_text)
        assert result is False
        assert len(session.submitted_claims) == 0

    @given(
        claim_text=st.just("a" * 1001)  # 1001자 (최대 + 1)
    )
    @settings(max_examples=10)
    def test_boundary_above_maximum_length(self, claim_text):
        """최대 길이 초과(1001자) 청구항은 거부된다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="boundary_above_max_001",
            player_name="경계테스터",
            level_id=1
        )

        result = session.submit_claim(claim_text)
        assert result is False
        assert len(session.submitted_claims) == 0


class TestPropertyBasedSequences:
    """시퀀스 프로퍼티 테스트"""

    @given(
        claims=st.lists(
            st.text(
                alphabet="가나다라마바사아아아아아아아아",
                min_size=30,
                max_size=100
            ),
            min_size=0,
            max_size=10
        )
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    def test_claim_sequence_preserves_order(self, claims):
        """청구항 시퀀스의 순서는 보존된다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="property_sequence_001",
            player_name="시퀀스테스터",
            level_id=1
        )

        # 모든 청구항 추가
        for claim in claims:
            session.submit_claim(claim)

        # 불변성: 순서 보존
        for i, claim in enumerate(claims):
            assert session.submitted_claims[i] == claim

    @given(
        scores=st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=10)
    )
    @settings(max_examples=50)
    def test_score_sequence_accumulation(self, scores):
        """점수 시퀀스 누적은 예측 가능하다"""
        engine = GameEngine()
        session = engine.create_session(
            session_id="property_score_sequence_001",
            player_name="점수시퀀스테스터",
            level_id=1
        )

        player = session.player
        expected_total = 0

        # 불변성: 누적 점수 = 모든 점수 합
        for score in scores:
            player.add_score(score)
            expected_total += score
            assert player.total_score == expected_total


class TestPropertyBasedCommutativity:
    """교환성 프로퍼티 테스트"""

    @given(
        score1=st.integers(min_value=0, max_value=500),
        score2=st.integers(min_value=0, max_value=500)
    )
    @settings(max_examples=100)
    def test_score_addition_is_commutative(self, score1, score2):
        """점수 추가는 교환성이 있다"""
        engine = GameEngine()

        # 경로 1: score1 → score2
        session1 = engine.create_session(
            session_id="commutative_test_1",
            player_name="교환성테스터",
            level_id=1
        )
        session1.player.add_score(score1)
        session1.player.add_score(score2)
        result1 = session1.player.total_score

        # 경로 2: score2 → score1
        session2 = engine.create_session(
            session_id="commutative_test_2",
            player_name="교환성테스터",
            level_id=1
        )
        session2.player.add_score(score2)
        session2.player.add_score(score1)
        result2 = session2.player.total_score

        # 불변성: 두 경로의 결과는 동일
        assert result1 == result2
        assert result1 == score1 + score2
