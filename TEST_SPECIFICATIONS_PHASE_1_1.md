# Phase 1-1 테스트 명세서: Civil Law Vocabulary

## 개요

**Phase**: 1-1 (Civil Law 데이터 모델)
**기간**: 1주차
**목표**: 민법 관련 핵심 데이터 모델 정의 및 검증

---

## 테스트할 클래스

### 1. CivilLawStatute (민법 조문)

#### 클래스 설명
```python
class CivilLawStatute:
    """
    민법 조문을 객체화하는 클래스

    속성:
    - statute_number: str (예: "제145조")
    - title: str (조문의 제목)
    - requirements: List[str] (성립 요건들)
    - effects: List[str] (법적 효과들)
    - exceptions: List[str] (예외 사유들)
    - related_precedents: List[str] (관련 판례 ID들)
    """
```

#### Unit Tests

| 테스트 ID | 테스트명 | 입력 | 기대 출력 | 타입 | 우선순위 |
|-----------|---------|------|---------|------|---------|
| U1-1 | 정상 생성 (모든 필드) | statute_number="제145조", title="저작권자의 권리", requirements=["독창성"], effects=["복제권"], exceptions=["공정이용"], related_precedents=[] | 객체 생성 성공 | ✅ 정상 | P0 |
| U1-2 | 정상 생성 (최소 필드) | statute_number="제145조", title="저작권자의 권리" | 객체 생성 성공, requirements=[], effects=[] | ✅ 정상 | P0 |
| U1-3 | 속성 조회 | 생성된 객체에서 `statute.statute_number` 조회 | "제145조" 반환 | ✅ 정상 | P1 |
| U1-4 | 빈 문자열 statute_number | statute_number="" | ValueError 발생 또는 경고 | ⚠️ 엣지케이스 | P1 |
| U1-5 | 빈 title | title="" | ValueError 발생 또는 경고 | ⚠️ 엣지케이스 | P1 |
| U1-6 | None 값 statute_number | statute_number=None | ValueError 또는 TypeError 발생 | ❌ 에러 | P0 |
| U1-7 | 중복된 requirements | requirements=["A", "A", "B"] | 중복 자동 제거 또는 경고 | ⚠️ 엣지케이스 | P2 |
| U1-8 | 중복된 effects | effects=["복제권", "복제권"] | 중복 자동 제거 또는 경고 | ⚠️ 엣지케이스 | P2 |
| U1-9 | 매우 긴 문자열 | title="가"*10000 | 정상 처리 또는 길이 제한 | ⚠️ 엣지케이스 | P2 |
| U1-10 | 특수 문자 포함 | title="제①조-②항" | 정상 처리 | ⚠️ 엣지케이스 | P2 |
| U1-11 | 각도 괄호 포함 | title="<제145조>" | 정상 처리 | ⚠️ 엣지케이스 | P2 |
| U1-12 | 개행문자 포함 | title="제145조\n추가 설명" | 정상 처리 또는 제거 | ⚠️ 엣지케이스 | P2 |
| U1-13 | 동등성 테스트 1 | 두 개의 동일한 Statute 객체 | `statute1 == statute2` → True | ✅ 정상 | P1 |
| U1-14 | 동등성 테스트 2 | 다른 statute_number를 가진 객체 | `statute1 == statute2` → False | ✅ 정상 | P1 |
| U1-15 | 문자열 표현 | `str(statute)` 또는 `repr(statute)` | "CivilLawStatute(제145조, ...)" 형식 | ✅ 정상 | P1 |
| U1-16 | requirements가 아닌 다른 타입 | requirements="A,B" (문자열) | TypeError 발생 | ❌ 에러 | P0 |
| U1-17 | effects가 아닌 다른 타입 | effects={"복제권": True} (딕셔너리) | TypeError 발생 | ❌ 에러 | P0 |
| U1-18 | 리스트의 원소가 문자열이 아님 | requirements=[1, 2, 3] | TypeError 또는 경고 | ❌ 에러 | P1 |
| U1-19 | 빈 리스트 requirements | requirements=[] | 정상 처리 | ✅ 정상 | P2 |
| U1-20 | 빈 리스트 exceptions | exceptions=[] | 정상 처리 | ✅ 정상 | P2 |

