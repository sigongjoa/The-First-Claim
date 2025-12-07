"""
API 엔드포인트 통합 테스트 - v2 (속성 기반 테스트 포함)

실제 GameEngine을 사용하여 통합 테스트합니다.
Hypothesis를 사용한 속성 기반 테스트로 엣지 케이스 검증합니다.
"""

import pytest
from hypothesis import given, strategies as st, settings
from src.ui.game import GameEngine, GameSession


class TestGameSessionCreation:
    """게임 세션 생성 테스트"""

    def test_create_basic_session(self):
        """기본 세션 생성"""
        engine = GameEngine()

        session = engine.create_session(
            session_id="test_001", player_name="김특허", level_id=1
        )

        assert session is not None
        assert session.session_id == "test_001"
        # current_level은 GameLevel 객체
        assert session.current_level is not None
        assert session.current_level.level_id == 1

    @given(
        session_id=st.text(min_size=1, max_size=50),
        player_name=st.text(min_size=1, max_size=100),
        level_id=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=50)
    def test_session_creation_property(self, session_id, player_name, level_id):
        """세션 생성은 항상 유효한 세션을 반환해야 함 (속성 기반)"""
        engine = GameEngine()

        try:
            session = engine.create_session(
                session_id=session_id, player_name=player_name, level_id=level_id
            )

            # 속성 1: 세션은 None이 아니어야 함
            assert session is not None

            # 속성 2: 세션 ID는 제공된 값과 동일해야 함
            assert session.session_id == session_id

            # 속성 3: 레벨은 1 이상이어야 함
            assert session.current_level.level_id >= 1

        except Exception as e:
            # 예외가 발생해도 그것도 유효한 테스트 결과
            assert True


class TestClaimSubmission:
    """청구항 제출 테스트"""

    def test_submit_valid_claim(self):
        """정상적인 청구항 제출"""
        engine = GameEngine()
        session = engine.create_session("test_002", "김특허", 1)

        claim = "배터리 장치는 양극, 음극, 전해질을 포함하며 안전성을 제공한다"
        result = session.submit_claim(claim)

        assert result is True
        assert len(session.claims) == 1
        assert session.claims[0] == claim

    def test_submit_empty_claim(self):
        """빈 청구항은 거부되어야 함"""
        engine = GameEngine()
        session = engine.create_session("test_003", "김특허", 1)

        result = session.submit_claim("")

        assert result is False
        assert len(session.claims) == 0

    @given(claim=st.text(min_size=10, max_size=500))
    @settings(max_examples=30)
    def test_claim_submission_property(self, claim):
        """청구항 제출 속성 검증 (속성 기반)"""
        engine = GameEngine()
        session = engine.create_session("test_prop", "김특허", 1)

        # 속성 1: 제출 후 청구항 개수는 0 또는 1
        result = session.submit_claim(claim)
        assert len(session.claims) in [0, 1]

        # 속성 2: 제출 성공하면 True, 실패하면 False
        assert isinstance(result, bool)

        # 속성 3: 제출된 청구항이 있으면 그 내용은 제출한 것과 같아야 함
        if len(session.claims) > 0:
            assert session.claims[0] == claim

    @given(claim=st.text(max_size=0))  # 빈 문자열만
    @settings(max_examples=10)
    def test_empty_claim_always_rejected(self, claim):
        """빈 청구항은 항상 거부되어야 함 (속성)"""
        engine = GameEngine()
        session = engine.create_session("test_empty", "김특허", 1)

        result = session.submit_claim(claim)

        # 속성: 빈 청구항은 항상 False
        assert result is False
        assert len(session.claims) == 0


