"""
Claim Grammar Validator - 청구항 문법 검증 시스템

청구항의 문법적 정확성과 법적 요구사항을 검증합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ValidationLevel(Enum):
    """검증 레벨"""

    ERROR = "error"  # 심각한 오류
    WARNING = "warning"  # 경고
    INFO = "info"  # 정보


class ClaimType(Enum):
    """청구항 타입"""

    INDEPENDENT = "independent"  # 독립항
    DEPENDENT = "dependent"  # 종속항
    MULTIPLE_DEPENDENT = "multiple_dependent"  # 다중 종속항


@dataclass
class ValidationError:
    """검증 오류"""

    level: ValidationLevel
    code: str
    message: str
    line: Optional[int] = None
    position: Optional[int] = None

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"ValidationError(level={self.level.value}, code='{self.code}', "
            f"message='{self.message}')"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return f"[{self.level.value.upper()}] {self.code}: {self.message}"


@dataclass
class ValidationRule:
    """검증 규칙"""

    rule_id: str
    description: str
    pattern: Optional[str] = None
    check_function: Optional[callable] = None
    level: ValidationLevel = ValidationLevel.ERROR

    def __post_init__(self) -> None:
        """검증 규칙 검증"""
        if not self.rule_id or not self.rule_id.strip():
            raise ValueError("rule_id는 비어있지 않아야 합니다")
        if not self.description or not self.description.strip():
            raise ValueError("description은 비어있지 않아야 합니다")


@dataclass
class ClaimValidationResult:
    """청구항 검증 결과"""

    claim_number: int
    claim_type: str
    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)

    def __post_init__(self) -> None:
        """검증 결과 정규화"""
        if self.errors:
            self.is_valid = False

    def add_error(self, code: str, message: str, line: Optional[int] = None) -> None:
        """오류 추가"""
        error = ValidationError(
            level=ValidationLevel.ERROR, code=code, message=message, line=line
        )
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, code: str, message: str, line: Optional[int] = None) -> None:
        """경고 추가"""
        warning = ValidationError(
            level=ValidationLevel.WARNING, code=code, message=message, line=line
        )
        self.warnings.append(warning)

    def add_info(self, code: str, message: str) -> None:
        """정보 추가"""
        info = ValidationError(level=ValidationLevel.INFO, code=code, message=message)
        self.info.append(info)

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"ClaimValidationResult("
            f"claim_number={self.claim_number}, "
            f"is_valid={self.is_valid}, "
            f"errors={len(self.errors)})"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return (
            f"청구항 {self.claim_number}: "
            f"{'✅ 유효' if self.is_valid else '❌ 무효'} "
            f"(오류: {len(self.errors)}, 경고: {len(self.warnings)})"
        )


class ClaimValidator:
    """청구항 문법 검증 엔진"""

    # 기본 검증 규칙들
    DEFAULT_RULES = {
        "STRUCTURE_001": ValidationRule(
            rule_id="STRUCTURE_001",
            description="청구항은 기술적 특징을 명시해야 함",
            level=ValidationLevel.ERROR,
        ),
        "STRUCTURE_002": ValidationRule(
            rule_id="STRUCTURE_002",
            description="청구항은 명확해야 함",
            level=ValidationLevel.ERROR,
        ),
        "STRUCTURE_003": ValidationRule(
            rule_id="STRUCTURE_003",
            description="종속항은 유효한 선행항에 의존해야 함",
            level=ValidationLevel.ERROR,
        ),
        "CLARITY_001": ValidationRule(
            rule_id="CLARITY_001",
            description="모호한 표현이 없어야 함",
            level=ValidationLevel.WARNING,
        ),
        "UNITY_001": ValidationRule(
            rule_id="UNITY_001",
            description="청구항들 사이의 단일성 필요",
            level=ValidationLevel.WARNING,
        ),
    }

    def __init__(self) -> None:
        """ClaimValidator 초기화"""
        self.rules: Dict[str, ValidationRule] = self.DEFAULT_RULES.copy()

    def add_rule(self, rule: ValidationRule) -> None:
        """검증 규칙 추가"""
        if not isinstance(rule, ValidationRule):
            raise TypeError("rule은 ValidationRule이어야 합니다")
        self.rules[rule.rule_id] = rule

    def validate_claim_content(
        self, claim_number: int, claim_type: str, content: str
    ) -> ClaimValidationResult:
        """청구항 내용 검증"""
        if not isinstance(claim_number, int) or claim_number <= 0:
            raise ValueError("claim_number은 양수여야 합니다")
        if not isinstance(claim_type, str):
            raise TypeError("claim_type은 문자열이어야 합니다")
        if not isinstance(content, str):
            raise TypeError("content는 문자열이어야 합니다")

        result = ClaimValidationResult(claim_number=claim_number, claim_type=claim_type)

        # 기본 검증: 내용이 비어있지 않은지
        if not content or not content.strip():
            result.add_error("CONTENT_EMPTY", "청구항 내용이 비어있습니다")
            return result

        # 기술적 특징 확인
        self._validate_technical_features(result, content)

        # 명확성 검증
        self._validate_clarity(result, content)

        # 구조 검증
        self._validate_structure(result, claim_type, content)

        return result

    def validate_claim_set(
        self, claims: Dict[int, Tuple[str, str]]
    ) -> List[ClaimValidationResult]:
        """청구항 세트 검증

        Args:
            claims: {claim_number: (claim_type, content)} 형식의 딕셔너리

        Returns:
            ClaimValidationResult 리스트
        """
        results = []
        claim_numbers = set()

        for claim_number, (claim_type, content) in claims.items():
            result = self.validate_claim_content(claim_number, claim_type, content)
            results.append(result)
            claim_numbers.add(claim_number)

            # 종속항의 참조 검증
            if claim_type == "dependent":
                self._validate_dependent_reference(result, content, claim_numbers)

        return results

    def _validate_technical_features(
        self, result: ClaimValidationResult, content: str
    ) -> None:
        """기술적 특징 검증"""
        # 기술 용어의 존재 확인
        technical_keywords = [
            "포함",
            "구성",
            "방법",
            "단계",
            "특징",
            "요소",
            "부분",
            "기술",
        ]

        has_technical_keyword = any(
            keyword in content for keyword in technical_keywords
        )

        if not has_technical_keyword:
            result.add_warning(
                "STRUCTURE_001", "청구항이 기술적 특징을 명확하게 포함하지 않을 수 있음"
            )

    def _validate_clarity(self, result: ClaimValidationResult, content: str) -> None:
        """명확성 검증"""
        # 모호한 표현 확인
        ambiguous_terms = [
            "등",
            "같은",
            "대략",
            "약",
            "대체로",
            "가능한",
            "되는",
        ]

        for term in ambiguous_terms:
            if term in content:
                result.add_warning(
                    "CLARITY_001",
                    f"모호한 표현 '{term}'이 포함되어 있습니다",
                )

    def _validate_structure(
        self, result: ClaimValidationResult, claim_type: str, content: str
    ) -> None:
        """구조적 검증"""
        # 독립항의 경우 기본 요소 확인
        if claim_type == "independent":
            # 최소한 하나의 핵심 요소 필요
            if len(content.strip()) < 20:
                result.add_error(
                    "STRUCTURE_002",
                    "청구항 내용이 너무 짧습니다 (최소 20자)",
                )

    def _validate_dependent_reference(
        self,
        result: ClaimValidationResult,
        content: str,
        available_claims: set,
    ) -> None:
        """종속항의 참조 검증"""
        # 종속항이 이전 청구항을 참조하는지 확인
        if "제" in content and "항" in content:
            result.add_info(
                "STRUCTURE_003", "종속항이 선행항을 올바르게 참조하고 있습니다"
            )
        else:
            result.add_error(
                "STRUCTURE_003",
                "종속항이 유효한 선행항을 참조하지 않습니다",
            )

    def generate_report(self, results: List[ClaimValidationResult]) -> str:
        """검증 결과 보고서 생성"""
        report = "=" * 80 + "\n"
        report += "청구항 검증 보고서\n"
        report += "=" * 80 + "\n\n"

        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid

        report += f"📊 전체 결과: {valid}/{total} 유효\n"
        report += f"   - 유효: {valid}개\n"
        report += f"   - 무효: {invalid}개\n\n"

        for result in results:
            report += f"{'✅' if result.is_valid else '❌'} {result}\n"
            for error in result.errors:
                report += f"   {error}\n"
            for warning in result.warnings:
                report += f"   {warning}\n"

        report += "=" * 80

        return report