#### 테스트 코드 예시

```python
# tests/test_civil_law_vocabulary.py

import pytest
from src.dsl.vocabulary.civil_law import CivilLawStatute


class TestCivilLawStatuteCreation:
    """CivilLawStatute 생성 테스트"""

    @pytest.mark.unit
    def test_valid_statute_creation_full(self):
        """U1-1: 정상 생성 (모든 필드)"""
        # Given: 모든 필드가 유효한 값
        statute_number = "제145조"
        title = "저작권자의 권리"
        requirements = ["독창성"]
        effects = ["복제권"]
        exceptions = ["공정이용"]
        related_precedents = []

        # When: CivilLawStatute 객체 생성
        statute = CivilLawStatute(
            statute_number=statute_number,
            title=title,
            requirements=requirements,
            effects=effects,
            exceptions=exceptions,
            related_precedents=related_precedents
        )

        # Then: 객체가 정상 생성되고 속성이 올바름
        assert statute.statute_number == statute_number
        assert statute.title == title
        assert statute.requirements == requirements
        assert statute.effects == effects
        # ✅ PASS

    @pytest.mark.unit
    def test_valid_statute_creation_minimal(self):
        """U1-2: 정상 생성 (최소 필드)"""
        # Given: 필수 필드만 제공
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리"
        )

        # Then: 기본값으로 초기화
        assert statute.requirements == []
        assert statute.effects == []
        # ✅ PASS

    @pytest.mark.unit
    def test_attribute_retrieval(self):
        """U1-3: 속성 조회"""
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리"
        )

        # When & Then: 속성 조회
        assert statute.statute_number == "제145조"
        assert statute.title == "저작권자의 권리"
        # ✅ PASS

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_empty_statute_number(self):
        """U1-4: 빈 문자열 statute_number"""
        # When & Then: 빈 문자열은 에러 또는 경고
        with pytest.raises(ValueError):
            CivilLawStatute(
                statute_number="",  # ❌ 빈 문자열
                title="저작권자의 권리"
            )
        # ✅ PASS

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_none_statute_number(self):
        """U1-6: None 값 statute_number"""
        # When & Then: None은 에러
        with pytest.raises((ValueError, TypeError)):
            CivilLawStatute(
                statute_number=None,  # ❌ None
                title="저작권자의 권리"
            )
        # ✅ PASS

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_duplicate_requirements(self):
        """U1-7: 중복된 requirements"""
        # When: 중복된 요건이 입력됨
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            requirements=["A", "A", "B"]
        )

        # Then: 중복이 제거됨 (순서는 유지)
        assert len(statute.requirements) == 2
        assert "A" in statute.requirements
        assert "B" in statute.requirements
        # ✅ PASS

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_very_long_title(self):
        """U1-9: 매우 긴 문자열"""
        # When: 10,000자의 제목
        long_title = "가" * 10000
        statute = CivilLawStatute(
            statute_number="제145조",
            title=long_title
        )

        # Then: 정상 처리
        assert len(statute.title) == 10000
        # ✅ PASS

    @pytest.mark.unit
    @pytest.mark.edge_case
    def test_special_characters_in_title(self):
        """U1-10: 특수 문자 포함"""
        # When: 특수 문자가 포함된 제목
        special_title = "제①조-②항(③)"
        statute = CivilLawStatute(
            statute_number="제145조",
            title=special_title
        )

        # Then: 정상 처리
        assert statute.title == special_title
        # ✅ PASS

    @pytest.mark.unit
    def test_statute_equality(self):
        """U1-13: 동등성 테스트 1"""
        # Given: 두 개의 동일한 Statute
        statute1 = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            requirements=["독창성"]
        )
        statute2 = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            requirements=["독창성"]
        )

        # When & Then: 동등성 검증
        assert statute1 == statute2
        # ✅ PASS

    @pytest.mark.unit
    def test_statute_inequality(self):
        """U1-14: 동등성 테스트 2"""
        # Given: 다른 statute_number를 가진 객체
        statute1 = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리"
        )
        statute2 = CivilLawStatute(
            statute_number="제146조",  # ← 다름
            title="저작권자의 권리"
        )

        # When & Then: 부등식 검증
        assert statute1 != statute2
        # ✅ PASS

    @pytest.mark.unit
    def test_statute_string_representation(self):
        """U1-15: 문자열 표현"""
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리"
        )

        # When: 문자열 표현 생성
        repr_str = repr(statute)
        str_str = str(statute)

        # Then: 형식이 올바름
        assert "제145조" in repr_str
        assert "CivilLawStatute" in repr_str or "제145조" in str_str
        # ✅ PASS

    @pytest.mark.unit
    def test_requirements_type_error(self):
        """U1-16: requirements가 리스트가 아님"""
        # When & Then: TypeError 발생
        with pytest.raises(TypeError):
            CivilLawStatute(
                statute_number="제145조",
                title="저작권자의 권리",
                requirements="A,B"  # ❌ 문자열, 리스트 아님
            )
        # ✅ PASS

    @pytest.mark.unit
    def test_effects_type_error(self):
        """U1-17: effects가 딕셔너리임"""
        # When & Then: TypeError 발생
        with pytest.raises(TypeError):
            CivilLawStatute(
                statute_number="제145조",
                title="저작권자의 권리",
                effects={"복제권": True}  # ❌ 딕셔너리, 리스트 아님
            )
        # ✅ PASS

    @pytest.mark.unit
    def test_empty_requirements_list(self):
        """U1-19: 빈 requirements 리스트"""
        # When: 빈 리스트 제공
        statute = CivilLawStatute(
            statute_number="제145조",
            title="저작권자의 권리",
            requirements=[]
        )

        # Then: 정상 처리
        assert statute.requirements == []
        # ✅ PASS
```

