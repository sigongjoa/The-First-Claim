"""
실제 특허법 데이터를 사용한 통합 테스트

온라인에서 다운로드한 실제 특허법 조문을 사용하여 PatentArticle 클래스를 검증합니다.
"""

import json
import pytest
from pathlib import Path
from src.dsl.vocabulary.patent_law import (
    PatentArticle,
    Invention,
    PatentClaim,
    PatentExamination,
)


class TestWithRealPatentLawData:
    """실제 특허법 데이터를 사용한 통합 테스트"""

    @pytest.fixture(scope="class")
    def patent_law_articles(self):
        """JSON 파일에서 특허법 조문 로드"""
        json_path = Path(__file__).parent.parent / "data" / "patent_law_articles.json"
        with open(json_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
        return articles

    def test_data_file_exists(self, patent_law_articles):
        """특허법 데이터 파일이 존재하는지 확인"""
        assert patent_law_articles is not None
        assert len(patent_law_articles) > 0
        print(f"✅ {len(patent_law_articles)}개의 특허법 조문 로드됨")

    def test_first_article_structure(self, patent_law_articles):
        """첫 번째 조문의 구조 확인"""
        first_article = patent_law_articles[0]
        assert "number" in first_article
        assert "title" in first_article
        assert "content" in first_article
        assert "requirements" in first_article
        assert "effects" in first_article
        assert "exceptions" in first_article

    def test_create_article_from_real_data(self, patent_law_articles):
        """실제 특허법 데이터로 PatentArticle 객체 생성"""
        article = patent_law_articles[0]

        patent_article = PatentArticle(
            article_number=article["number"],
            title=article["title"],
            content=article.get("content", ""),
            requirements=article.get("requirements", []),
            effects=article.get("effects", []),
            exceptions=article.get("exceptions", []),
        )

        assert patent_article.article_number == article["number"]
        assert patent_article.title == article["title"]

    def test_multiple_articles_from_real_data(self, patent_law_articles):
        """여러 특허법 조문으로 객체 생성"""
        articles = []
        for article_data in patent_law_articles:
            article = PatentArticle(
                article_number=article_data["number"],
                title=article_data["title"],
                content=article_data.get("content", ""),
                requirements=article_data.get("requirements", []),
                effects=article_data.get("effects", []),
                exceptions=article_data.get("exceptions", []),
            )
            articles.append(article)

        assert len(articles) == len(patent_law_articles)
        print(f"✅ {len(articles)}개의 PatentArticle 객체 생성 성공")

    def test_article_with_requirements(self, patent_law_articles):
        """요건이 있는 조문 찾기"""
        articles_with_requirements = []
        for article_data in patent_law_articles:
            if article_data.get("requirements"):
                article = PatentArticle(
                    article_number=article_data["number"],
                    title=article_data["title"],
                    requirements=article_data["requirements"],
                )
                articles_with_requirements.append(article)

        print(f"📊 요건이 있는 조문: {len(articles_with_requirements)}개")
        assert len(articles_with_requirements) > 0

    def test_article_with_effects(self, patent_law_articles):
        """효과가 있는 조문 찾기"""
        articles_with_effects = []
        for article_data in patent_law_articles:
            if article_data.get("effects"):
                article = PatentArticle(
                    article_number=article_data["number"],
                    title=article_data["title"],
                    effects=article_data["effects"],
                )
                articles_with_effects.append(article)

        print(f"📊 효과가 있는 조문: {len(articles_with_effects)}개")
        assert len(articles_with_effects) > 0

    def test_article_equality_with_real_data(self, patent_law_articles):
        """같은 데이터로 생성한 두 조문은 동일한지 확인"""
        article_data = patent_law_articles[3]

        article1 = PatentArticle(
            article_number=article_data["number"],
            title=article_data["title"],
            content=article_data.get("content", ""),
            requirements=article_data.get("requirements", []),
            effects=article_data.get("effects", []),
        )

        article2 = PatentArticle(
            article_number=article_data["number"],
            title=article_data["title"],
            content=article_data.get("content", ""),
            requirements=article_data.get("requirements", []),
            effects=article_data.get("effects", []),
        )

        assert article1 == article2

    def test_article_string_representation(self, patent_law_articles):
        """조문의 문자열 표현 확인"""
        article_data = patent_law_articles[0]
        article = PatentArticle(
            article_number=article_data["number"], title=article_data["title"]
        )

        assert str(article) == f"{article_data['number']} - {article_data['title']}"

    def test_article_hash_consistency(self, patent_law_articles):
        """같은 조문의 해시값이 일관성 있는지 확인"""
        article_data = patent_law_articles[5]

        article1 = PatentArticle(
            article_number=article_data["number"], title=article_data["title"]
        )

        article2 = PatentArticle(
            article_number=article_data["number"], title=article_data["title"]
        )

        assert hash(article1) == hash(article2)

    def test_article_collection_with_set(self, patent_law_articles):
        """조문을 set에 저장할 수 있는지 확인 (해시 가능)"""
        article_set = set()

        for article_data in patent_law_articles:
            article = PatentArticle(
                article_number=article_data["number"], title=article_data["title"]
            )
            article_set.add(article)

        # set의 크기는 조문 개수와 같아야 함
        assert len(article_set) == len(patent_law_articles)
        print(f"✅ {len(article_set)}개의 고유한 조문을 set에 저장 성공")


class TestPatentLawApplicationScenarios:
    """특허법 적용 시나리오 테스트"""

    def test_create_invention_scenario(self):
        """발명 생성 시나리오"""
        invention = Invention(
            title="개선된 배터리 기술",
            technical_field="전기화학",
            novelty=True,
            inventive_step=True,
            industrial_applicability=True,
            claims=[
                "1. 높은 에너지 밀도를 가진 배터리",
                "2. 빠른 충전 기술",
                "3. 안전한 배터리 관리 시스템",
            ],
        )

        assert invention.title == "개선된 배터리 기술"
        assert len(invention.claims) == 3
        assert invention.novelty is True

    def test_patent_application_with_claims(self):
        """청구항을 포함한 특허 출원"""
        independent_claim = PatentClaim(
            claim_number=1,
            claim_type="독립항",
            content="배터리의 양극은 리튬코발트산화물로 이루어진다",
            scope="배터리 장치",
        )

        dependent_claim1 = PatentClaim(
            claim_number=2,
            claim_type="종속항",
            content="제1항의 배터리에서 전해질은 유기용매로 이루어진다",
            dependent_on=1,
        )

        dependent_claim2 = PatentClaim(
            claim_number=3,
            claim_type="종속항",
            content="제1항의 배터리에서 음극은 흑연으로 이루어진다",
            dependent_on=1,
        )

        claims = [independent_claim, dependent_claim1, dependent_claim2]

        assert len(claims) == 3
        assert claims[0].claim_type == "독립항"
        assert claims[1].dependent_on == 1
        assert claims[2].dependent_on == 1

    def test_patent_examination_lifecycle(self):
        """특허 심사 라이프사이클"""
        # 출원
        exam_application = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
            status="출원",
        )

        assert exam_application.status == "출원"

        # 심사 중
        exam_examination = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
            status="심사중",
            examination_results=["1차 심사 진행중"],
        )

        assert exam_examination.status == "심사중"
        assert len(exam_examination.examination_results) > 0

        # 거절
        exam_rejection = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
            status="거절",
            rejection_reasons=["선행기술과의 신규성 부재"],
        )

        assert exam_rejection.status == "거절"
        assert len(exam_rejection.rejection_reasons) > 0

        # 등록
        exam_registration = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
            status="등록",
        )

        assert exam_registration.status == "등록"

    def test_patent_article_references_in_examination(self):
        """심사에서 특허법 조문 참조"""
        # 특허법 제32조 (신규성)
        novelty_article = PatentArticle(
            article_number="제32조",
            title="(신규성)",
            content="다음 중 어느 하나에 해당하는 발명에 대해서는 특허를 주지 아니한다.",
            requirements=["공지", "공용"],
            effects=["거절 사유"],
        )

        # 특허법 제33조 (진보성)
        inventive_step_article = PatentArticle(
            article_number="제33조",
            title="(진보성)",
            content="특허출원 전에 그 발명이 속하는 기술분야에서 통상적인 지식을 가진 자가...",
            requirements=["기술분야 통상인"],
            effects=["진보성 판단"],
        )

        assert novelty_article.article_number == "제32조"
        assert inventive_step_article.article_number == "제33조"

        # 심사에서 거절 사유로 사용
        exam = PatentExamination(
            application_number="10-2024-0001234",
            application_date="2024-01-15",
            applicant_name="김철학",
            status="거절",
            rejection_reasons=[
                f"{novelty_article.article_number} 해당: 신규성 부재",
                f"{inventive_step_article.article_number} 해당: 진보성 부재",
            ],
        )

        assert len(exam.rejection_reasons) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
