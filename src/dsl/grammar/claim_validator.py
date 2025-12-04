"""
Claim Grammar Validator - 청구항 문법 검증 시스템

청구항의 문법적 정확성과 법적 요구사항을 검증합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re


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
        """기술적 특징 검증

        Rule: 청구항은 명백한 기술적 특징을 포함해야 함
        """
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
            "장치",
            "시스템",
            "수단",
            "구조",
        ]

        has_technical_keyword = any(
            keyword in content for keyword in technical_keywords
        )

        if not has_technical_keyword:
            result.add_error(
                "STRUCTURE_001",
                "청구항이 명확한 기술적 특징을 포함하지 않습니다. "
                "포함, 구성, 방법, 단계 등의 기술용어가 필요합니다."
            )
        else:
            result.add_info(
                "STRUCTURE_001",
                "✅ 기술적 특징이 명확하게 포함되어 있습니다"
            )

    def _validate_clarity(self, result: ClaimValidationResult, content: str) -> None:
        """명확성 검증

        Rule: 청구항은 명확해야 함 - 모호한 표현 제거
        """
        # 모호한 표현 확인
        ambiguous_terms = [
            "등",           # "예를 들어 등" 형식의 모호한 표현
            "같은",         # "~같은" 비한정적 표현
            "대략",         # 부정확한 표현
            "약",           # 근사치 표현
            "대체로",       # 비확정적 표현
            "가능한",       # 조건부 표현
            "기타",         # 범위 불명확
            "그 외",        # 범위 불명확
        ]

        found_ambiguous = []
        for term in ambiguous_terms:
            if term in content:
                found_ambiguous.append(term)

        if found_ambiguous:
            result.add_error(
                "CLARITY_001",
                f"모호한 표현이 포함되어 있습니다: {', '.join(found_ambiguous)}. "
                f"특허법 제42조에서는 청구항이 명확해야 한다고 규정합니다."
            )
        else:
            result.add_info(
                "CLARITY_001",
                "✅ 모호한 표현이 없습니다"
            )

    def _validate_structure(
        self, result: ClaimValidationResult, claim_type: str, content: str
    ) -> None:
        """구조적 검증

        Rule 1: 독립항은 최소 20자 이상
        Rule 2: 독립항은 전문과 본체 구조 필요
        Rule 3: 종속항은 제X항 형식 필수
        """
        if claim_type == "independent":
            # 최소 길이 검증 (특허법 시행규칙 요구사항)
            if len(content.strip()) < 20:
                result.add_error(
                    "STRUCTURE_002",
                    "청구항 내용이 너무 짧습니다 (최소 20자). "
                    "더 상세한 기술적 특징을 포함해야 합니다."
                )
            else:
                result.add_info(
                    "STRUCTURE_002",
                    "✅ 최소 길이 요건을 충족합니다"
                )

            # 독립항의 전문과 본체 구조 확인
            # 전문: "~를 포함하는", "~로 이루어진" 등
            # 본체: 기술적 특징들
            preamble_keywords = ["포함하는", "구성된", "이루어진", "갖는", "포함한"]
            has_preamble = any(kw in content for kw in preamble_keywords)

            if not has_preamble:
                result.add_warning(
                    "STRUCTURE_002",
                    "독립항의 전문 구조가 명확하지 않을 수 있습니다. "
                    "'포함하는', '구성된' 등의 표현이 권장됩니다."
                )
            else:
                result.add_info(
                    "STRUCTURE_002",
                    "✅ 독립항의 전문 구조가 명확합니다"
                )

        elif claim_type == "dependent":
            # 종속항의 필수 요소: 선행항 참조
            if "제" not in content or "항" not in content:
                result.add_error(
                    "STRUCTURE_003",
                    "종속항이 선행항을 명시적으로 참조하지 않습니다. "
                    "'제X항' 형식의 참조가 필요합니다."
                )
            else:
                # 종속항 참조 형식 검증 (제X항)
                dependent_pattern = r"제\d+항"
                if re.search(dependent_pattern, content):
                    result.add_info(
                        "STRUCTURE_003",
                        "✅ 종속항이 올바른 형식으로 선행항을 참조합니다"
                    )
                else:
                    result.add_warning(
                        "STRUCTURE_003",
                        "종속항의 참조 형식이 표준 형식('제X항')과 다릅니다"
                    )

    def _validate_dependent_reference(
        self,
        result: ClaimValidationResult,
        content: str,
        available_claims: set,
    ) -> None:
        """종속항의 참조 검증

        Rule: 종속항은 존재하는 선행항만 참조 가능
        특허법 제45조 - 종속항은 선행항의 전체 구성요소를 포함하고 제한을 가할 수 있음
        """
        # 종속항 참조 추출 (제X항 형식)
        dependent_pattern = r"제(\d+)항"
        matches = re.findall(dependent_pattern, content)

        if not matches:
            result.add_error(
                "STRUCTURE_003",
                "종속항이 선행항을 참조하지 않습니다. "
                "'제X항'의 항 참조가 필요합니다."
            )
            return

        # 참조된 청구항이 실제로 존재하는지 확인
        referenced_claims = [int(m) for m in matches]
        invalid_references = []

        for ref_num in referenced_claims:
            if ref_num not in available_claims:
                invalid_references.append(ref_num)
            elif ref_num >= result.claim_number:
                # 종속항은 선행항만 참조 가능
                invalid_references.append(ref_num)

        if invalid_references:
            result.add_error(
                "STRUCTURE_003",
                f"존재하지 않는 청구항을 참조합니다: 제{invalid_references}항. "
                f"종속항은 선행하는 청구항만 참조할 수 있습니다."
            )
        else:
            result.add_info(
                "STRUCTURE_003",
                f"✅ 종속항이 유효한 선행항을 올바르게 참조합니다 (제{referenced_claims}항)"
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
