"""
Claim Grammar Validator 테스트

청구항 문법 검증 시스템을 테스트합니다.
"""

import pytest
from src.dsl.grammar.claim_validator import (
    ClaimValidator,
    ValidationLevel,
    ClaimType,
    ValidationError,
    ValidationRule,
    ClaimValidationResult,
)


class TestValidationError:
    """ValidationError 클래스 테스트"""

    def test_create_error(self):
        """검증 오류 생성"""
        error = ValidationError(
            level=ValidationLevel.ERROR,
            code="TEST_001",
            message="테스트 오류",
        )

        assert error.level == ValidationLevel.ERROR
        assert error.code == "TEST_001"
        assert error.message == "테스트 오류"

    def test_error_string_representation(self):
        """오류의 문자열 표현"""
        error = ValidationError(
            level=ValidationLevel.ERROR,
            code="TEST_001",
            message="테스트 오류",
        )

        assert str(error) == "[ERROR] TEST_001: 테스트 오류"


class TestValidationRule:
    """ValidationRule 클래스 테스트"""

    def test_create_rule(self):
        """검증 규칙 생성"""
        rule = ValidationRule(
            rule_id="TEST_001",
            description="테스트 규칙",
            level=ValidationLevel.WARNING,
        )

        assert rule.rule_id == "TEST_001"
        assert rule.description == "테스트 규칙"
        assert rule.level == ValidationLevel.WARNING

    def test_empty_rule_id_fails(self):
        """빈 규칙 ID는 실패"""
        with pytest.raises(ValueError):
            ValidationRule(
                rule_id="",
                description="테스트 규칙",
            )

    def test_empty_description_fails(self):
        """빈 설명은 실패"""
        with pytest.raises(ValueError):
            ValidationRule(
                rule_id="TEST_001",
                description="",
            )


class TestClaimValidationResult:
    """ClaimValidationResult 클래스 테스트"""

    def test_create_result(self):
        """검증 결과 생성"""
        result = ClaimValidationResult(
            claim_number=1,
            claim_type="independent",
        )

        assert result.claim_number == 1
        assert result.claim_type == "independent"
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_add_error(self):
        """오류 추가"""
        result = ClaimValidationResult(
            claim_number=1,
            claim_type="independent",
        )

        result.add_error("TEST_001", "테스트 오류")

        assert len(result.errors) == 1
        assert result.is_valid is False

    def test_add_warning(self):
        """경고 추가"""
        result = ClaimValidationResult(
            claim_number=1,
            claim_type="independent",
        )

        result.add_warning("TEST_001", "테스트 경고")

        assert len(result.warnings) == 1
        assert result.is_valid is True

    def test_result_string_representation(self):
        """결과의 문자열 표현"""
        result = ClaimValidationResult(
            claim_number=1,
            claim_type="independent",
        )

        assert "청구항 1" in str(result)
        assert "✅ 유효" in str(result)


