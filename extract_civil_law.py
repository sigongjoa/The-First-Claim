#!/usr/bin/env python3
"""
민법 추출 스크립트

한글 4법전 PDF에서 민법 부분만 추출하여 구조화된 데이터로 변환합니다.
"""

import pdfplumber
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CivilLawArticle:
    """민법 조문 데이터 클래스"""

    number: str  # 제145조
    title: str
    content: str
    requirements: List[str]
    effects: List[str]
    exceptions: List[str]


def extract_civil_law_from_pdf(pdf_path: str) -> str:
    """
    PDF에서 민법 섹션만 추출합니다.

    Args:
        pdf_path: PDF 파일 경로

    Returns:
        민법 전체 텍스트
    """
    print(f"📖 PDF 파일 열기: {pdf_path}")

    civil_law_text = ""
    start_extracting = False
    found_civil_law_header = False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"📄 총 페이지 수: {total_pages}")

            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()

                if text is None:
                    continue

                # 민법 섹션 헤더 찾기 ("민법" 단독 또는 "민법" 제목)
                if not start_extracting:
                    # "민법" 텍스트를 찾되, 형법이나 헌법, 형사소송법과 함께 나타나지 않아야 함
                    if (
                        "민법" in text
                        and "헌법" not in text[:100]
                        and "형법" not in text[:100]
                        and "제1조" in text
                    ):  # 첫 조문이 있는지 확인
                        print(f"✅ 민법 섹션 시작: {page_num}페이지")
                        start_extracting = True
                        found_civil_law_header = True

                # 민법 섹션 추출
                if start_extracting:
                    # 형법이 시작되면 중단 (민법 이후가 형법)
                    if "형법" in text and "제1조" in text and civil_law_text:
                        print(f"🛑 민법 섹션 종료: {page_num}페이지 (형법 시작)")
                        break

                    civil_law_text += text + "\n"

                if page_num % 100 == 0:
                    print(f"  진행 중: {page_num}/{total_pages} 페이지...")

            if civil_law_text:
                print(f"📊 추출된 민법 텍스트 길이: {len(civil_law_text):,} 자")
            else:
                print("⚠️  민법 텍스트를 찾을 수 없습니다")

    except Exception as e:
        print(f"❌ PDF 처리 오류: {e}")
        raise

    return civil_law_text


def parse_civil_law_articles(text: str) -> List[Dict]:
    """
    민법 텍스트를 조문별로 파싱합니다.

    Args:
        text: 민법 전체 텍스트

    Returns:
        조문별 데이터 리스트
    """
    print("\n🔍 민법 조문 파싱 시작...")

    articles = []

    # 조문 패턴: 제XXX조 또는 제XXX조의X
    # 예: 제145조, 제371조의2
    article_pattern = (
        r"제\s*(\d+)\s*조(?:의\s*(\d+))?\s*([^\n]*)\n((?:(?!^제).)*?)(?=^제|\Z)"
    )

    matches = re.finditer(article_pattern, text, re.MULTILINE | re.DOTALL)

    for match in matches:
        article_num = match.group(1)
        sub_num = match.group(2)
        title = match.group(3).strip()
        content = match.group(4).strip()

        # 조문번호 생성
        if sub_num:
            full_number = f"제{article_num}조의{sub_num}"
        else:
            full_number = f"제{article_num}조"

        if content:  # 내용이 있을 때만 추가
            article_data = {
                "number": full_number,
                "title": title,
                "content": content[:500],  # 처음 500자만
                "requirements": [],
                "effects": [],
                "exceptions": [],
            }
            articles.append(article_data)

    print(f"✅ 총 {len(articles)}개의 조문 파싱 완료")

    return articles


def extract_law_components(article: Dict) -> Dict:
    """
    조문에서 요건, 효과, 예외를 추출합니다.

    Args:
        article: 조문 데이터

    Returns:
        요건/효과/예외가 추가된 조문 데이터
    """
    content = article.get("content", "")

    # 간단한 패턴 기반 추출 (휴리스틱)
    if "하면" in content or "하는 경우" in content:
        article["requirements"].append("특정 조건 충족")

    if "할 수 있다" in content or "권리" in content:
        article["effects"].append("권리 발생")

    if "단, " in content or "다만, " in content or "제외" in content:
        article["exceptions"].append("예외 존재")

    return article


def save_to_json(articles: List[Dict], output_path: str) -> None:
    """
    추출한 조문을 JSON으로 저장합니다.

    Args:
        articles: 조문 리스트
        output_path: 저장 경로
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"💾 JSON 저장 완료: {output_path}")


def main():
    """메인 실행 함수"""
    pdf_path = "/mnt/d/progress/The-First-Claim/assets/한글 4법전(헌법, 민법, 형법, 형사소송법).pdf"
    output_json = "/mnt/d/progress/The-First-Claim/data/civil_law_articles.json"

    # 1. PDF에서 민법 추출
    print("=" * 60)
    print("📚 한글 4법전에서 민법 추출")
    print("=" * 60)

    civil_law_text = extract_civil_law_from_pdf(pdf_path)

    # 2. 조문 파싱
    articles = parse_civil_law_articles(civil_law_text)

    # 3. 요건/효과/예외 추출
    print("\n📋 조문별 요건/효과/예외 추출 중...")
    articles = [extract_law_components(article) for article in articles]

    # 4. JSON으로 저장
    print()
    save_to_json(articles, output_json)

    # 5. 샘플 출력
    print("\n" + "=" * 60)
    print("📖 추출된 조문 샘플 (처음 3개)")
    print("=" * 60)
    for article in articles[:3]:
        print(f"\n{article['number']} - {article['title']}")
        print(f"  내용: {article['content'][:100]}...")
        print(f"  요건: {article['requirements']}")
        print(f"  효과: {article['effects']}")
        print(f"  예외: {article['exceptions']}")


if __name__ == "__main__":
    main()
