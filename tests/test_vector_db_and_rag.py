"""
Vector DB and RAG System Tests

벡터 데이터베이스와 RAG 시스템의 기능을 테스트합니다.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

from src.knowledge_base.vector_database import (
    EmbeddingManager,
    MemoryVectorDatabase,
    VectorDatabaseManager,
    VectorDbType,
    VectorSearchResult,
    get_vector_database,
)
from src.knowledge_base.rag_system import (
    RAGSystem,
    RAGContext,
    RAGResponse,
    get_rag_system,
)
from src.knowledge_base.vector_db_loader import (
    VectorDbLoader,
    initialize_vector_database,
)


# ============================================================================
# Embedding Manager Tests
# ============================================================================


class TestEmbeddingManager:
    """EmbeddingManager 테스트"""

    @patch("requests.post")
    def test_get_embedding_success(self, mock_post):
        """임베딩 생성 성공"""
        # Mock Ollama API response
        mock_response = Mock()
        mock_response.json.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        manager = EmbeddingManager()
        embedding = manager.get_embedding("test text")

        assert embedding == [0.1, 0.2, 0.3]
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_get_embedding_missing_key(self, mock_post):
        """Ollama 연결 불가"""
        from tenacity import RetryError
        # Mock Ollama connection failure
        mock_post.side_effect = ValueError("Ollama 서버에 연결할 수 없습니다")

        manager = EmbeddingManager()
        with pytest.raises((ValueError, RetryError)):
            manager.get_embedding("test text")

    def test_get_embedding_empty_text(self):
        """빈 텍스트"""
        from tenacity import RetryError
        manager = EmbeddingManager()
        with pytest.raises((ValueError, RetryError)):
            manager.get_embedding("")

    @patch("requests.post")
    def test_get_batch_embeddings(self, mock_post):
        """배치 임베딩"""
        # Mock Ollama batch API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "embeddings": [[0.1, 0.2], [0.3, 0.4]]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        manager = EmbeddingManager()
        embeddings = manager.get_batch_embeddings(["text1", "text2"])

        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2]
        assert embeddings[1] == [0.3, 0.4]


# ============================================================================
# Memory Vector Database Tests
# ============================================================================


class TestMemoryVectorDatabase:
    """MemoryVectorDatabase 테스트"""

    @patch.object(EmbeddingManager, "get_embedding")
    def test_add_statute(self, mock_embedding):
        """조문 추가"""
        mock_embedding.return_value = [0.1, 0.2, 0.3]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            db = MemoryVectorDatabase()
            db.add_statute(
                statute_id="civil_197",
                statute_number="제197조",
                title="취득시효",
                content="20년 동안 소유의 의사로 타인의 물건을 점유한 자는...",
                source_type="civil_law",
            )

            assert "civil_197" in db.vectors
            assert len(db.vectors) == 1

    @patch.object(EmbeddingManager, "get_embedding")
    def test_search_cosine_similarity(self, mock_embedding):
        """코사인 유사도 검색"""
        # 다른 벡터들을 반환하도록 side_effect 설정
        mock_embedding.side_effect = [
            [1.0, 0.0, 0.0],  # civil_197 임베딩
            [0.9, 0.1, 0.0],  # civil_198 임베딩
            [1.0, 0.0, 0.0],  # 검색 쿼리 임베딩 (civil_197과 동일)
        ]

        db = MemoryVectorDatabase()

        # 3개 조문 추가
        db.add_statute(
            statute_id="civil_197",
            statute_number="제197조",
            title="취득시효",
            content="취득시효에 관한 조문",
            source_type="civil_law",
        )

        db.add_statute(
            statute_id="civil_198",
            statute_number="제198조",
            title="부동산 취득시효",
            content="부동산 취득시효에 관한 조문",
            source_type="civil_law",
        )

        # 검색 (첫 번째 벡터와 유사)
        results = db.search("취득시효 관련", top_k=1)

        assert len(results) >= 1
        assert results[0].statute_number == "제197조"
        assert results[0].similarity_score > 0.9

    @patch.object(EmbeddingManager, "get_embedding")
    def test_search_with_source_filter(self, mock_embedding):
        """소스 필터링"""
        mock_embedding.return_value = [0.1, 0.2, 0.3]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            db = MemoryVectorDatabase()

            db.add_statute(
                statute_id="civil_197",
                statute_number="제197조",
                title="취득시효",
                content="민법 조문",
                source_type="civil_law",
            )

            db.add_statute(
                statute_id="patent_29",
                statute_number="제29조",
                title="신규성",
                content="특허법 조문",
                source_type="patent_law",
            )

            # 특허법만 검색
            results = db.search("조문", top_k=10, source_type="patent_law")

            assert len(results) == 1
            assert results[0].statute_number == "제29조"

    @patch.object(EmbeddingManager, "get_embedding")
    def test_search_empty_db(self, mock_embedding):
        """빈 DB 검색"""
        mock_embedding.return_value = [0.1, 0.2]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            db = MemoryVectorDatabase()
            results = db.search("쿼리")

            assert results == []

    @patch.object(EmbeddingManager, "get_embedding")
    def test_get_stats(self, mock_embedding):
        """통계 조회"""
        mock_embedding.return_value = [0.1, 0.2, 0.3]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            db = MemoryVectorDatabase()
            db.add_statute(
                statute_id="civil_1",
                statute_number="제1조",
                title="법의 적용",
                content="내용",
                source_type="civil_law",
            )

            stats = db.get_stats()

            assert stats["total_vectors"] == 1
            assert stats["embedding_dimension"] == 3


# ============================================================================
# Vector Database Manager Tests
# ============================================================================


class TestVectorDatabaseManager:
    """VectorDatabaseManager 테스트"""

    @patch.object(EmbeddingManager, "get_embedding")
    def test_init_memory_db(self, mock_embedding):
        """메모리 DB 초기화"""
        mock_embedding.return_value = [0.1]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            manager = VectorDatabaseManager(VectorDbType.MEMORY)

            assert manager.db_type == VectorDbType.MEMORY
            assert isinstance(manager.db, MemoryVectorDatabase)

    def test_init_unsupported_type(self):
        """지원하지 않는 타입"""
        with pytest.raises(ValueError, match="지원하지 않는"):
            # 존재하지 않는 타입으로 초기화 시도
            VectorDatabaseManager(Mock(name="unsupported"))

    def test_init_pinecone(self):
        """Pinecone DB 초기화"""
        import sys
        # Mock the pinecone module since it's not installed
        mock_pinecone = MagicMock()
        with patch.dict(sys.modules, {'pinecone': mock_pinecone}):
            with patch.dict(os.environ, {"PINECONE_API_KEY": "test-key"}):
                manager = VectorDatabaseManager(VectorDbType.PINECONE)
                assert manager.db_type == VectorDbType.PINECONE


# ============================================================================
# RAG System Tests
# ============================================================================


class TestRAGSystem:
    """RAGSystem 테스트"""

    @patch.object(EmbeddingManager, "get_embedding")
    def test_retrieve_context(self, mock_embedding):
        """컨텍스트 검색"""
        mock_embedding.return_value = [0.1, 0.2]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            vector_db = VectorDatabaseManager(VectorDbType.MEMORY)
            vector_db.add_statute(
                statute_id="civil_197",
                statute_number="제197조",
                title="취득시효",
                content="20년 동안 점유하면 소유권 취득",
                source_type="civil_law",
            )

            rag = RAGSystem(vector_db=vector_db)
            context = rag.retrieve_context("취득시효")

            assert isinstance(context, RAGContext)
            assert context.query == "취득시효"
            assert len(context.search_results) > 0

    @patch.object(EmbeddingManager, "get_embedding")
    def test_format_context(self, mock_embedding):
        """컨텍스트 포맷팅"""
        mock_embedding.return_value = [0.1, 0.2]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            vector_db = VectorDatabaseManager(VectorDbType.MEMORY)
            vector_db.add_statute(
                statute_id="civil_197",
                statute_number="제197조",
                title="취득시효",
                content="20년",
                source_type="civil_law",
            )

            rag = RAGSystem(vector_db=vector_db)
            context = rag.retrieve_context("취득시효")

            assert "제197조" in context.formatted_context
            assert "취득시효" in context.formatted_context
            assert "관련 법률 조문" in context.formatted_context

    @patch.object(EmbeddingManager, "get_embedding")
    def test_construct_prompt(self, mock_embedding):
        """프롬프트 구성"""
        mock_embedding.return_value = [0.1, 0.2]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            vector_db = VectorDatabaseManager(VectorDbType.MEMORY)
            vector_db.add_statute(
                statute_id="civil_197",
                statute_number="제197조",
                title="취득시효",
                content="내용",
                source_type="civil_law",
            )

            rag = RAGSystem(vector_db=vector_db)
            context = rag.retrieve_context("테스트")
            prompt = rag._construct_prompt("테스트", context)

            assert "테스트" in prompt
            assert "질문" in prompt
            assert "답변" in prompt

    @patch.object(EmbeddingManager, "get_embedding")
    @patch.object(RAGSystem, "_construct_prompt")
    def test_generate_answer(self, mock_prompt, mock_embedding):
        """답변 생성"""
        mock_embedding.return_value = [0.1]
        mock_prompt.return_value = "test prompt"

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            vector_db = VectorDatabaseManager(VectorDbType.MEMORY)
            vector_db.add_statute(
                statute_id="civil_197",
                statute_number="제197조",
                title="취득시효",
                content="20년",
                source_type="civil_law",
            )

            mock_llm = Mock()
            mock_llm.evaluate_claim.return_value = {"answer": "테스트 답변"}

            rag = RAGSystem(vector_db=vector_db, llm_evaluator=mock_llm)
            context = rag.retrieve_context("테스트")
            response = rag.generate_answer("테스트", context)

            assert isinstance(response, RAGResponse)
            assert "테스트" in response.query or response.answer

    @patch.object(EmbeddingManager, "get_embedding")
    def test_query_integration(self, mock_embedding):
        """통합 쿼리"""
        mock_embedding.return_value = [0.1]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            vector_db = VectorDatabaseManager(VectorDbType.MEMORY)
            vector_db.add_statute(
                statute_id="civil_197",
                statute_number="제197조",
                title="취득시효",
                content="20년 동안 점유하면 소유권 취득",
                source_type="civil_law",
            )

            rag = RAGSystem(vector_db=vector_db)

            # 쿼리 실행
            response = rag.query("취득시효")

            assert isinstance(response, RAGResponse)
            assert "제197조" in response.sources


# ============================================================================
# Vector DB Loader Tests
# ============================================================================


class TestVectorDbLoader:
    """VectorDbLoader 테스트"""

    @patch.object(EmbeddingManager, "get_embedding")
    @patch("builtins.open", create=True)
    @patch("os.path.exists")
    def test_load_civil_law(self, mock_exists, mock_open, mock_embedding):
        """민법 로드"""
        mock_exists.return_value = True
        mock_embedding.return_value = [0.1]

        # Mock JSON 파일
        mock_file_content = json.dumps(
            [{"number": "제197조", "title": "취득시효", "content": "20년 동안..."}]
        )

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch(
                "builtins.open",
                MagicMock(
                    return_value=MagicMock(
                        __enter__=Mock(
                            return_value=MagicMock(
                                read=Mock(return_value=mock_file_content)
                            )
                        ),
                        __exit__=Mock(return_value=None),
                    )
                ),
            ):
                vector_db = VectorDatabaseManager(VectorDbType.MEMORY)
                loader = VectorDbLoader(vector_db)

                # JSON 파싱을 위해 json.load 직접 호출
                with patch("json.load") as mock_load:
                    mock_load.return_value = [
                        {
                            "number": "제197조",
                            "title": "취득시효",
                            "content": "20년 동안...",
                        }
                    ]

                    # loader.load_civil_law() 대신 직접 로드
                    count = loader.load_civil_law()
                    assert count >= 0


# ============================================================================
# Integration Tests
# ============================================================================


class TestVectorDbRAGIntegration:
    """Vector DB와 RAG 시스템 통합 테스트"""

    @patch.object(EmbeddingManager, "get_embedding")
    def test_end_to_end_rag_flow(self, mock_embedding):
        """End-to-End RAG 플로우"""
        # 임베딩은 항상 같은 값으로 설정
        mock_embedding.return_value = [1.0, 0.0, 0.0]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            # 1. Vector DB 생성
            vector_db = VectorDatabaseManager(VectorDbType.MEMORY)

            # 2. 조문 추가
            vector_db.add_statute(
                statute_id="civil_197",
                statute_number="제197조",
                title="취득시효",
                content="20년 동안 소유의 의사로 타인의 부동산을 점유한 자는 그 소유권을 취득한다.",
                source_type="civil_law",
            )

            # 3. RAG 시스템 생성
            rag = RAGSystem(vector_db=vector_db)

            # 4. RAG 쿼리 실행
            response = rag.query("20년 점유로 소유권 취득 가능?")

            # 5. 검증
            assert isinstance(response, RAGResponse)
            assert len(response.sources) > 0
            assert "제197조" in response.sources[0]
            assert response.confidence >= 0.0


# ============================================================================
# Pytest Markers
# ============================================================================

pytestmark = [
    pytest.mark.unit,
    pytest.mark.vector_db,
]


# ============================================================================
# JSON import (필요한 경우)
# ============================================================================

import json
