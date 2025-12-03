"""
Patent Law Vocabulary - 특허법 관련 핵심 데이터 모델

이 모듈은 특허법 조문, 발명, 청구항, 심사 등을 객체로 모델링합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Set


@dataclass
class PatentArticle:
    """
    특허법 조문을 객체화하는 클래스.

    특허법의 각 조문을 구조화하여 요건(requirements)과 효과(effects),
    예외(exceptions)를 명시적으로 표현합니다.

    Attributes:
        article_number: 조문 번호 (예: "제1조")
        title: 조문의 제목 (예: "(목적)")
        content: 조문의 내용
        requirements: 성립 요건들 (List[str])
        effects: 법적 효과들 (List[str])
        exceptions: 예외 사유들 (List[str])

    Example:
        >>> article = PatentArticle(
        ...     article_number="제1조",
        ...     title="(목적)",
        ...     content="이 법은 발명에 대한 특허권의 취득...",
        ...     requirements=[],
        ...     effects=["특허권 설정"],
        ...     exceptions=[]
        ... )
        >>> article.article_number
        '제1조'
    """

    article_number: str
    title: str
    content: str = ""
    requirements: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        객체 생성 후 유효성 검증 및 정규화.

        Raises:
            ValueError: article_number 또는 title이 비어있거나 유효하지 않은 경우
            TypeError: 리스트 필드의 타입이 올바르지 않은 경우
        """
        # article_number 검증
        if not isinstance(self.article_number, str):
            raise TypeError("article_number은 문자열이어야 합니다")
        if not self.article_number or not self.article_number.strip():
            raise ValueError("article_number은 비어있지 않은 문자열이어야 합니다")

        # title 검증
        if not isinstance(self.title, str):
            raise TypeError("title은 문자열이어야 합니다")
        if not self.title or not self.title.strip():
            raise ValueError("title은 비어있지 않은 문자열이어야 합니다")

        # content 검증
        if not isinstance(self.content, str):
            raise TypeError("content는 문자열이어야 합니다")

        # 리스트 필드 검증
        self._validate_and_normalize_list("requirements", self.requirements)
        self._validate_and_normalize_list("effects", self.effects)
        self._validate_and_normalize_list("exceptions", self.exceptions)

        # 중복 제거 (순서 유지)
        self.requirements = list(dict.fromkeys(self.requirements))
        self.effects = list(dict.fromkeys(self.effects))
        self.exceptions = list(dict.fromkeys(self.exceptions))

    @staticmethod
    def _validate_and_normalize_list(field_name: str, items: List) -> None:
        """
        리스트 필드의 타입을 검증합니다.

        Args:
            field_name: 필드명 (에러 메시지용)
            items: 검증할 리스트

        Raises:
            TypeError: 리스트가 아니거나 원소가 문자열이 아닌 경우
        """
        if not isinstance(items, list):
            raise TypeError(f"{field_name}은 리스트여야 합니다")

        for item in items:
            if not isinstance(item, str):
                raise TypeError(f"{field_name}의 모든 원소는 문자열이어야 합니다")

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"PatentArticle("
            f"article_number='{self.article_number}', "
            f"title='{self.title}')"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return f"{self.article_number} - {self.title}"

    def __eq__(self, other: object) -> bool:
        """두 PatentArticle 객체의 동등성을 검사합니다."""
        if not isinstance(other, PatentArticle):
            return NotImplemented
        return (
            self.article_number == other.article_number
            and self.title == other.title
            and self.content == other.content
            and self.requirements == other.requirements
            and self.effects == other.effects
            and self.exceptions == other.exceptions
        )

    def __hash__(self) -> int:
        """해시값을 계산합니다."""
        return hash(
            (
                self.article_number,
                self.title,
                tuple(self.requirements),
                tuple(self.effects),
                tuple(self.exceptions),
            )
        )


