"""
Phase 1-1: Civil Law Vocabulary Tests

테스트 명세: TEST_SPECIFICATIONS_PHASE_1_1.md 참조
"""

import pytest
from src.dsl.vocabulary.civil_law import (
    CivilLawStatute,
    Person,
    Transaction,
    LegalRight,
)


# ============================================================================
# CivilLawStatute Tests
# ============================================================================


class TestCivilLawStatuteCreation:
    """CivilLawStatute 생성 테스트"""

    @pytest.mark.unit
    def test_valid_statute_creation_full(self):
        """U1-1: 정상 생성 (모든 필드)"""
        # Given
        statute_number = "제145조"
        title = "저작권자의 권리"
        requirements = ["독창성"]
        effects = ["복제권"]
        exceptions = ["공정이용"]
        related_precedents = []

        # When
        statute = CivilLawStatute(
            statute_number=statute_number,
            title=title,
            requirements=requirements,
            effects=effects,
            exceptions=exceptions,
            related_precedents=related_precedents,
        )

        # Then
        assert statute.statute_number == statute_number
        assert statute.title == title
        assert statute.requirements == requirements
        assert statute.effects == effects
        assert statute.exceptions == exceptions
        assert statute.related_precedents == related_precedents

    @pytest.mark.unit
    def test_valid_statute_creation_minimal(self):
        """U1-2: 정상 생성 (최소 필드)"""
        # When
        statute = CivilLawStatute(statute_number="제145조", title="저작권자의 권리")

        # Then
        assert statute.statute_number == "제145조"
        assert statute.title == "저작권자의 권리"
        assert statute.requirements == []
        assert statute.effects == []

    @pytest.mark.unit
    def test_attribute_retrieval(self):
        """U1-3: 속성 조회"""
        # Given
        statute = CivilLawStatute(statute_number="제145조", title="저작권자의 권리")

        # When & Then
        assert statute.statute_number == "제145조"
        assert statute.title == "저작권자의 권리"

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_empty_statute_number(self):
        """U1-4: 빈 문자열 statute_number"""
        # When & Then
        with pytest.raises(ValueError, match="statute_number"):
            CivilLawStatute(statute_number="", title="저작권자의 권리")

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_empty_title(self):
        """U1-5: 빈 title"""
        # When & Then
        with pytest.raises(ValueError, match="title"):
            CivilLawStatute(statute_number="제145조", title="")

    @pytest.mark.unit
    def test_none_statute_number(self):
        """U1-6: None 값 statute_number"""
        # When & Then
        with pytest.raises((ValueError, TypeError)):
            CivilLawStatute(statute_number=None, title="저작권자의 권리")  # type: ignore

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_duplicate_requirements(self):
        """U1-7: 중복된 requirements"""
        # When
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            requirements=["A", "A", "B"],
        )

        # Then: 중복이 제거됨
        assert len(statute.requirements) == 2
        assert "A" in statute.requirements
        assert "B" in statute.requirements

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_duplicate_effects(self):
        """U1-8: 중복된 effects"""
        # When
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            effects=["복제권", "복제권", "배포권"],
        )

        # Then: 중복이 제거됨
        assert len(statute.effects) == 2
        assert "복제권" in statute.effects
        assert "배포권" in statute.effects

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_very_long_title(self):
        """U1-9: 매우 긴 문자열"""
        # When
        long_title = "가" * 10000
        statute = CivilLawStatute(statute_number="제145조", title=long_title)

        # Then
        assert len(statute.title) == 10000
        assert statute.title == long_title

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_special_characters_in_title(self):
        """U1-10: 특수 문자 포함"""
        # When
        special_title = "제①조-②항(③)"
        statute = CivilLawStatute(statute_number="제145조", title=special_title)

        # Then
        assert statute.title == special_title

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_angle_brackets_in_title(self):
        """U1-11: 각도 괄호 포함"""
        # When
        title_with_brackets = "<제145조>"
        statute = CivilLawStatute(statute_number="제145조", title=title_with_brackets)

        # Then
        assert statute.title == title_with_brackets

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_newline_in_title(self):
        """U1-12: 개행문자 포함"""
        # When
        title_with_newline = "제145조\n추가 설명"
        statute = CivilLawStatute(statute_number="제145조", title=title_with_newline)

        # Then
        assert statute.title == title_with_newline

    @pytest.mark.unit
    def test_statute_equality(self):
        """U1-13: 동등성 테스트 1"""
        # Given
        statute1 = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            requirements=["독창성"],
        )
        statute2 = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            requirements=["독창성"],
        )

        # When & Then
        assert statute1 == statute2

    @pytest.mark.unit
    def test_statute_inequality(self):
        """U1-14: 동등성 테스트 2"""
        # Given
        statute1 = CivilLawStatute(statute_number="제145조", title="저작권자의 권리")
        statute2 = CivilLawStatute(statute_number="제146조", title="저작권자의 권리")

        # When & Then
        assert statute1 != statute2

    @pytest.mark.unit
    def test_statute_string_representation(self):
        """U1-15: 문자열 표현"""
        # Given
        statute = CivilLawStatute(statute_number="제145조", title="저작권자의 권리")

        # When
        repr_str = repr(statute)
        str_str = str(statute)

        # Then
        assert "제145조" in repr_str
        assert "CivilLawStatute" in repr_str or "제145조" in str_str

    @pytest.mark.unit
    def test_requirements_type_error(self):
        """U1-16: requirements가 리스트가 아님"""
        # When & Then
        with pytest.raises(TypeError):
            CivilLawStatute(
                statute_number="제145조",
                title="저작권자의 권리",
                requirements="A,B",  # type: ignore
            )

    @pytest.mark.unit
    def test_effects_type_error(self):
        """U1-17: effects가 딕셔너리임"""
        # When & Then
        with pytest.raises(TypeError):
            CivilLawStatute(
                statute_number="제145조",
                title="저작권자의 권리",
                effects={"복제권": True},  # type: ignore
            )

    @pytest.mark.unit
    def test_list_elements_not_string(self):
        """U1-18: 리스트의 원소가 문자열이 아님"""
        # When & Then
        with pytest.raises((TypeError, ValueError)):
            CivilLawStatute(
                statute_number="제145조",
                title="저작권자의 권리",
                requirements=[1, 2, 3],  # type: ignore
            )

    @pytest.mark.unit
    def test_empty_requirements_list(self):
        """U1-19: 빈 requirements 리스트"""
        # When
        statute = CivilLawStatute(
            statute_number="제145조", title="저작권자의 권리", requirements=[]
        )

        # Then
        assert statute.requirements == []

    @pytest.mark.unit
    def test_empty_exceptions_list(self):
        """U1-20: 빈 exceptions 리스트"""
        # When
        statute = CivilLawStatute(
            statute_number="제145조", title="저작권자의 권리", exceptions=[]
        )

        # Then
        assert statute.exceptions == []


