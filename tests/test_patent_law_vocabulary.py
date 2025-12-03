"""
Patent Law Vocabulary 테스트

PatentArticle, Invention, PatentClaim, PatentExamination 클래스를 테스트합니다.
"""

import pytest
from src.dsl.vocabulary.patent_law import (
    PatentArticle,
    Invention,
    PatentClaim,
    PatentExamination,
)


class TestPatentArticleCreation:
    """PatentArticle 클래스 생성 및 검증 테스트"""

    def test_valid_article_creation_full(self):
        """전체 정보를 포함한 유효한 조문 생성"""
        article = PatentArticle(
            article_number="제1조",
            title="(목적)",
            content="이 법은 발명에 대한 특허권의 취득, 갱신 및 보호에 관한 사항을 규정함으로써...",
            requirements=["발명"],
            effects=["특허권 설정"],
            exceptions=["예외 사항"],
        )

        assert article.article_number == "제1조"
        assert article.title == "(목적)"
        assert len(article.requirements) == 1
        assert len(article.effects) == 1

    def test_valid_article_creation_minimal(self):
        """최소 정보만으로 조문 생성"""
        article = PatentArticle(article_number="제1조", title="(목적)")

        assert article.article_number == "제1조"
        assert article.title == "(목적)"
        assert article.content == ""
        assert article.requirements == []

    def test_empty_article_number(self):
        """빈 조문 번호로 생성 시도"""
        with pytest.raises(ValueError, match="비어있지 않은"):
            PatentArticle(article_number="", title="(목적)")

    def test_empty_title(self):
        """빈 제목으로 생성 시도"""
        with pytest.raises(ValueError, match="비어있지 않은"):
            PatentArticle(article_number="제1조", title="")

    def test_duplicate_requirements(self):
        """중복된 요건은 자동으로 제거"""
        article = PatentArticle(
            article_number="제1조",
            title="(목적)",
            requirements=["요건1", "요건1", "요건2"],
        )

        assert len(article.requirements) == 2
        assert article.requirements == ["요건1", "요건2"]

    def test_requirements_type_error(self):
        """유효하지 않은 타입의 requirements"""
        with pytest.raises(TypeError, match="리스트"):
            PatentArticle(
                article_number="제1조", title="(목적)", requirements="not a list"
            )

    def test_article_equality(self):
        """두 조문의 동등성 검사"""
        article1 = PatentArticle(article_number="제1조", title="(목적)")
        article2 = PatentArticle(article_number="제1조", title="(목적)")

        assert article1 == article2

    def test_article_string_representation(self):
        """조문의 문자열 표현"""
        article = PatentArticle(article_number="제1조", title="(목적)")

        assert str(article) == "제1조 - (목적)"

    def test_article_hash_consistency(self):
        """같은 조문의 해시값이 일관성 있음"""
        article1 = PatentArticle(article_number="제1조", title="(목적)")
        article2 = PatentArticle(article_number="제1조", title="(목적)")

        assert hash(article1) == hash(article2)


class TestInventionCreation:
    """Invention 클래스 생성 및 검증 테스트"""

    def test_valid_invention_creation(self):
        """유효한 발명 생성"""
        invention = Invention(
            title="개선된 배터리",
            technical_field="전자기술",
            novelty=True,
            inventive_step=True,
            industrial_applicability=True,
            claims=["배터리 구조", "배터리 재료"],
        )

        assert invention.title == "개선된 배터리"
        assert invention.technical_field == "전자기술"
        assert invention.novelty is True
        assert len(invention.claims) == 2

    def test_invention_minimal_creation(self):
        """최소 정보로 발명 생성"""
        invention = Invention(
            title="배터리",
            technical_field="전자기술",
        )

        assert invention.title == "배터리"
        assert invention.novelty is False
        assert invention.claims == []

    def test_empty_title(self):
        """빈 제목으로 발명 생성 시도"""
        with pytest.raises(ValueError):
            Invention(title="", technical_field="전자기술")

    def test_empty_technical_field(self):
        """빈 기술분야로 발명 생성 시도"""
        with pytest.raises(ValueError):
            Invention(title="배터리", technical_field="")

    def test_invention_equality(self):
        """두 발명의 동등성 검사"""
        inv1 = Invention(title="배터리", technical_field="전자기술")
        inv2 = Invention(title="배터리", technical_field="전자기술")

        assert inv1 == inv2

    def test_invention_string_representation(self):
        """발명의 문자열 표현"""
        invention = Invention(title="배터리", technical_field="전자기술")

        assert str(invention) == "배터리 (전자기술)"