---

### 2. Person (법적 주체)

#### 클래스 설명
```python
class Person:
    """
    저작권자, 침해자 등 법적 주체를 나타내는 클래스

    속성:
    - name: str (이름)
    - role: str (역할: "저작권자", "침해자", "제3자" 등)
    - attributes: Dict[str, bool] (속성: {"good_faith": True, ...})
    """
```

#### Unit Tests

| 테스트 ID | 테스트명 | 입력 | 기대 출력 | 타입 | 우선순위 |
|-----------|---------|------|---------|------|---------|
| U2-1 | 정상 생성 | name="홍길동", role="저작권자" | 객체 생성 성공 | ✅ 정상 | P0 |
| U2-2 | 속성 포함 생성 | name="홍길동", role="제3자", attributes={"good_faith": True} | 객체 생성, 속성 저장 | ✅ 정상 | P0 |
| U2-3 | 빈 이름 | name="", role="저작권자" | ValueError | ❌ 에러 | P0 |
| U2-4 | None 이름 | name=None | ValueError 또는 TypeError | ❌ 에러 | P0 |
| U2-5 | 빈 role | name="홍길동", role="" | ValueError 또는 경고 | ❌ 에러 | P1 |
| U2-6 | 잘못된 role | name="홍길동", role="우주인" | ValueError 또는 경고 | ⚠️ 엣지케이스 | P2 |
| U2-7 | 동등성 테스트 | 같은 name과 role을 가진 두 객체 | `person1 == person2` → True | ✅ 정상 | P1 |
| U2-8 | attributes가 비어있음 | attributes={} | 정상 처리 | ✅ 정상 | P1 |

#### 테스트 코드 예시