# ============================================================================
# Person Tests
# ============================================================================


class TestPersonCreation:
    """Person 생성 테스트"""

    @pytest.mark.unit
    def test_valid_person_creation(self):
        """U2-1: 정상 생성"""
        # When
        person = Person(name="홍길동", role="저작권자")

        # Then
        assert person.name == "홍길동"
        assert person.role == "저작권자"

    @pytest.mark.unit
    def test_person_with_attributes(self):
        """U2-2: 속성 포함 생성"""
        # When
        person = Person(
            name="홍길동",
            role="제3자",
            attributes={"good_faith": True, "acquired_for_value": True},
        )

        # Then
        assert person.attributes["good_faith"] is True
        assert person.attributes["acquired_for_value"] is True

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_empty_name(self):
        """U2-3: 빈 이름"""
        # When & Then
        with pytest.raises(ValueError, match="name"):
            Person(name="", role="저작권자")

    @pytest.mark.unit
    def test_none_name(self):
        """U2-4: None 이름"""
        # When & Then
        with pytest.raises((ValueError, TypeError)):
            Person(name=None, role="저작권자")  # type: ignore

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_empty_role(self):
        """U2-5: 빈 role"""
        # When & Then
        with pytest.raises(ValueError, match="role"):
            Person(name="홍길동", role="")

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_invalid_role(self):
        """U2-6: 잘못된 role"""
        # When & Then: 경고 또는 에러
        # 유효한 role 목록: "저작권자", "침해자", "제3자" 등
        with pytest.raises((ValueError, TypeError)):
            Person(name="홍길동", role="우주인")

    @pytest.mark.unit
    def test_person_equality(self):
        """U2-7: 동등성 테스트"""
        # Given
        person1 = Person(name="홍길동", role="저작권자")
        person2 = Person(name="홍길동", role="저작권자")

        # When & Then
        assert person1 == person2

    @pytest.mark.unit
    def test_empty_attributes(self):
        """U2-8: attributes가 비어있음"""
        # When
        person = Person(name="홍길동", role="저작권자", attributes={})

        # Then
        assert person.attributes == {}


# ============================================================================
# Transaction Tests
# ============================================================================


