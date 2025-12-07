"""
Patent Law Database - 특허법 조항 데이터베이스

실제 특허법 조항들을 인스턴스화하여 제공합니다.
검증 엔진과 평가 엔진에서 참조합니다.
"""

from .patent_law import PatentArticle, Invention, PatentClaim


class PatentLawDatabase:
    """특허법 조항을 관리하는 데이터베이스"""

    def __init__(self):
        self.articles = {}
        self._initialize_articles()

    def _initialize_articles(self):
        """특허법 주요 조항 초기화"""

        # 제1조: 목적
        self.articles["제1조"] = PatentArticle(
            article_number="제1조",
            title="목적",
            content="산업상 이용할 수 있는 발명을 보호하고 발명을 장려하여 산업 발전에 기여함을 목적으로 한다.",
            requirements=["산업성"],
            effects=["특허 보호"],
            exceptions=[],
        )

        # 제2조: 발명의 정의
        self.articles["제2조"] = PatentArticle(
            article_number="제2조",
            title="발명의 정의",
            content="이 법에서 발명이라 함은 자연법칙을 이용한 기술적 사상의 창작으로서 고도한 것을 말한다.",
            requirements=["자연법칙 이용", "기술적 사상", "창작성", "고도성"],
            effects=["특허 대상"],
            exceptions=["순수 이론", "비즈니스 방법"],
        )

        # 제3조: 불특허 대상
        self.articles["제3조"] = PatentArticle(
            article_number="제3조",
            title="특허 받을 수 없는 발명",
            content="다음 각 호의 발명은 특허받을 수 없다.",
            requirements=["해당 요건 미충족"],
            effects=["특허 거절"],
            exceptions=[],
        )

        # 제32조: 신규성
        self.articles["제32조"] = PatentArticle(
            article_number="제32조",
            title="신규성",
            content="출원일 전에 국내 또는 국외에서 공개된 발명은 특허받을 수 없다.",
            requirements=["선행 기술과 동일하지 않을 것"],
            effects=["신규성 심사"],
            exceptions=["6개월 이내 재출원"],
        )

        # 제33조: 진보성
        self.articles["제33조"] = PatentArticle(
            article_number="제33조",
            title="진보성",
            content="출원 전에 공개된 발명으로부터 당해 기술 분야의 통상의 지식을 가진 자가 쉽게 생각해낼 수 있는 발명은 특허받을 수 없다.",
            requirements=["진보적 단계", "비자명성"],
            effects=["진보성 심사"],
            exceptions=[],
        )

        # 제34조: 산업상 이용가능성
        self.articles["제34조"] = PatentArticle(
            article_number="제34조",
            title="산업상 이용가능성",
            content="발명은 산업상 이용할 수 있어야 특허받을 수 있다.",
            requirements=["산업상 이용 가능"],
            effects=["산업상 이용가능성 심사"],
            exceptions=[],
        )

        # 제42조: 청구항의 작성
        self.articles["제42조"] = PatentArticle(
            article_number="제42조",
            title="청구항의 작성",
            content="청구항은 명확하고 간결하며 종속항이 있을 때에는 당해 종속항은 종속되는 항의 모든 구성요소를 포함하여야 한다.",
            requirements=["명확성", "간결성", "종속항 규칙"],
            effects=["청구항 적절성 심사"],
            exceptions=[],
        )

        # 제45조: 청구항의 개수
        self.articles["제45조"] = PatentArticle(
            article_number="제45조",
            title="독립항과 종속항",
            content="독립항은 선행항에 의존하지 않고, 종속항은 선행항의 전체 구성요소를 포함하되 제한을 가할 수 있다.",
            requirements=["독립항 독립성", "종속항 의존성"],
            effects=["청구항 구조 심사"],
            exceptions=[],
        )

        # 제47조: 청구항의 명확성
        self.articles["제47조"] = PatentArticle(
            article_number="제47조",
            title="청구항의 명확성",
            content="청구항은 기술분야의 통상의 지식을 가진 자가 이해할 수 있도록 명확하게 작성되어야 한다.",
            requirements=["명확성", "통상 지식"],
            effects=["명확성 심사"],
            exceptions=[],
        )

        # 제49조: 청구항의 범위
        self.articles["제49조"] = PatentArticle(
            article_number="제49조",
            title="청구항의 범위",
            content="청구항의 범위는 명세서에 개시된 발명을 초과할 수 없다.",
            requirements=["명세서 기재 요건"],
            effects=["청구범위 심사"],
            exceptions=[],
        )

        # 제59조: 등록특허의 효력
        self.articles["제59조"] = PatentArticle(
            article_number="제59조",
            title="특허권의 효력",
            content="특허를 받은 자는 해당 발명에 대하여 독점적 권리를 가진다.",
            requirements=["유효한 특허"],
            effects=["특허권 발생"],
            exceptions=["선지권"],
        )

        # 제60조: 침해 행위
        self.articles["제60조"] = PatentArticle(
            article_number="제60조",
            title="침해 행위",
            content="누구든지 특허권자의 동의 없이 특허 발명을 사용할 수 없다.",
            requirements=["무단 사용"],
            effects=["침해 구성"],
            exceptions=["개인 실험", "선지권"],
        )

        # 제62조: 손해배상청구
        self.articles["제62조"] = PatentArticle(
            article_number="제62조",
            title="손해배상청구",
            content="특허권자는 침해자에게 손해배상을 청구할 수 있다.",
            requirements=["침해 행위", "손해 발생"],
            effects=["손해배상청구권"],
            exceptions=["과실 없는 경우"],
        )

        # 제64조: 침해 추정
        self.articles["제64조"] = PatentArticle(
            article_number="제64조",
            title="침해 추정",
            content="특허청구범위에 기재된 구성과 실질적으로 동일한 구성은 침해로 추정된다.",
            requirements=["실질적 동일성"],
            effects=["침해 추정"],
            exceptions=[],
        )

        # 제99조: 재심사 청구
        self.articles["제99조"] = PatentArticle(
            article_number="제99조",
            title="재심사 청구",
            content="특허청은 특허권자의 청구에 따라 거절 이유를 검토하여 재심사할 수 있다.",
            requirements=["재심사 청구권"],
            effects=["재심사 기회"],
            exceptions=[],
        )

        # 제133조: 무효 심판
        self.articles["제133조"] = PatentArticle(
            article_number="제133조",
            title="무효 심판",
            content="누구든지 특허가 특허 받을 수 없는 발명이라고 주장할 수 있다.",
            requirements=["무효 사유"],
            effects=["무효 심판"],
            exceptions=[],
        )

    def get_article(self, article_number):
        """조항 번호로 특허법 조항 조회"""
        return self.articles.get(article_number)

    def get_all_articles(self):
        """모든 조항 반환"""
        return list(self.articles.values())

    def search_by_title(self, keyword):
        """제목으로 조항 검색"""
        return [a for a in self.articles.values() if keyword in a.title]

    def search_by_requirement(self, keyword):
        """요건으로 조항 검색"""
        results = []
        for article in self.articles.values():
            if any(keyword in req for req in article.requirements):
                results.append(article)
        return results

    def search_by_effect(self, keyword):
        """효과로 조항 검색"""
        results = []
        for article in self.articles.values():
            if any(keyword in eff for eff in article.effects):
                results.append(article)
        return results

    def get_statistics(self):
        """데이터베이스 통계"""
        return {
            "total_articles": len(self.articles),
            "article_numbers": list(self.articles.keys()),
        }


# 전역 인스턴스
patent_law_db = PatentLawDatabase()


def get_patent_law_database():
    """특허법 데이터베이스 인스턴스 반환"""
    return patent_law_db
