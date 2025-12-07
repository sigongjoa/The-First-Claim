"""
Vector Database Loader - 법률 조문을 벡터 DB에 로드

민법, 특허법 조문을 JSON에서 읽어서 벡터 DB에 추가합니다.
"""

from __future__ import annotations

import json
import os
from typing import List, Dict, Optional
import logging

from .vector_database import VectorDatabaseManager, VectorDbType

logger = logging.getLogger(__name__)


class VectorDbLoader:
    """벡터 DB 로더"""

    def __init__(self, vector_db: VectorDatabaseManager):
        """
        로더 초기화

        Args:
            vector_db: 벡터 데이터베이스 매니저
        """
        self.vector_db = vector_db
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
        )

    def load_civil_law(self) -> int:
        """
        민법 조문 로드

        Returns:
            로드된 조문 개수
        """
        logger.info("민법 조문 로드 시작...")

        civil_law_file = os.path.join(self.data_dir, "civil_law_articles.json")

        if not os.path.exists(civil_law_file):
            logger.warning(f"파일을 찾을 수 없습니다: {civil_law_file}")
            return 0

        try:
            with open(civil_law_file, "r", encoding="utf-8") as f:
                articles = json.load(f)

            count = 0
            for article in articles:
                try:
                    statute_id = f"civil_{article.get('number', '').replace('제', '').replace('조', '')}"
                    statute_number = article.get("number", "")
                    title = article.get("title", "")
                    content = article.get("content", "")

                    if not statute_number or not content:
                        logger.warning(f"불완전한 조문: {statute_number}")
                        continue

                    self.vector_db.add_statute(
                        statute_id=statute_id,
                        statute_number=statute_number,
                        title=title,
                        content=content,
                        source_type="civil_law",
                        metadata={"article_count": len(articles), "type": "statute"},
                    )
                    count += 1

                except Exception as e:
                    logger.error(f"조문 추가 실패: {e}")
                    continue

            logger.info(f"민법 로드 완료: {count}개 조문")
            return count

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return 0
        except Exception as e:
            logger.error(f"민법 로드 실패: {e}")
            return 0

    def load_patent_law(self) -> int:
        """
        특허법 조문 로드

        Returns:
            로드된 조문 개수
        """
        logger.info("특허법 조문 로드 시작...")

        patent_law_file = os.path.join(self.data_dir, "patent_law_articles.json")

        if not os.path.exists(patent_law_file):
            logger.warning(f"파일을 찾을 수 없습니다: {patent_law_file}")
            return 0

        try:
            with open(patent_law_file, "r", encoding="utf-8") as f:
                articles = json.load(f)

            count = 0
            for article in articles:
                try:
                    statute_id = f"patent_{article.get('number', '').replace('제', '').replace('조', '')}"
                    statute_number = article.get("number", "")
                    title = article.get("title", "")
                    content = article.get("content", "")

                    if not statute_number or not content:
                        logger.warning(f"불완전한 조문: {statute_number}")
                        continue

                    self.vector_db.add_statute(
                        statute_id=statute_id,
                        statute_number=statute_number,
                        title=title,
                        content=content,
                        source_type="patent_law",
                        metadata={"article_count": len(articles), "type": "statute"},
                    )
                    count += 1

                except Exception as e:
                    logger.error(f"조문 추가 실패: {e}")
                    continue

            logger.info(f"특허법 로드 완료: {count}개 조문")
            return count

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return 0
        except Exception as e:
            logger.error(f"특허법 로드 실패: {e}")
            return 0

    def load_all(self) -> Dict[str, int]:
        """
        모든 법률 조문 로드

        Returns:
            로드 결과 딕셔너리
        """
        logger.info("=" * 50)
        logger.info("벡터 DB 로드 시작")
        logger.info("=" * 50)

        civil_count = self.load_civil_law()
        patent_count = self.load_patent_law()
        total_count = civil_count + patent_count

        result = {
            "civil_law": civil_count,
            "patent_law": patent_count,
            "total": total_count,
        }

        logger.info("=" * 50)
        logger.info(f"벡터 DB 로드 완료")
        logger.info(f"  민법: {civil_count}개")
        logger.info(f"  특허법: {patent_count}개")
        logger.info(f"  합계: {total_count}개")
        logger.info("=" * 50)

        return result

    def verify_load(self) -> bool:
        """
        로드 확인 (테스트 검색)

        Returns:
            로드 성공 여부
        """
        try:
            logger.info("벡터 DB 로드 확인 중...")

            # 테스트 검색 1: 민법
            results_civil = self.vector_db.search(
                "취득시효", top_k=3, source_type="civil_law"
            )

            # 테스트 검색 2: 특허법
            results_patent = self.vector_db.search(
                "신규성", top_k=3, source_type="patent_law"
            )

            success = bool(results_civil or results_patent)

            if success:
                logger.info(f"✅ 벡터 DB 로드 확인 성공")
                logger.info(f"  민법 검색 결과: {len(results_civil)}개")
                logger.info(f"  특허법 검색 결과: {len(results_patent)}개")
            else:
                logger.error("❌ 벡터 DB에 데이터가 없습니다")

            return success

        except Exception as e:
            logger.error(f"❌ 로드 확인 실패: {e}")
            return False


def initialize_vector_database(
    db_type: VectorDbType = VectorDbType.MEMORY, auto_load: bool = True
) -> VectorDatabaseManager:
    """
    벡터 데이터베이스 초기화 및 로드

    Args:
        db_type: 벡터 DB 타입
        auto_load: 자동 로드 여부

    Returns:
        초기화된 VectorDatabaseManager
    """
    from .vector_database import VectorDatabaseManager

    logger.info(f"벡터 데이터베이스 초기화 중... (타입={db_type.value})")

    vector_db = VectorDatabaseManager(db_type)

    if auto_load:
        loader = VectorDbLoader(vector_db)
        loader.load_all()
        loader.verify_load()

    return vector_db