class TestTransactionCreation:
    """Transaction 생성 테스트"""

    @pytest.mark.unit
    def test_valid_transaction_creation(self):
        """T1-1: 정상 생성"""
        # Given
        person1 = Person(name="홍길동", role="판매자")
        person2 = Person(name="김영희", role="구매자")

        # When
        transaction = Transaction(
            parties=[person1, person2],
            subject="저작물",
            consideration="100,000원",
            date="2025-01-01",
        )

        # Then
        assert len(transaction.parties) == 2
        assert transaction.subject == "저작물"
        assert transaction.consideration == "100,000원"
        assert transaction.date == "2025-01-01"

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_empty_parties(self):
        """T1-2: 빈 parties 리스트"""
        # When & Then
        with pytest.raises((ValueError, IndexError)):
            Transaction(
                parties=[],
                subject="저작물",
                consideration="100,000원",
                date="2025-01-01",
            )

    @pytest.mark.unit
    def test_none_subject(self):
        """T1-3: None subject"""
        # When & Then
        person = Person(name="홍길동", role="판매자")
        with pytest.raises((ValueError, TypeError)):
            Transaction(
                parties=[person],
                subject=None,  # type: ignore
                consideration="100,000원",
                date="2025-01-01",
            )

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_invalid_date_format(self):
        """T1-4: 형식이 잘못된 date"""
        # When & Then: 날짜 형식 검증
        person = Person(name="홍길동", role="판매자")
        with pytest.raises((ValueError, TypeError)):
            Transaction(
                parties=[person],
                subject="저작물",
                consideration="100,000원",
                date="invalid-date",  # type: ignore
            )

    @pytest.mark.unit
    def test_transaction_equality(self):
        """T1-5: 동등성 테스트"""
        # Given
        person1 = Person(name="홍길동", role="판매자")
        person2 = Person(name="김영희", role="구매자")

        transaction1 = Transaction(
            parties=[person1, person2],
            subject="저작물",
            consideration="100,000원",
            date="2025-01-01",
        )
        transaction2 = Transaction(
            parties=[person1, person2],
            subject="저작물",
            consideration="100,000원",
            date="2025-01-01",
        )

        # When & Then
        assert transaction1 == transaction2


# ============================================================================
# LegalRight Tests
# ============================================================================


class TestLegalRightCreation:
    """LegalRight 생성 테스트"""

    @pytest.mark.unit
    def test_valid_legal_right_creation(self):
        """LR1-1: 정상 생성"""
        # When
        right = LegalRight(
            name="저작권",
            scope="저작물",
            duration="저작자의 생존 중 + 70년",
            remedies=["침해금지청구", "손해배상청구"],
        )

        # Then
        assert right.name == "저작권"
        assert right.scope == "저작물"
        assert right.duration == "저작자의 생존 중 + 70년"
        assert "침해금지청구" in right.remedies

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_empty_remedies(self):
        """LR1-2: 빈 remedies 리스트"""
        # When
        right = LegalRight(
            name="저작권",
            scope="저작물",
            duration="저작자의 생존 중 + 70년",
            remedies=[],
        )

        # Then
        assert right.remedies == []

    @pytest.mark.unit
    def test_none_duration(self):
        """LR1-3: None duration"""
        # When & Then
        with pytest.raises((ValueError, TypeError)):
            LegalRight(
                name="저작권",
                scope="저작물",
                duration=None,  # type: ignore
                remedies=["침해금지청구"],
            )

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_very_long_scope(self):
        """LR1-4: 매우 긴 scope"""
        # When
        long_scope = "X" * 10000
        right = LegalRight(
            name="저작권",
            scope=long_scope,
            duration="저작자의 생존 중 + 70년",
            remedies=[],
        )

        # Then
        assert len(right.scope) == 10000

    @pytest.mark.unit
    def test_legal_right_equality(self):
        """LR1-5: 동등성 테스트"""
        # Given
        right1 = LegalRight(
            name="저작권",
            scope="저작물",
            duration="저작자의 생존 중 + 70년",
            remedies=["침해금지청구"],
        )
        right2 = LegalRight(
            name="저작권",
            scope="저작물",
            duration="저작자의 생존 중 + 70년",
            remedies=["침해금지청구"],
        )

        # When & Then
        assert right1 == right2


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """통합 테스트"""

    @pytest.mark.integration
    def test_statute_related_to_person(self):
        """I1-1: Statute와 Person의 관계"""
        # Given
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            effects=["복제권", "배포권"],
        )
        person = Person(name="홍길동", role="저작권자")

        # When & Then: 저작권자는 저작권법의 효과를 누릴 수 있어야 함
        assert person.role == "저작권자"
        assert "복제권" in statute.effects

    @pytest.mark.integration
    def test_person_transaction_relation(self):
        """I1-2: Person과 Transaction의 관계"""
        # Given
        person1 = Person(name="홍길동", role="저작권자")
        person2 = Person(name="김영희", role="침해자")

        # When
        transaction = Transaction(
            parties=[person1, person2],
            subject="저작물",
            consideration="0원",
            date="2025-01-01",
        )

        # Then
        assert person1 in transaction.parties
        assert person2 in transaction.parties

    @pytest.mark.integration
    def test_statute_and_legal_right(self):
        """I1-3: Statute와 LegalRight의 관계"""
        # Given
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            effects=["복제권", "배포권"],
        )
        right = LegalRight(
            name="저작권",
            scope="저작물",
            duration="저작자의 생존 중 + 70년",
            remedies=["침해금지청구"],
        )

        # Then: statute의 효과는 right의 내용과 일치해야 함
        assert "복제권" in statute.effects
        assert right.name == "저작권"
