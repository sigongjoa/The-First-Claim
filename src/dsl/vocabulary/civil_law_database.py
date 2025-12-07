"""
Civil Law Database - 민법 조항 데이터베이스

실제 민법 조항들을 인스턴스화하여 제공합니다.
검증 엔진과 평가 엔진에서 참조합니다.
"""

from .civil_law import CivilLawStatute, Person, Transaction, LegalRight
from datetime import datetime


class CivilLawDatabase:
    """민법 조항을 관리하는 데이터베이스"""

    def __init__(self):
        self.statutes = {}
        self._initialize_statutes()

    def _initialize_statutes(self):
        """민법 주요 조항 초기화"""

        # 제1조: 법 적용의 범위
        self.statutes["제1조"] = CivilLawStatute(
            statute_number="제1조",
            title="법 적용의 범위",
            requirements=["대한민국 영역 내에서의 법률 관계"],
            effects=["민법 적용"],
            exceptions=["특별법 있는 경우"],
            related_precedents=["대법원 1984-02-14"],
        )

        # 제2조: 사람
        self.statutes["제2조"] = CivilLawStatute(
            statute_number="제2조",
            title="사람",
            requirements=["출생"],
            effects=["권리능력 발생"],
            exceptions=["사망시 소멸"],
            related_precedents=[],
        )

        # 제3조: 성년
        self.statutes["제3조"] = CivilLawStatute(
            statute_number="제3조",
            title="성년",
            requirements=["19세 도달"],
            effects=["행위능력 취득"],
            exceptions=["법원의 제한"],
            related_precedents=[],
        )

        # 제10조: 의사능력
        self.statutes["제10조"] = CivilLawStatute(
            statute_number="제10조",
            title="의사능력",
            requirements=["자신의 행위의 의미와 결과를 이해할 능력"],
            effects=["법률행위 유효"],
            exceptions=["의사능력 없는 경우 무효"],
            related_precedents=["대법원 2006-10-26"],
        )

        # 제109조: 권리와 의무
        self.statutes["제109조"] = CivilLawStatute(
            statute_number="제109조",
            title="권리와 의무",
            requirements=["법적 주체의 지위"],
            effects=["민사상 권리 의무 귀속"],
            exceptions=["공익상 금지 행위"],
            related_precedents=[],
        )

        # 제145조: 저작권의 성립
        self.statutes["제145조"] = CivilLawStatute(
            statute_number="제145조",
            title="저작권의 성립",
            requirements=["창작", "독창성", "표현의 고정"],
            effects=["저작권 발생"],
            exceptions=["사전에 등록 불필요"],
            related_precedents=["대법원 2005-04-28"],
        )

        # 제188조: 점유의 개념
        self.statutes["제188조"] = CivilLawStatute(
            statute_number="제188조",
            title="점유의 개념",
            requirements=["물건에 대한 사실상의 지배"],
            effects=["점유권 발생"],
            exceptions=["타인 물건에 대한 경우"],
            related_precedents=[],
        )

        # 제213조: 소유권의 일반적 효력
        self.statutes["제213조"] = CivilLawStatute(
            statute_number="제213조",
            title="소유권의 일반적 효력",
            requirements=["소유권 보유"],
            effects=["사용, 수익, 처분권"],
            exceptions=["법령 또는 계약의 제한"],
            related_precedents=[],
        )

        # 제366조: 계약의 개념
        self.statutes["제366조"] = CivilLawStatute(
            statute_number="제366조",
            title="계약의 개념",
            requirements=["당사자의 의사일치"],
            effects=["법적 구속력 발생"],
            exceptions=["법정 형식 미충족시 무효"],
            related_precedents=["대법원 1994-03-22"],
        )

        # 제383조: 매매계약의 성립
        self.statutes["제383조"] = CivilLawStatute(
            statute_number="제383조",
            title="매매계약의 성립",
            requirements=["당사자간 가격의 합의"],
            effects=["계약 성립"],
            exceptions=["서면 요건"],
            related_precedents=[],
        )

        # 제570조: 권리의 보증
        self.statutes["제570조"] = CivilLawStatute(
            statute_number="제570조",
            title="권리의 보증",
            requirements=["판매인이 물건에 대한 권리 보유"],
            effects=["구매인에게 권리 이전"],
            exceptions=["권리 하자 있는 경우 손해배상"],
            related_precedents=[],
        )

        # 제665조: 위임의 성립
        self.statutes["제665조"] = CivilLawStatute(
            statute_number="제665조",
            title="위임의 성립",
            requirements=["당사자의 합의"],
            effects=["위임 관계 성립"],
            exceptions=["서면 요건 없음"],
            related_precedents=[],
        )

        # 제750조: 불법행위
        self.statutes["제750조"] = CivilLawStatute(
            statute_number="제750조",
            title="불법행위",
            requirements=[
                "고의 또는 과실",
                "타인의 권리 침해",
                "손해 발생",
                "인과관계",
            ],
            effects=["손해배상 책임"],
            exceptions=["정당행위", "자위행위"],
            related_precedents=["대법원 2000-06-23"],
        )

        # 제761조: 과실의 입증책임
        self.statutes["제761조"] = CivilLawStatute(
            statute_number="제761조",
            title="과실의 입증책임",
            requirements=["피해자가 손해 및 인과관계 입증"],
            effects=["가해자의 과실 추정"],
            exceptions=["특수 경우의 입증 책임 전환"],
            related_precedents=[],
        )

        # 제766조: 손해배상의 범위
        self.statutes["제766조"] = CivilLawStatute(
            statute_number="제766조",
            title="손해배상의 범위",
            requirements=["인과관계"],
            effects=["적극적 손해와 소극적 손해 배상"],
            exceptions=["예측 불가능한 손해"],
            related_precedents=["대법원 2005-07-22"],
        )

        # 제771조: 채무불이행시 손해배상
        self.statutes["제771조"] = CivilLawStatute(
            statute_number="제771조",
            title="채무불이행시 손해배상",
            requirements=["채무 불이행"],
            effects=["손해배상 청구권 발생"],
            exceptions=["불가항력"],
            related_precedents=[],
        )

        # 제955조: 보증채무의 성립
        self.statutes["제955조"] = CivilLawStatute(
            statute_number="제955조",
            title="보증채무의 성립",
            requirements=["주채무의 존재", "보증인의 동의"],
            effects=["보증채무 성립"],
            exceptions=["서면 요건"],
            related_precedents=[],
        )

        # 저작권법 제37조
        self.statutes["저작권법 제37조"] = CivilLawStatute(
            statute_number="저작권법 제37조",
            title="복제권",
            requirements=["저작권 보유"],
            effects=["복제 허가권", "복제권 침해시 배상청구"],
            exceptions=["공정이용"],
            related_precedents=["대법원 2008-09-18"],
        )

        # 저작권법 제50조
        self.statutes["저작권법 제50조"] = CivilLawStatute(
            statute_number="저작권법 제50조",
            title="공정이용",
            requirements=["비영리 목적", "보도", "비평", "교육", "연구"],
            effects=["저작권 침해 성립 안 함"],
            exceptions=["상당히 큰 부분 복제"],
            related_precedents=["대법원 2014-10-23"],
        )

    def get_statute(self, statute_number):
        """조문 번호로 조항 조회"""
        return self.statutes.get(statute_number)

    def get_all_statutes(self):
        """모든 조항 반환"""
        return list(self.statutes.values())

    def search_by_title(self, keyword):
        """제목으로 조항 검색"""
        return [s for s in self.statutes.values() if keyword in s.title]

    def search_by_requirement(self, keyword):
        """요건으로 조항 검색"""
        results = []
        for statute in self.statutes.values():
            if any(keyword in req for req in statute.requirements):
                results.append(statute)
        return results

    def search_by_effect(self, keyword):
        """효과로 조항 검색"""
        results = []
        for statute in self.statutes.values():
            if any(keyword in eff for eff in statute.effects):
                results.append(statute)
        return results

    def get_statistics(self):
        """데이터베이스 통계"""
        return {
            "total_statutes": len(self.statutes),
            "statute_numbers": list(self.statutes.keys()),
        }


# 전역 인스턴스
civil_law_db = CivilLawDatabase()


def get_civil_law_database():
    """민법 데이터베이스 인스턴스 반환"""
    return civil_law_db