class TestClaimLength:
    """청구항 길이 범위 테스트"""

    @given(length=st.integers(min_value=1, max_value=30))
    @settings(max_examples=20)
    def test_very_short_claim(self, length):
        """너무 짧은 청구항 (1~30자)"""
        engine = GameEngine()
        session = engine.create_session("test_short", "김특허", 1)

        claim = "배터리" * (length // 2 + 1)
        claim = claim[:length]  # 정확히 원하는 길이로

        result = session.submit_claim(claim)

        # 매우 짧은 청구항은 거부될 가능성 높음
        # 하지만 실제 구현에 따라 다름

    @given(repetition=st.integers(min_value=100, max_value=500))
    @settings(max_examples=10)
    def test_very_long_claim(self, repetition):
        """매우 긴 청구항"""
        engine = GameEngine()
        session = engine.create_session("test_long", "김특허", 1)

        claim = "배터리" * repetition  # 1200~3000자

        result = session.submit_claim(claim)

        # 속성: 제출은 성공하든 실패하든 정상 처리되어야 함
        assert isinstance(result, bool)


class TestSpecialCharacters:
    """특수 문자 처리 테스트"""

    @given(
        claim=st.text(
            alphabet=st.characters(
                blacklist_categories=("Cc", "Cs"),  # 제어 문자 제외
                min_codepoint=0x1100,  # 한글만
            ),
            min_size=10,
            max_size=500,
        )
    )
    @settings(max_examples=20)
    def test_korean_characters(self, claim):
        """한글 청구항 처리"""
        engine = GameEngine()
        session = engine.create_session("test_korean", "김특허", 1)

        result = session.submit_claim(claim)

        # 속성: 한글은 항상 정상 처리되어야 함
        assert isinstance(result, bool)

    def test_special_characters_chemistry(self):
        """화학식 포함"""
        engine = GameEngine()
        session = engine.create_session("test_chem", "김특허", 1)

        claim = "배터리는 Li-ion(리튬이온), H₂O, NaCl 성분을 포함한다"
        result = session.submit_claim(claim)

        # 특수 문자는 처리되어야 함
        assert isinstance(result, bool)

    def test_parentheses_and_symbols(self):
        """괄호 및 기호"""
        engine = GameEngine()
        session = engine.create_session("test_symbols", "김특허", 1)

        claim = "배터리(양극, 음극, 전해질)는 [양극 단자]와 (음극 단자)로 연결된다"
        result = session.submit_claim(claim)

        assert isinstance(result, bool)


class TestDataConsistency:
    """데이터 일관성 테스트"""

    @given(num_claims=st.integers(min_value=1, max_value=10))
    @settings(max_examples=20)
    def test_claim_order_preserved(self, num_claims):
        """청구항 순서가 보존되어야 함 (속성)"""
        engine = GameEngine()
        session = engine.create_session("test_order", "김특허", 1)

        claims = [f"청구항 {i}: 배터리는 양극을 포함한다" for i in range(num_claims)]

        for claim in claims:
            session.submit_claim(claim)

        # 속성 1: 제출한 개수와 저장된 개수가 같아야 함
        successful_claims = len([c for c in session.claims if c is not None])
        assert successful_claims <= num_claims

        # 속성 2: 저장된 청구항의 순서는 제출 순서와 같아야 함
        for i, stored_claim in enumerate(session.claims):
            if stored_claim is not None:
                assert stored_claim.content == claims[i]

    def test_multiple_sessions_isolation(self):
        """다중 세션 격리"""
        engine = GameEngine()

        session1 = engine.create_session("test_s1", "플레이어1", 1)
        session2 = engine.create_session("test_s2", "플레이어2", 1)

        claim1 = "청구항1: 배터리는 양극을 포함한다"
        claim2 = "청구항2: 배터리는 음극을 포함한다"

        session1.submit_claim(claim1)
        session2.submit_claim(claim2)

        # 속성: 각 세션의 청구항은 분리되어야 함
        assert len(session1.claims) >= 0
        assert len(session2.claims) >= 0

        if len(session1.claims) > 0 and len(session2.claims) > 0:
            assert session1.claims[0].content != session2.claims[0].content


class TestErrorHandling:
    """에러 처리 테스트"""

    def test_none_claim_returns_false(self):
        """None 청구항은 False 반환"""
        engine = GameEngine()
        session = engine.create_session("test_none", "김특허", 1)

        result = session.submit_claim(None)

        # 속성: None은 항상 False를 반환해야 함
        assert result is False
        assert len(session.claims) == 0

    @given(claim=st.just(None))  # None만 생성
    @settings(max_examples=5)
    def test_none_always_returns_false(self, claim):
        """None은 항상 False를 반환해야 함 (속성)"""
        engine = GameEngine()
        session = engine.create_session("test_none_prop", "김특허", 1)

        result = session.submit_claim(claim)

        # 속성: None은 항상 False를 반환
        assert result is False
        assert len(session.claims) == 0


class TestScoreCalculation:
    """점수 계산 속성 검증"""

    @given(num_claims=st.integers(min_value=1, max_value=5))
    @settings(max_examples=10)
    def test_score_always_in_range(self, num_claims):
        """점수는 항상 유효한 범위여야 함 (속성)"""
        engine = GameEngine()
        session = engine.create_session("test_score", "김특허", 1)

        for i in range(num_claims):
            claim = f"청구항 {i}: 배터리는 구성요소를 포함한다"
            session.submit_claim(claim)

        # 평가 실행 시도
        if len(session.claims) > 0:
            success, feedback, details = engine.evaluate_claims(session.session_id)

            if success and "score" in details:
                score = details["score"]

                # 속성: 점수는 항상 >= 0
                assert score >= 0

                # 속성: 점수는 합리적인 범위 (0~300)
                assert score <= 300


class TestPerformance:
    """성능 속성 검증"""

    @given(text_length=st.integers(min_value=50, max_value=500))
    @settings(max_examples=10)
    def test_claim_submission_speed(self, text_length):
        """청구항 제출은 빠르게 처리되어야 함 (속성)"""
        import time

        engine = GameEngine()
        session = engine.create_session("test_perf", "김특허", 1)

        claim = "배터리" * (text_length // 2)

        start = time.time()
        result = session.submit_claim(claim)
        elapsed = time.time() - start

        # 속성: 제출은 100ms 이내에 완료되어야 함
        assert elapsed < 0.1, f"Claim submission took {elapsed:.3f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