@dataclass
class Invention:
    """
    발명을 표현하는 클래스.

    특허 출원의 대상이 되는 발명을 모델링합니다.

    Attributes:
        title: 발명의 제목
        technical_field: 기술분야
        novelty: 신규성 여부
        inventive_step: 진보성 여부
        industrial_applicability: 산업상 이용가능성 여부
        claims: 청구항들 (List[str])

    Example:
        >>> invention = Invention(
        ...     title="개선된 배터리",
        ...     technical_field="전자기술",
        ...     novelty=True,
        ...     inventive_step=True,
        ...     industrial_applicability=True,
        ...     claims=["1. 배터리의 구조", "2. 배터리의 재료"]
        ... )
    """

    title: str
    technical_field: str
    novelty: bool = False
    inventive_step: bool = False
    industrial_applicability: bool = False
    claims: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        객체 생성 후 유효성 검증.

        Raises:
            ValueError: 필수 필드가 비어있는 경우
            TypeError: 필드 타입이 올바르지 않은 경우
        """
        # title 검증
        if not isinstance(self.title, str):
            raise TypeError("title은 문자열이어야 합니다")
        if not self.title or not self.title.strip():
            raise ValueError("title은 비어있지 않은 문자열이어야 합니다")

        # technical_field 검증
        if not isinstance(self.technical_field, str):
            raise TypeError("technical_field는 문자열이어야 합니다")
        if not self.technical_field or not self.technical_field.strip():
            raise ValueError("technical_field는 비어있지 않은 문자열이어야 합니다")

        # 불린 필드 검증
        if not isinstance(self.novelty, bool):
            raise TypeError("novelty는 불린이어야 합니다")
        if not isinstance(self.inventive_step, bool):
            raise TypeError("inventive_step은 불린이어야 합니다")
        if not isinstance(self.industrial_applicability, bool):
            raise TypeError("industrial_applicability는 불린이어야 합니다")

        # claims 검증
        if not isinstance(self.claims, list):
            raise TypeError("claims는 리스트여야 합니다")
        for claim in self.claims:
            if not isinstance(claim, str):
                raise TypeError("claims의 모든 원소는 문자열이어야 합니다")

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"Invention(title='{self.title}', technical_field='{self.technical_field}')"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return f"{self.title} ({self.technical_field})"

    def __eq__(self, other: object) -> bool:
        """두 Invention 객체의 동등성을 검사합니다."""
        if not isinstance(other, Invention):
            return NotImplemented
        return (
            self.title == other.title
            and self.technical_field == other.technical_field
            and self.novelty == other.novelty
            and self.inventive_step == other.inventive_step
            and self.industrial_applicability == other.industrial_applicability
            and self.claims == other.claims
        )

    def __hash__(self) -> int:
        """해시값을 계산합니다."""
        return hash((self.title, self.technical_field, tuple(self.claims)))


@dataclass
class PatentClaim:
    """
    특허 청구항을 표현하는 클래스.

    독립항과 종속항을 모두 표현할 수 있습니다.

    Attributes:
        claim_number: 청구항 번호 (예: 1, 2, 3...)
        claim_type: 청구항 종류 ("독립항" 또는 "종속항")
        content: 청구항 내용
        dependent_on: 종속항인 경우 의존하는 청구항 번호
        scope: 청구 범위

    Example:
        >>> claim = PatentClaim(
        ...     claim_number=1,
        ...     claim_type="독립항",
        ...     content="방법의 단계들...",
        ...     scope="장치의 구조"
        ... )
    """

    claim_number: int
    claim_type: str
    content: str
    scope: str = ""
    dependent_on: Optional[int] = None

    def __post_init__(self) -> None:
        """
        객체 생성 후 유효성 검증.

        Raises:
            ValueError: 필드가 유효하지 않은 경우
            TypeError: 필드 타입이 올바르지 않은 경우
        """
        # claim_number 검증
        if not isinstance(self.claim_number, int):
            raise TypeError("claim_number은 정수여야 합니다")
        if self.claim_number <= 0:
            raise ValueError("claim_number은 양수여야 합니다")

        # claim_type 검증
        valid_types = {"독립항", "종속항"}
        if self.claim_type not in valid_types:
            raise ValueError(f"유효하지 않은 claim_type: {self.claim_type}")

        # content 검증
        if not isinstance(self.content, str):
            raise TypeError("content는 문자열이어야 합니다")
        if not self.content or not self.content.strip():
            raise ValueError("content는 비어있지 않은 문자열이어야 합니다")

        # scope 검증
        if not isinstance(self.scope, str):
            raise TypeError("scope는 문자열이어야 합니다")

        # dependent_on 검증 (종속항인 경우)
        if self.claim_type == "종속항":
            if self.dependent_on is None:
                raise ValueError("종속항은 dependent_on을 지정해야 합니다")
            if not isinstance(self.dependent_on, int):
                raise TypeError("dependent_on은 정수여야 합니다")

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"PatentClaim(claim_number={self.claim_number}, type='{self.claim_type}')"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        if self.claim_type == "종속항":
            return f"청구항 {self.claim_number} ({self.claim_type}, 제{self.dependent_on}항 의존)"
        return f"청구항 {self.claim_number} ({self.claim_type})"

    def __eq__(self, other: object) -> bool:
        """두 PatentClaim 객체의 동등성을 검사합니다."""
        if not isinstance(other, PatentClaim):
            return NotImplemented
        return (
            self.claim_number == other.claim_number
            and self.claim_type == other.claim_type
            and self.content == other.content
            and self.scope == other.scope
            and self.dependent_on == other.dependent_on
        )

    def __hash__(self) -> int:
        """해시값을 계산합니다."""
        return hash((self.claim_number, self.claim_type, self.content))


@dataclass
class PatentExamination:
    """
    특허 심사를 표현하는 클래스.

    출원부터 등록까지의 심사 과정을 모델링합니다.

    Attributes:
        application_number: 출원 번호
        application_date: 출원 날짜
        applicant_name: 출원인 이름
        status: 심사 상태 (출원, 심사 중, 거절, 등록)
        examination_results: 심사 결과들
        rejection_reasons: 거절 사유들

    Example:
        >>> exam = PatentExamination(
        ...     application_number="10-2024-0001234",
        ...     application_date="2024-01-15",
        ...     applicant_name="김철학",
        ...     status="심사중"
        ... )
    """

    application_number: str
    application_date: str
    applicant_name: str
    status: str = "출원"
    examination_results: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        객체 생성 후 유효성 검증.

        Raises:
            ValueError: 필드가 유효하지 않은 경우
            TypeError: 필드 타입이 올바르지 않은 경우
        """
        # application_number 검증
        if not isinstance(self.application_number, str):
            raise TypeError("application_number은 문자열이어야 합니다")
        if not self.application_number or not self.application_number.strip():
            raise ValueError("application_number은 비어있지 않은 문자열이어야 합니다")

        # application_date 검증
        if not isinstance(self.application_date, str):
            raise TypeError("application_date는 문자열이어야 합니다")
        self._validate_date_format(self.application_date)

        # applicant_name 검증
        if not isinstance(self.applicant_name, str):
            raise TypeError("applicant_name은 문자열이어야 합니다")
        if not self.applicant_name or not self.applicant_name.strip():
            raise ValueError("applicant_name은 비어있지 않은 문자열이어야 합니다")

        # status 검증
        valid_statuses = {"출원", "심사중", "거절", "등록", "포기"}
        if self.status not in valid_statuses:
            raise ValueError(f"유효하지 않은 status: {self.status}")

        # 리스트 검증
        if not isinstance(self.examination_results, list):
            raise TypeError("examination_results는 리스트여야 합니다")
        if not isinstance(self.rejection_reasons, list):
            raise TypeError("rejection_reasons는 리스트여야 합니다")

    @staticmethod
    def _validate_date_format(date_str: str) -> None:
        """
        날짜 형식을 검증합니다 (YYYY-MM-DD).

        Args:
            date_str: 검증할 날짜 문자열

        Raises:
            ValueError: 날짜 형식이 올바르지 않은 경우
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"application_date는 YYYY-MM-DD 형식이어야 합니다. 받은 값: {date_str}"
            )

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"PatentExamination("
            f"application_number='{self.application_number}', "
            f"status='{self.status}')"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return f"{self.application_number} - {self.applicant_name} ({self.status})"

    def __eq__(self, other: object) -> bool:
        """두 PatentExamination 객체의 동등성을 검사합니다."""
        if not isinstance(other, PatentExamination):
            return NotImplemented
        return (
            self.application_number == other.application_number
            and self.application_date == other.application_date
            and self.applicant_name == other.applicant_name
            and self.status == other.status
        )

    def __hash__(self) -> int:
        """해시값을 계산합니다."""
        return hash(
            (self.application_number, self.application_date, self.applicant_name)
        )
