"""
실제 민법 데이터를 사용한 통합 테스트

PDF에서 추출한 실제 민법 조문을 사용하여 CivilLawStatute 클래스를 검증합니다.
"""

import json
import pytest
from pathlib import Path
from src.dsl.vocabulary.civil_law import (
    CivilLawStatute,
    Person,
    Transaction,
    LegalRight,
)


class TestWithRealCivilLawData:
    """실제 민법 데이터를 사용한 통합 테스트"""

    @pytest.fixture(scope="class")
    def civil_law_articles(self):
        """JSON 파일에서 민법 조문 로드"""
        json_path = Path(__file__).parent.parent / "data" / "civil_law_articles.json"
        with open(json_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
        return articles

    def test_data_file_exists(self, civil_law_articles):
        """민법 데이터 파일이 존재하는지 확인"""
        assert civil_law_articles is not None
        assert len(civil_law_articles) > 0
        print(f"✅ {len(civil_law_articles)}개의 민법 조문 로드됨")

    def test_first_article_structure(self, civil_law_articles):
        """첫 번째 조문의 구조 확인"""
        first_article = civil_law_articles[0]
        assert "number" in first_article
        assert "title" in first_article
        assert "content" in first_article
        assert "requirements" in first_article
        assert "effects" in first_article
        assert "exceptions" in first_article

    def test_create_statute_from_real_data(self, civil_law_articles):
        """실제 민법 데이터로 CivilLawStatute 객체 생성"""
        article = civil_law_articles[0]

        statute = CivilLawStatute(
            statute_number=article["number"],
            title=article["title"],
            requirements=article["requirements"],
            effects=article["effects"],
            exceptions=article["exceptions"],
        )

        assert statute.statute_number == article["number"]
        assert statute.title == article["title"]

    def test_multiple_statutes_from_real_data(self, civil_law_articles):
        """여러 민법 조문으로 객체 생성"""
        statutes = []
        for article in civil_law_articles[:50]:  # 처음 50개 조문
            statute = CivilLawStatute(
                statute_number=article["number"],
                title=article["title"],
                requirements=article["requirements"],
                effects=article["effects"],
                exceptions=article["exceptions"],
            )
            statutes.append(statute)

        assert len(statutes) == 50
        print(f"✅ {len(statutes)}개의 CivilLawStatute 객체 생성 성공")

    def test_statute_uniqueness(self, civil_law_articles):
        """중복 조문번호 확인 (PDF 파싱 오류 감지)"""
        statute_numbers = []
        duplicates = set()

        for article in civil_law_articles:
            number = article["number"]
            if number in statute_numbers:
                duplicates.add(number)
            statute_numbers.append(number)

        # 중복이 일부 있을 수 있음 (PDF 파싱 오류)
        unique_count = len(set(statute_numbers))
        total_count = len(statute_numbers)

        print(
            f"📊 고유한 조문: {unique_count}개, 전체: {total_count}개, 중복: {len(duplicates)}개"
        )

        # 중복이 과도하지 않아야 함 (10% 이하)
        assert unique_count > total_count * 0.9, f"중복이 과도함: {len(duplicates)}개"

    def test_article_range(self, civil_law_articles):
        """조문 번호 범위 확인 (제7조 ~ 제1010조)"""
        first_article = civil_law_articles[0]
        last_article = civil_law_articles[-1]

        assert "제7조" in first_article["number"]
        assert "제1010조" in last_article["number"]

    def test_statute_with_effects(self, civil_law_articles):
        """효과(effects)가 있는 조문 찾기"""
        statutes_with_effects = []
        for article in civil_law_articles:
            if article["effects"]:
                statute = CivilLawStatute(
                    statute_number=article["number"],
                    title=article["title"],
                    effects=article["effects"],
                )
                statutes_with_effects.append(statute)

        print(f"📊 효과가 있는 조문: {len(statutes_with_effects)}개")
        assert len(statutes_with_effects) > 0

    def test_statute_with_exceptions(self, civil_law_articles):
        """예외(exceptions)가 있는 조문 찾기"""
        statutes_with_exceptions = []
        for article in civil_law_articles:
            if article["exceptions"]:
                statute = CivilLawStatute(
                    statute_number=article["number"],
                    title=article["title"],
                    exceptions=article["exceptions"],
                )
                statutes_with_exceptions.append(statute)

        print(f"📊 예외가 있는 조문: {len(statutes_with_exceptions)}개")
        assert len(statutes_with_exceptions) > 0

    def test_statute_equality_with_same_data(self, civil_law_articles):
        """같은 데이터로 생성한 두 statute는 동일한지 확인"""
        article = civil_law_articles[5]

        statute1 = CivilLawStatute(
            statute_number=article["number"],
            title=article["title"],
            requirements=article["requirements"],
            effects=article["effects"],
            exceptions=article["exceptions"],
        )

        statute2 = CivilLawStatute(
            statute_number=article["number"],
            title=article["title"],
            requirements=article["requirements"],
            effects=article["effects"],
            exceptions=article["exceptions"],
        )

        assert statute1 == statute2

    def test_statute_string_representation(self, civil_law_articles):
        """조문의 문자열 표현 확인"""
        article = civil_law_articles[0]
        statute = CivilLawStatute(
            statute_number=article["number"], title=article["title"]
        )

        assert str(statute) == f"{article['number']} - {article['title']}"

    def test_statute_hash_consistency(self, civil_law_articles):
        """같은 조문의 해시값이 일관성 있는지 확인"""
        article = civil_law_articles[10]

        statute1 = CivilLawStatute(
            statute_number=article["number"], title=article["title"]
        )

        statute2 = CivilLawStatute(
            statute_number=article["number"], title=article["title"]
        )

        assert hash(statute1) == hash(statute2)

    def test_statute_collection_with_set(self, civil_law_articles):
        """조문을 set에 저장할 수 있는지 확인 (해시 가능)"""
        statute_set = set()

        for article in civil_law_articles[:100]:
            statute = CivilLawStatute(
                statute_number=article["number"], title=article["title"]
            )
            statute_set.add(statute)

        # set의 크기는 100이어야 함
        assert len(statute_set) == 100
        print(f"✅ {len(statute_set)}개의 고유한 조문을 set에 저장 성공")

    def test_statute_with_related_precedents(self, civil_law_articles):
        """판례 참조 정보 추가"""
        article = civil_law_articles[0]

        statute = CivilLawStatute(
            statute_number=article["number"],
            title=article["title"],
            related_precedents=["2000가123456", "2001다98765"],
        )

        assert len(statute.related_precedents) == 2
        assert "2000가123456" in statute.related_precedents

    def test_statute_duplicate_removal(self, civil_law_articles):
        """중복된 요소 자동 제거 확인"""
        statute = CivilLawStatute(
            statute_number="제100조",
            title="테스트 조문",
            requirements=["요건1", "요건1", "요건2"],  # 중복
            effects=["효과1", "효과1", "효과1"],  # 중복
        )

        assert len(statute.requirements) == 2
        assert len(statute.effects) == 1
        print("✅ 중복 요소 자동 제거 확인")

    def test_statute_validation_with_real_titles(self, civil_law_articles):
        """실제 민법 제목으로 validation 테스트"""
        # 제목이 매우 긴 조문 찾기
        long_title_articles = [a for a in civil_law_articles if len(a["title"]) > 50]

        for article in long_title_articles[:5]:
            statute = CivilLawStatute(
                statute_number=article["number"], title=article["title"]
            )
            assert len(statute.title) > 50
            print(f"✅ 긴 제목 validation: {len(statute.title)} 자")


class TestPersonWithCivilLawContext:
    """민법 맥락에서 Person 클래스 테스트"""

    def test_create_copyright_holder(self):
        """저작권자 Person 생성"""
        person = Person(
            name="김철학",
            role="저작권자",
            attributes={"good_faith": True, "registered": True},
        )

        assert person.name == "김철학"
        assert person.role == "저작권자"
        assert person.attributes["good_faith"] is True

    def test_create_infringer(self):
        """침해자 Person 생성"""
        person = Person(name="이영수", role="침해자", attributes={"intentional": True})

        assert person.role == "침해자"
        assert person.attributes["intentional"] is True

    def test_create_third_party(self):
        """제3자 Person 생성"""
        person = Person(name="박민준", role="제3자", attributes={})

        assert person.role == "제3자"


class TestTransactionWithCivilLawContext:
    """민법 맥락에서 Transaction 클래스 테스트"""

    def test_copyright_transfer_transaction(self):
        """저작권 양도 거래"""
        seller = Person(name="김철학", role="판매자")
        buyer = Person(name="이영수", role="구매자")

        transaction = Transaction(
            parties=[seller, buyer],
            subject="저작물 - 소설 '달빛'",
            consideration="10,000,000원",
            date="2024-01-15",
        )

        assert len(transaction.parties) == 2
        assert transaction.subject == "저작물 - 소설 '달빛'"
        assert transaction.date == "2024-01-15"

    def test_multi_party_license_transaction(self):
        """다중 당사자 라이센스 거래"""
        licensor = Person(name="박출판사", role="판매자")
        licensee1 = Person(name="온라인서점", role="구매자")
        licensee2 = Person(name="전자책회사", role="구매자")

        transaction = Transaction(
            parties=[licensor, licensee1, licensee2],
            subject="디지털 라이센스",
            consideration="각각 1,000,000원",
            date="2024-06-01",
        )

        assert len(transaction.parties) == 3


class TestLegalRightWithCivilLawContext:
    """민법 맥락에서 LegalRight 클래스 테스트"""

    def test_copyright_right(self):
        """저작권 LegalRight 정의"""
        right = LegalRight(
            name="저작권",
            scope="저작물 (문학, 음악, 영상 등)",
            duration="저작자의 생존 중 + 70년",
            remedies=["침해금지청구", "손해배상청구", "형사처벌"],
        )

        assert right.name == "저작권"
        assert len(right.remedies) == 3

    def test_patent_right(self):
        """특허권 LegalRight 정의"""
        right = LegalRight(
            name="특허권",
            scope="발명",
            duration="등록일로부터 20년",
            remedies=["침해금지청구", "손해배상청구", "재산권"],
        )

        assert right.name == "특허권"
        assert "침해금지청구" in right.remedies

    def test_trademark_right(self):
        """상표권 LegalRight 정의"""
        right = LegalRight(
            name="상표권",
            scope="상표",
            duration="등록일로부터 10년 (갱신 가능)",
            remedies=["침해금지청구", "손해배상청구"],
        )

        assert right.name == "상표권"
        assert "침해금지청구" in right.remedies


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