class TestClaimValidator:
    """ClaimValidator 클래스 테스트"""

    def test_validator_creation(self):
        """검증 엔진 생성"""
        validator = ClaimValidator()

        assert validator is not None
        assert len(validator.rules) > 0

    def test_validate_valid_claim(self):
        """유효한 청구항 검증"""
        validator = ClaimValidator()
        result = validator.validate_claim_content(
            claim_number=1,
            claim_type="independent",
            content="배터리 장치는 양극, 음극, 전해질을 포함한다",
        )

        assert result.claim_number == 1
        assert len(result.errors) == 0

    def test_validate_empty_content(self):
        """빈 내용 검증"""
        validator = ClaimValidator()
        result = validator.validate_claim_content(
            claim_number=1,
            claim_type="independent",
            content="",
        )

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_short_content(self):
        """너무 짧은 내용 검증"""
        validator = ClaimValidator()
        result = validator.validate_claim_content(
            claim_number=1,
            claim_type="independent",
            content="짧은 내용",
        )

        assert result.is_valid is False

    def test_validate_ambiguous_claim(self):
        """모호한 표현이 있는 청구항"""
        validator = ClaimValidator()
        result = validator.validate_claim_content(
            claim_number=1,
            claim_type="independent",
            content="배터리 장치는 여러 요소 등을 포함할 수 있다",
        )

        assert len(result.warnings) > 0

    def test_validate_dependent_claim(self):
        """종속항 검증"""
        validator = ClaimValidator()
        result = validator.validate_claim_content(
            claim_number=2,
            claim_type="dependent",
            content="제1항의 배터리에서 양극은 리튬 함유 물질로 이루어진다",
        )

        assert result.claim_number == 2

    def test_add_custom_rule(self):
        """사용자 정의 규칙 추가"""
        validator = ClaimValidator()

        custom_rule = ValidationRule(
            rule_id="CUSTOM_001",
            description="사용자 정의 규칙",
        )

        validator.add_rule(custom_rule)

        assert "CUSTOM_001" in validator.rules

    def test_invalid_rule_type(self):
        """유효하지 않은 규칙 타입"""
        validator = ClaimValidator()

        with pytest.raises(TypeError):
            validator.add_rule("not a rule")

    def test_validate_claim_set(self):
        """청구항 세트 검증"""
        validator = ClaimValidator()

        claims = {
            1: ("independent", "배터리 장치는 양극, 음극, 전해질을 포함한다"),
            2: (
                "dependent",
                "제1항의 배터리에서 양극은 리튬 함유 물질로 이루어진다",
            ),
            3: (
                "dependent",
                "제1항의 배터리에서 음극은 흑연으로 이루어진다",
            ),
        }

        results = validator.validate_claim_set(claims)

        assert len(results) == 3
        assert all(isinstance(r, ClaimValidationResult) for r in results)

    def test_generate_report(self):
        """검증 보고서 생성"""
        validator = ClaimValidator()

        claims = {
            1: ("independent", "배터리 장치는 양극, 음극, 전해질을 포함한다"),
            2: (
                "dependent",
                "제1항의 배터리에서 양극은 리튬 함유 물질로 이루어진다",
            ),
        }

        results = validator.validate_claim_set(claims)
        report = validator.generate_report(results)

        assert "검증 보고서" in report
        assert "청구항" in report

    def test_validate_claim_invalid_number(self):
        """유효하지 않은 청구항 번호"""
        validator = ClaimValidator()

        with pytest.raises(ValueError):
            validator.validate_claim_content(
                claim_number=0,
                claim_type="independent",
                content="내용",
            )

    def test_validate_claim_invalid_type(self):
        """유효하지 않은 claim_type 타입"""
        validator = ClaimValidator()

        with pytest.raises(TypeError):
            validator.validate_claim_content(
                claim_number=1,
                claim_type=123,  # 정수 대신 문자열 필요
                content="내용",
            )

    def test_validate_claim_invalid_content_type(self):
        """유효하지 않은 content 타입"""
        validator = ClaimValidator()

        with pytest.raises(TypeError):
            validator.validate_claim_content(
                claim_number=1,
                claim_type="independent",
                content=123,  # 정수 대신 문자열 필요
            )


class TestClaimValidationScenarios:
    """실제 청구항 검증 시나리오"""

    def test_invention_patent_claim_validation(self):
        """발명 특허 청구항 검증"""
        validator = ClaimValidator()

        claims = {
            1: (
                "independent",
                "고성능 배터리 장치는 양극, 음극, 전해질, 분리막으로 구성된다",
            ),
            2: (
                "dependent",
                "제1항의 배터리에서 양극은 리튬코발트산화물로 이루어진다",
            ),
            3: (
                "dependent",
                "제1항의 배터리에서 음극은 흑연으로 이루어진다",
            ),
            4: (
                "dependent",
                "제1항의 배터리에서 전해질은 유기용매에 용해된 리튬염이다",
            ),
        }

        results = validator.validate_claim_set(claims)

        assert len(results) == 4
        print(validator.generate_report(results))

    def test_method_claim_validation(self):
        """방법 청구항 검증"""
        validator = ClaimValidator()

        claims = {
            1: (
                "independent",
                "배터리 제조 방법은 다음 단계를 포함한다: "
                "1) 양극 준비, 2) 음극 준비, 3) 조립",
            ),
            2: (
                "dependent",
                "제1항의 방법에서 양극 준비는 리튬코발트산화물을 가열하는 단계를 포함한다",
            ),
        }

        results = validator.validate_claim_set(claims)

        assert len(results) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
