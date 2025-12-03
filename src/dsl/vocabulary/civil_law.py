"""
Civil Law Vocabulary - 민법 관련 핵심 데이터 모델

이 모듈은 민법 조문, 법적 주체, 거래, 권리 등을 객체로 모델링합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class CivilLawStatute:
    """
    민법 조문을 객체화하는 클래스.

    민법의 각 조문을 구조화하여 요건(requirements)과 효과(effects),
    예외(exceptions)를 명시적으로 표현합니다.

    Attributes:
        statute_number: 조문 번호 (예: "제145조")
        title: 조문의 제목
        requirements: 성립 요건들 (List[str])
        effects: 법적 효과들 (List[str])
        exceptions: 예외 사유들 (List[str])
        related_precedents: 관련 판례 ID들 (List[str])

    Example:
        >>> statute = CivilLawStatute(
        ...     statute_number="제145조",
        ...     title="저작권자의 권리",
        ...     requirements=["독창성"],
        ...     effects=["복제권", "배포권"],
        ...     exceptions=["공정이용"]
        ... )
        >>> statute.statute_number
        '제145조'
    """

    statute_number: str
    title: str
    requirements: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    related_precedents: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        객체 생성 후 유효성 검증 및 정규화.

        Raises:
            ValueError: statute_number 또는 title이 비어있거나 유효하지 않은 경우
            TypeError: 리스트 필드의 타입이 올바르지 않은 경우
        """
        # statute_number 검증
        if not isinstance(self.statute_number, str):
            raise TypeError("statute_number은 문자열이어야 합니다")
        if not self.statute_number or not self.statute_number.strip():
            raise ValueError("statute_number은 비어있지 않은 문자열이어야 합니다")

        # title 검증
        if not isinstance(self.title, str):
            raise TypeError("title은 문자열이어야 합니다")
        if not self.title or not self.title.strip():
            raise ValueError("title은 비어있지 않은 문자열이어야 합니다")

        # 리스트 필드 검증 및 정규화
        self._validate_and_normalize_list("requirements", self.requirements)
        self._validate_and_normalize_list("effects", self.effects)
        self._validate_and_normalize_list("exceptions", self.exceptions)
        self._validate_and_normalize_list("related_precedents", self.related_precedents)

        # 중복 제거 (순서 유지)
        self.requirements = list(dict.fromkeys(self.requirements))
        self.effects = list(dict.fromkeys(self.effects))
        self.exceptions = list(dict.fromkeys(self.exceptions))
        self.related_precedents = list(dict.fromkeys(self.related_precedents))

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
            f"CivilLawStatute("
            f"statute_number='{self.statute_number}', "
            f"title='{self.title}', "
            f"requirements={self.requirements}, "
            f"effects={self.effects})"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return f"{self.statute_number} - {self.title}"

    def __eq__(self, other: object) -> bool:
        """두 Statute 객체의 동등성을 검사합니다."""
        if not isinstance(other, CivilLawStatute):
            return NotImplemented
        return (
            self.statute_number == other.statute_number
            and self.title == other.title
            and self.requirements == other.requirements
            and self.effects == other.effects
            and self.exceptions == other.exceptions
            and self.related_precedents == other.related_precedents
        )

    def __hash__(self) -> int:
        """해시값을 계산합니다."""
        return hash(
            (
                self.statute_number,
                self.title,
                tuple(self.requirements),
                tuple(self.effects),
                tuple(self.exceptions),
            )
        )