class TestPatentClaimCreation:
    """PatentClaim 클래스 생성 및 검증 테스트"""

    def test_valid_independent_claim(self):
        """유효한 독립항 생성"""
        claim = PatentClaim(
            claim_number=1,
            claim_type="독립항",
            content="배터리의 구조는 다음과 같다...",
            scope="장치",
        )

        assert claim.claim_number == 1
        assert claim.claim_type == "독립항"
        assert claim.dependent_on is None

    def test_valid_dependent_claim(self):
        """유효한 종속항 생성"""
        claim = PatentClaim(
            claim_number=2,
            claim_type="종속항",
            content="제1항의 배터리에서...",
            dependent_on=1,
        )

        assert claim.claim_number == 2
        assert claim.claim_type == "종속항"
        assert claim.dependent_on == 1

    def test_dependent_claim_without_dependent_on(self):
        """종속항이지만 dependent_on이 없을 때"""
        with pytest.raises(ValueError):
            PatentClaim(
                claim_number=2,
                claim_type="종속항",
                content="제1항의 배터리에서...",
            )

    def test_invalid_claim_type(self):
        """유효하지 않은 청구항 종류"""
        with pytest.raises(ValueError, match="유효하지 않은"):
            PatentClaim(
                claim_number=1,
                claim_type="복합항",
                content="내용",
            )

    def test_claim_number_zero(self):
        """청구항 번호가 0인 경우"""
        with pytest.raises(ValueError):
            PatentClaim(
                claim_number=0,
                claim_type="독립항",
                content="내용",
            )

    def test_empty_content(self):
        """빈 내용으로 청구항 생성 시도"""
        with pytest.raises(ValueError):
            PatentClaim(
                claim_number=1,
                claim_type="독립항",
                content="",
            )

    def test_claim_string_representation_independent(self):
        """독립항의 문자열 표현"""
        claim = PatentClaim(
            claim_number=1,
            claim_type="독립항",
            content="내용",
        )

        assert str(claim) == "청구항 1 (독립항)"

    def test_claim_string_representation_dependent(self):
        """종속항의 문자열 표현"""
        claim = PatentClaim(
            claim_number=2,
            claim_type="종속항",
            content="내용",
            dependent_on=1,
        )

        assert "제1항 의존" in str(claim)

    def test_claim_equality(self):
        """두 청구항의 동등성 검사"""
        claim1 = PatentClaim(claim_number=1, claim_type="독립항", content="내용")
        claim2 = PatentClaim(claim_number=1, claim_type="독립항", content="내용")

        assert claim1 == claim2


class TestPatentExaminationCreation:
    """PatentExamination 클래스 생성 및 검증 테스트"""

    def test_valid_examination_creation(self):
        """유효한 심사 생성"""
        exam = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
            status="심사중",
            examination_results=["1차 심사 완료"],
            rejection_reasons=["거절 사유 없음"],
        )

        assert exam.application_number == "10-2024-0001234"
        assert exam.applicant_name == "김철학"
        assert exam.status == "심사중"

    def test_examination_default_status(self):
        """기본 상태는 '출원'"""
        exam = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
        )

        assert exam.status == "출원"

    def test_invalid_date_format(self):
        """유효하지 않은 날짜 형식"""
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            PatentExamination(
                application_number="10-2024-0001234",
                application_date="2024/01/15",  # 잘못된 형식
                applicant_name="김철학",
            )

    def test_empty_application_number(self):
        """빈 출원 번호"""
        with pytest.raises(ValueError):
            PatentExamination(
                application_number="",
                application_date="2024-01-15",
                applicant_name="김철학",
            )

    def test_empty_applicant_name(self):
        """빈 출원인 이름"""
        with pytest.raises(ValueError):
            PatentExamination(
                application_number="10-2024-0001234",
                application_date="2024-01-15",
                applicant_name="",
            )

    def test_invalid_status(self):
        """유효하지 않은 심사 상태"""
        with pytest.raises(ValueError):
            PatentExamination(
                application_number="10-2024-0001234",
                application_date="2024-01-15",
                applicant_name="김철학",
                status="완료",  # 유효하지 않은 상태
            )

    def test_valid_statuses(self):
        """모든 유효한 상태 테스트"""
        valid_statuses = ["출원", "심사중", "거절", "등록", "포기"]

        for status in valid_statuses:
            exam = PatentExamination(
                application_number="10-2024-0001234",
                application_date="2024-01-15",
                applicant_name="김철학",
                status=status,
            )
            assert exam.status == status

    def test_examination_string_representation(self):
        """심사의 문자열 표현"""
        exam = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
            status="심사중",
        )

        assert str(exam) == "10-2024-0001234 - 김철학 (심사중)"

    def test_examination_equality(self):
        """두 심사의 동등성 검사"""
        exam1 = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
        )
        exam2 = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
        )

        assert exam1 == exam2


class TestPatentLawIntegration:
    """Patent Law 모델들의 통합 테스트"""

    def test_invention_with_claims(self):
        """발명에 청구항 추가"""
        invention = Invention(
            title="개선된 배터리",
            technical_field="전자기술",
            novelty=True,
            claims=["1. 배터리 구조", "2. 배터리 재료"],
        )

        assert len(invention.claims) == 2

    def test_patent_examination_with_status_progression(self):
        """심사 상태 변경"""
        exam = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
            status="출원",
        )

        # 상태 변경 시뮬레이션
        assert exam.status == "출원"

        # 새로운 상태로 재생성
        exam_updated = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
            status="등록",
        )
        assert exam_updated.status == "등록"

    def test_multiple_claims_creation(self):
        """여러 청구항 생성"""
        claims = [
            PatentClaim(claim_number=1, claim_type="독립항", content="청구항 1 내용"),
            PatentClaim(
                claim_number=2,
                claim_type="종속항",
                content="청구항 2 내용",
                dependent_on=1,
            ),
            PatentClaim(
                claim_number=3,
                claim_type="종속항",
                content="청구항 3 내용",
                dependent_on=1,
            ),
        ]

        assert len(claims) == 3
        assert claims[0].claim_type == "독립항"
        assert claims[1].dependent_on == 1
        assert claims[2].dependent_on == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
