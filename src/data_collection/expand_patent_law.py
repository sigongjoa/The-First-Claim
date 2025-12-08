"""
Script to expand patent law articles in the database
Adds additional articles from the ADDITIONAL_PATENT_ARTICLES dictionary
"""

import json
import os
from datetime import date
from typing import List, Dict

from src.knowledge_base.models import LawArticle


def load_current_articles(filepath: str) -> List[dict]:
    """Load current articles from JSON file"""
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_additional_articles() -> List[LawArticle]:
    """Create additional patent law articles"""

    # Comprehensive set of additional articles
    articles_dict = {
        "제31조": ("신규성 상실의 예외", "발명자 또는 출원인이 공개한 경우 1년 이내의 출원은 신규성을 상실하지 않는다."),
        "제33조": ("진보성", "발명이 출원 전에 공개된 특허, 실용신안 또는 간행물에 기재된 발명 또는 널리 알려진 발명에 비하여 진보성이 없는 경우 특허를 받을 수 없다."),
        "제34조": ("발명의 단일성", "한 특허출원에는 발명의 단일성이 있어야 한다."),
        "제37조": ("명세서", "명세서는 그 발명의 목적, 구성 및 효과를 명확하게 기재해야 한다."),
        "제39조": ("거절이유의 통지", "특허청장이 거절이유를 발견하면 출원인에게 이를 통지하여야 한다."),
        "제40조": ("의견서 제출", "출원인은 거절이유 통지를 받은 날부터 3개월 이내에 의견서를 제출할 수 있다."),
        "제41조": ("특허 결정", "출원인이 제시한 의견이 타당한 경우 특허결정을 한다."),
        "제44조": ("특허권의 포기", "특허권자는 특허권을 포기할 수 있다."),
        "제46조": ("특허권의 범위 해석", "특허권의 범위는 명세서에 첨부된 도면을 참조하여 해석한다."),
        "제48조": ("특허료의 납부", "특허권의 존속을 위해서는 특허료를 납부해야 한다."),
        "제49조": ("특허료 납부의 기한", "특허료는 특허등록일부터 계산하여 매년 납부해야 한다."),
        "제50조": ("우선권의 주장", "파리협약의 동맹국에서 특허출원한 자가 1년 이내에 출원하면 우선권을 주장할 수 있다."),
        "제51조": ("국제특허출원", "특허협력조약(PCT)에 따라 국제특허출원을 할 수 있다."),
        "제67조": ("발명의 범위에 대한 이의", "발명의 범위에 대해 이의가 있을 때는 부정정심판을 청구할 수 있다."),
        "제71조": ("무효심판", "특허의 무효에 관해서는 무효심판을 청구할 수 있다."),
        "제72조": ("무효심판의 사유", "신규성 또는 진보성이 없는 경우 무효심판을 청구할 수 있다."),
        "제80조": ("침해죄", "다른 사람의 특허권을 침해한 자는 법정형에 처한다."),
        "제81조": ("침해 행위의 정지와 손해배상", "특허권자는 침해 행위의 정지와 손해배상을 청구할 수 있다."),
        "제82조": ("손해배상의 범위", "침해로 인한 손해배상은 실제 손해액을 기준으로 한다."),
        "제83조": ("침해 제품 등의 개시", "특허권자는 침해 혐의 제품의 개시를 청구할 수 있다."),
        "제84조": ("특허권 침해의 추정", "등록된 청구범위와 동일한 행위는 침해로 추정된다."),
        "제85조": ("손해배상의 증액", "악의적 침해의 경우 손해배상을 3배 이하로 증액할 수 있다."),
        "제86조": ("형사 처벌", "특허권을 침해한 자는 10년 이하의 징역 또는 1억원 이하의 벌금에 처한다."),
        "제87조": ("몰수", "침해에 사용된 물품 및 도구는 몰수할 수 있다."),
        "제88조": ("특허청의 권한", "특허청장은 특허출원 심사 및 등록에 관한 사무를 담당한다."),
        "제99조": ("임시보호권", "공개된 특허출원의 발명은 임시보호권의 대상이 된다."),
        "제100조": ("우선권 없이 출원한 경우", "우선권을 주장하지 않은 출원은 통상적 출원으로 처리된다."),
    }

    articles = []
    for article_number, (title, content) in articles_dict.items():
        article = LawArticle(
            article_number=article_number,
            title=title,
            content=content,
            category="특허법",
            effective_date=date(2024, 1, 1),
        )
        articles.append(article)

    return articles


def expand_patent_law_database(output_path: str = "data/patent_law_articles.json"):
    """
    Expand the patent law database with additional articles

    Args:
        output_path: Path to the output JSON file
    """
    # Load current articles
    current_articles = load_current_articles(output_path)
    existing_numbers = {article['number'] for article in current_articles}

    # Create new articles
    new_articles = create_additional_articles()
    new_articles_dict = [
        article.to_dict() for article in new_articles
        if article.article_number not in existing_numbers
    ]

    # Merge and save
    all_articles = current_articles + new_articles_dict

    # Sort by article number
    all_articles.sort(key=lambda x: (
        int(x['number'].replace('제', '').replace('조', ''))
        if x['number'].replace('제', '').replace('조', '').isdigit()
        else 9999
    ))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print(f"✓ Patent law database expanded")
    print(f"  - Total articles: {len(all_articles)}")
    print(f"  - New articles added: {len(new_articles_dict)}")
    print(f"  - Saved to: {output_path}")

    return len(all_articles)


if __name__ == "__main__":
    expand_patent_law_database()