@dataclass
class Person:
    """
    법적 주체(저작권자, 침해자, 제3자 등)를 표현하는 클래스.

    법적 분쟁이나 거래에서의 당사자를 나타냅니다.

    Attributes:
        name: 사람의 이름
        role: 역할 (예: "저작권자", "침해자", "제3자")
        attributes: 추가 특성 (예: {"good_faith": True})

    Example:
        >>> person = Person(
        ...     name="홍길동",
        ...     role="저작권자",
        ...     attributes={"good_faith": True}
        ... )
        >>> person.name
        '홍길동'
    """

    VALID_ROLES = {
        "저작권자",
        "침해자",
        "제3자",
        "판매자",
        "구매자",
        "출원인",
        "심사관",
    }

    name: str
    role: str
    attributes: Dict[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        객체 생성 후 유효성 검증.

        Raises:
            ValueError: name 또는 role이 비어있는 경우
            TypeError: name이 문자열이 아닌 경우
        """
        # name 검증
        if not isinstance(self.name, str):
            raise TypeError("name은 문자열이어야 합니다")
        if not self.name or not self.name.strip():
            raise ValueError("name은 비어있지 않은 문자열이어야 합니다")

        # role 검증
        if not isinstance(self.role, str):
            raise TypeError("role은 문자열이어야 합니다")
        if not self.role or not self.role.strip():
            raise ValueError("role은 비어있지 않은 문자열이어야 합니다")

        # role이 유효한 값인지 확인
        if self.role not in self.VALID_ROLES:
            raise ValueError(
                f"유효하지 않은 role '{self.role}'. " f"유효한 값: {self.VALID_ROLES}"
            )

        # attributes 검증
        if not isinstance(self.attributes, dict):
            raise TypeError("attributes는 딕셔너리여야 합니다")

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return f"Person(name='{self.name}', role='{self.role}')"

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return f"{self.name} ({self.role})"

    def __eq__(self, other: object) -> bool:
        """두 Person 객체의 동등성을 검사합니다."""
        if not isinstance(other, Person):
            return NotImplemented
        return (
            self.name == other.name
            and self.role == other.role
            and self.attributes == other.attributes
        )

    def __hash__(self) -> int:
        """해시값을 계산합니다."""
        return hash((self.name, self.role))


@dataclass
class Transaction:
    """
    거래 또는 법적 행위를 표현하는 클래스.

    저작물의 구입, 양도, 라이센스 부여 등의 거래를 모델링합니다.

    Attributes:
        parties: 거래 당사자들 (List[Person])
        subject: 거래 대상 (예: "저작물", "특허권")
        consideration: 대가 (예: "100,000원")
        date: 거래 발생 날짜 (YYYY-MM-DD 형식)

    Example:
        >>> person1 = Person(name="홍길동", role="판매자")
        >>> person2 = Person(name="김영희", role="구매자")
        >>> transaction = Transaction(
        ...     parties=[person1, person2],
        ...     subject="저작물",
        ...     consideration="100,000원",
        ...     date="2025-01-01"
        ... )
    """

    parties: List[Person]
    subject: str
    consideration: str
    date: str

    def __post_init__(self) -> None:
        """
        객체 생성 후 유효성 검증.

        Raises:
            ValueError: 필수 필드가 비어있거나 형식이 잘못된 경우
            TypeError: 필드 타입이 올바르지 않은 경우
        """
        # parties 검증
        if not isinstance(self.parties, list):
            raise TypeError("parties는 리스트여야 합니다")
        if not self.parties or len(self.parties) == 0:
            raise ValueError("parties는 최소 1명 이상의 사람을 포함해야 합니다")

        for party in self.parties:
            if not isinstance(party, Person):
                raise TypeError("parties의 모든 원소는 Person이어야 합니다")

        # subject 검증
        if not isinstance(self.subject, str):
            raise TypeError("subject는 문자열이어야 합니다")
        if not self.subject or not self.subject.strip():
            raise ValueError("subject는 비어있지 않은 문자열이어야 합니다")

        # consideration 검증
        if not isinstance(self.consideration, str):
            raise TypeError("consideration은 문자열이어야 합니다")

        # date 검증 (YYYY-MM-DD 형식)
        if not isinstance(self.date, str):
            raise TypeError("date는 문자열이어야 합니다")
        self._validate_date_format(self.date)

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
                f"date는 YYYY-MM-DD 형식이어야 합니다. 받은 값: {date_str}"
            )

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"Transaction(parties={[str(p) for p in self.parties]}, "
            f"subject='{self.subject}', date='{self.date}')"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        parties_str = ", ".join(p.name for p in self.parties)
        return f"{parties_str} - {self.subject} ({self.date})"

    def __eq__(self, other: object) -> bool:
        """두 Transaction 객체의 동등성을 검사합니다."""
        if not isinstance(other, Transaction):
            return NotImplemented
        return (
            self.parties == other.parties
            and self.subject == other.subject
            and self.consideration == other.consideration
            and self.date == other.date
        )

    def __hash__(self) -> int:
        """해시값을 계산합니다."""
        return hash((tuple(self.parties), self.subject, self.consideration, self.date))


@dataclass
class LegalRight:
    """
    법적 권리(저작권, 특허권, 상표권 등)를 표현하는 클래스.

    법적 권리의 범위, 기간, 구제 수단 등을 명시합니다.

    Attributes:
        name: 권리명 (예: "저작권", "특허권")
        scope: 보호 범위 (예: "저작물")
        duration: 보호 기간 (예: "저작자의 생존 중 + 70년")
        remedies: 구제 수단들 (예: ["침해금지청구", "손해배상청구"])

    Example:
        >>> right = LegalRight(
        ...     name="저작권",
        ...     scope="저작물",
        ...     duration="저작자의 생존 중 + 70년",
        ...     remedies=["침해금지청구", "손해배상청구"]
        ... )
        >>> right.name
        '저작권'
    """

    name: str
    scope: str
    duration: str
    remedies: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        객체 생성 후 유효성 검증.

        Raises:
            ValueError: 필수 필드가 비어있는 경우
            TypeError: 필드 타입이 올바르지 않은 경우
        """
        # name 검증
        if not isinstance(self.name, str):
            raise TypeError("name은 문자열이어야 합니다")
        if not self.name or not self.name.strip():
            raise ValueError("name은 비어있지 않은 문자열이어야 합니다")

        # scope 검증
        if not isinstance(self.scope, str):
            raise TypeError("scope는 문자열이어야 합니다")
        if not self.scope or not self.scope.strip():
            raise ValueError("scope는 비어있지 않은 문자열이어야 합니다")

        # duration 검증
        if not isinstance(self.duration, str):
            raise TypeError("duration은 문자열이어야 합니다")
        if not self.duration or not self.duration.strip():
            raise ValueError("duration은 비어있지 않은 문자열이어야 합니다")

        # remedies 검증
        if not isinstance(self.remedies, list):
            raise TypeError("remedies는 리스트여야 합니다")

        for remedy in self.remedies:
            if not isinstance(remedy, str):
                raise TypeError("remedies의 모든 원소는 문자열이어야 합니다")

    def __repr__(self) -> str:
        """정식 문자열 표현."""
        return (
            f"LegalRight(name='{self.name}', scope='{self.scope}', "
            f"remedies={self.remedies})"
        )

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현."""
        return f"{self.name} - {self.scope}"

    def __eq__(self, other: object) -> bool:
        """두 LegalRight 객체의 동등성을 검사합니다."""
        if not isinstance(other, LegalRight):
            return NotImplemented
        return (
            self.name == other.name
            and self.scope == other.scope
            and self.duration == other.duration
            and self.remedies == other.remedies
        )

    def __hash__(self) -> int:
        """해시값을 계산합니다."""
        return hash((self.name, self.scope, self.duration, tuple(self.remedies)))
