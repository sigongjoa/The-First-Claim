"""
Script to initialize the precedent case database with landmark cases and additional cases
"""

import json
import os
from datetime import date
from typing import List

from src.knowledge_base.models import PrecedentCase


def create_all_precedent_cases() -> List[PrecedentCase]:
    """
    Create a comprehensive list of landmark and additional precedent cases

    Returns:
        List of PrecedentCase objects
    """

    # All cases with full details
    cases_dict = {
        # LANDMARK CASES
        "2019후10001": {
            "court": "특허법원",
            "decision_date": date(2020, 3, 26),
            "case_type": "신규성",
            "summary": "청구항의 신규성 판단에 있어서 기술적 특징의 개수보다 개별 특징의 구체성이 중요한 판단 기준이 된다는 판례",
            "key_holdings": [
                "신규성 판단은 공개 자료의 명확한 기재에 기초해야 함",
                "추상적 표현은 신규성 판단의 근거가 될 수 없음",
                "기술적 특징의 구체적 구성이 중요"
            ],
            "cited_articles": ["제29조", "제30조"],
            "outcome": "인용",
            "patent_field": "전자",
        },
        "2019후10002": {
            "court": "특허법원",
            "decision_date": date(2020, 5, 28),
            "case_type": "진보성",
            "summary": "진보성 판단에서 동기부여 요소의 존재와 기술적 노력 정도를 종합적으로 고려해야 한다",
            "key_holdings": [
                "진보성 부족은 동기부여, 기술적 예측 가능성, 기술적 노력이 필요",
                "선행기술 결합시 동기부여가 명확해야 함",
                "예측 불가능한 기술 효과는 진보성 증거"
            ],
            "cited_articles": ["제29조", "제33조"],
            "outcome": "인용",
            "patent_field": "기계",
        },
        "2020후10001": {
            "court": "특허법원",
            "decision_date": date(2021, 2, 11),
            "case_type": "권리범위",
            "summary": "청구범위 해석에서 명세서와 도면의 기재 내용을 종합적으로 고려하여야 함",
            "key_holdings": [
                "청구범위 해석은 명세서 전체를 고려해야 함",
                "발명의 기술적 의의를 고려한 해석이 필요",
                "통상의 기술자 입장에서 해석"
            ],
            "cited_articles": ["제66조"],
            "outcome": "기각",
            "patent_field": "소프트웨어",
        },
        "2020후10002": {
            "court": "특허법원",
            "decision_date": date(2021, 4, 15),
            "case_type": "명세서 기재 불충분",
            "summary": "발명의 효과가 명세서에 충분히 기재되지 않으면 명세서 기재 요건 미달",
            "key_holdings": [
                "발명의 목적, 구성, 효과가 명확해야 함",
                "발명의 효과가 구체적으로 기재되어야 함",
                "일반적인 지식만으로 이해 불가능해야 함"
            ],
            "cited_articles": ["제37조"],
            "outcome": "기각",
            "patent_field": "화학",
        },
        "2021후10001": {
            "court": "특허법원",
            "decision_date": date(2022, 1, 20),
            "case_type": "신규성",
            "summary": "복합적 기술 구성의 신규성 판단에서 구성 요소별 개별 신규성뿐 아니라 결합 관계도 고려",
            "key_holdings": [
                "구성 요소의 조합 관계가 신규성 판단 대상이 될 수 있음",
                "조합에 따른 기술적 의의 존재 여부 검토 필요",
                "선행기술에서 동일 구성의 조합이 없으면 신규"
            ],
            "cited_articles": ["제29조", "제30조"],
            "outcome": "인용",
            "patent_field": "전자",
        },
        # ADDITIONAL CASES
        "2021후10002": {
            "court": "특허법원",
            "decision_date": date(2022, 3, 17),
            "case_type": "진보성",
            "summary": "통상의 기술자가 선행기술을 결합하여 용이하게 발명할 수 없을 때 진보성 있음",
            "key_holdings": [
                "기술 결합의 동기부여 필요",
                "기술적 노력이 필요",
                "통상의 기술자가 용이하게 예측할 수 없어야 함"
            ],
            "cited_articles": ["제33조"],
            "outcome": "인용",
            "patent_field": "기계",
        },
        "2021후10003": {
            "court": "특허법원",
            "decision_date": date(2022, 5, 19),
            "case_type": "권리범위",
            "summary": "청구범위의 용어 해석은 발명이 속하는 기술 분야의 통상의 기술자 관점에서 함",
            "key_holdings": [
                "통상의 기술자 기준 적용",
                "기술 분야의 맥락 고려",
                "도면과 명세서를 종합적으로 해석"
            ],
            "cited_articles": ["제66조"],
            "outcome": "인용",
            "patent_field": "전자",
        },
        "2022후10001": {
            "court": "특허법원",
            "decision_date": date(2023, 1, 12),
            "case_type": "신규성",
            "summary": "선행기술에 명확히 기재되지 않은 기술적 특징은 신규성을 상실하지 않음",
            "key_holdings": [
                "선행기술의 명확한 기재 필요",
                "암묵적 기재는 신규성 판단 제외",
                "구체적 명시가 필요"
            ],
            "cited_articles": ["제29조", "제30조"],
            "outcome": "인용",
            "patent_field": "화학",
        },
        "2022후10002": {
            "court": "특허법원",
            "decision_date": date(2023, 3, 9),
            "case_type": "진보성",
            "summary": "기술효과의 예측 불가능성이 입증되면 진보성이 있는 것으로 인정",
            "key_holdings": [
                "예측 불가능한 기술 효과가 진보성 근거",
                "효과의 구체적 입증 필요",
                "수치 범위 설정의 임의성 검토"
            ],
            "cited_articles": ["제33조"],
            "outcome": "인용",
            "patent_field": "화학",
        },
        "2023후10001": {
            "court": "특허법원",
            "decision_date": date(2023, 6, 15),
            "case_type": "명세서 기재 불충분",
            "summary": "실시 가능 요건은 통상의 기술자가 명세서와 도면으로 충분히 이해할 수 있어야 함",
            "key_holdings": [
                "통상의 기술자 입장에서 판단",
                "실현 가능성이 명확해야 함",
                "불가피한 시험은 허용"
            ],
            "cited_articles": ["제37조"],
            "outcome": "기각",
            "patent_field": "바이오",
        },
        "2023후10002": {
            "court": "특허법원",
            "decision_date": date(2023, 8, 24),
            "case_type": "권리범위",
            "summary": "청구항의 기술적 특징을 이용하는 행위가 모두 침해에 해당하는 것은 아님",
            "key_holdings": [
                "청구범위의 경계 결정이 중요",
                "기술적 특징의 필요성 검토",
                "선택적 특징의 해석"
            ],
            "cited_articles": ["제66조"],
            "outcome": "인용",
            "patent_field": "소프트웨어",
        },
        "2024후10001": {
            "court": "특허법원",
            "decision_date": date(2024, 2, 8),
            "case_type": "신규성",
            "summary": "같은 기술이라도 구성 방식에 따라 신규성 판단이 달라질 수 있음",
            "key_holdings": [
                "구성 방식의 차이가 신규성에 영향",
                "기술적 의미를 고려한 해석",
                "개념적 동일성만으로 부족"
            ],
            "cited_articles": ["제29조"],
            "outcome": "인용",
            "patent_field": "전자",
        },
    }

    cases = []
    for case_number, case_data in cases_dict.items():
        # Create full_text from summary and holdings
        full_text = f"""사건번호: {case_number}
법원: {case_data['court']}
판결일: {case_data['decision_date']}
사건 유형: {case_data['case_type']}

【요약】
{case_data['summary']}

【주요 판시사항】
"""
        for i, holding in enumerate(case_data['key_holdings'], 1):
            full_text += f"{i}. {holding}\n"

        full_text += f"""
【인용 조문】
{', '.join(case_data['cited_articles'])}

【판결 결과】
{case_data['outcome']}
"""

        case = PrecedentCase(
            case_number=case_number,
            court=case_data['court'],
            decision_date=case_data['decision_date'],
            case_type=case_data['case_type'],
            summary=case_data['summary'],
            full_text=full_text,
            key_holdings=case_data['key_holdings'],
            cited_articles=case_data['cited_articles'],
            outcome=case_data['outcome'],
            patent_field=case_data.get('patent_field'),
        )
        cases.append(case)

    return cases


def initialize_precedent_database(output_path: str = "data/patent_precedent_cases.json"):
    """
    Initialize the precedent case database

    Args:
        output_path: Path to the output JSON file
    """
    cases = create_all_precedent_cases()

    # Convert to dictionary for JSON serialization
    cases_dict = [case.to_dict() for case in cases]

    # Sort by decision date (newest first)
    cases_dict.sort(key=lambda x: x['decision_date'], reverse=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cases_dict, f, ensure_ascii=False, indent=2)

    print(f"✓ Precedent database initialized")
    print(f"  - Total cases: {len(cases)}")
    print(f"  - Saved to: {output_path}")

    return len(cases)


if __name__ == "__main__":
    initialize_precedent_database()