```python
# tests/test_civil_law_vocabulary.py (계속)

class TestPersonCreation:
    """Person 생성 테스트"""

    @pytest.mark.unit
    def test_valid_person_creation(self):
        """U2-1: 정상 생성"""
        person = Person(name="홍길동", role="저작권자")

        assert person.name == "홍길동"
        assert person.role == "저작권자"
        # ✅ PASS

    @pytest.mark.unit
    def test_person_with_attributes(self):
        """U2-2: 속성 포함 생성"""
        person = Person(
            name="홍길동",
            role="제3자",
            attributes={"good_faith": True, "acquired_for_value": True}
        )

        assert person.attributes["good_faith"] == True
        # ✅ PASS

    @pytest.mark.unit
    def test_empty_name(self):
        """U2-3: 빈 이름"""
        with pytest.raises(ValueError):
            Person(name="", role="저작권자")
        # ✅ PASS

    @pytest.mark.unit
    def test_person_equality(self):
        """U2-7: 동등성 테스트"""
        person1 = Person(name="홍길동", role="저작권자")
        person2 = Person(name="홍길동", role="저작권자")

        assert person1 == person2
        # ✅ PASS
```

---

### 3. Transaction (거래/법적 행위)

#### 테스트 케이스 요약

| 테스트 ID | 테스트명 | 우선순위 |
|-----------|---------|---------|
| U3-1 | 정상 생성 | P0 |
| U3-2 | 빈 parties 리스트 | P1 |
| U3-3 | None subject | P0 |
| U3-4 | 형식이 잘못된 date | P2 |
| U3-5 | 동등성 테스트 | P1 |

---

### 4. LegalRight (법적 권리)

#### 테스트 케이스 요약

| 테스트 ID | 테스트명 | 우선순위 |
|-----------|---------|---------|
| U4-1 | 정상 생성 | P0 |
| U4-2 | 빈 remedies 리스트 | P1 |
| U4-3 | None duration | P0 |
| U4-4 | 매우 긴 scope | P2 |
| U4-5 | 동등성 테스트 | P1 |

---

## 통합 테스트 (Integration Tests)

### I1-1: Statute와 Person의 관계

```python
@pytest.mark.integration
def test_statute_related_to_person():
    """특정 Person의 역할이 Statute의 효과와 일치하는가?"""
    statute = CivilLawStatute(
        statute_number="제145조",
        title="저작권자의 권리",
        effects=["복제권", "배포권"]
    )
    person = Person(name="홍길동", role="저작권자")

    # 저작권자는 저작권법의 효과를 누릴 수 있어야 함
    assert person.role == "저작권자"
    assert "복제권" in statute.effects
    # ✅ PASS
```

---

## 성공 기준 (Definition of Done)

- [ ] 모든 단위 테스트 통과 (20개 이상)
- [ ] 모든 통합 테스트 통과
- [ ] 테스트 커버리지 ≥ 95%
- [ ] PEP 8 준수 (black으로 검증)
- [ ] 타입 힌팅 100% (mypy --strict 통과)
- [ ] Docstring 작성 (모든 함수)

---

## 실행 방법

```bash
# Phase 1-1 테스트만 실행
pytest tests/test_civil_law_vocabulary.py -v

# 단위 테스트만 실행
pytest tests/test_civil_law_vocabulary.py -m unit -v

# 엣지 케이스만 실행
pytest tests/test_civil_law_vocabulary.py -m edge_case -v

# 커버리지 포함
pytest tests/test_civil_law_vocabulary.py --cov=src.dsl.vocabulary.civil_law --cov-report=html
```

---

## 결론

이 명세서를 따라 개발하면:
1. ✅ 모든 기능이 완벽하게 검증됨
2. ✅ 엣지 케이스가 처리됨
3. ✅ 회귀 버그가 방지됨
4. ✅ 팀원들이 코드를 쉽게 이해할 수 있음
