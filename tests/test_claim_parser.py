"""
Tests for claim component parser
"""

import pytest
from src.dsl.logic.claim_parser import (
    ClaimComponentParser,
    SynonymDictionary,
    ParsedClaim,
    create_claim_parser
)


class TestSynonymDictionary:
    """Test synonym dictionary functionality"""

    def test_get_canonical_form(self):
        """Test getting canonical forms of terms"""
        syn_dict = SynonymDictionary()

        # Test display-related synonyms
        assert syn_dict.get_canonical_form("디스플레이") == "표시_장치"
        assert syn_dict.get_canonical_form("화면") == "표시_장치"
        assert syn_dict.get_canonical_form("lcd") == "표시_장치"

        # Test storage-related synonyms
        assert syn_dict.get_canonical_form("메모리") == "저장_장치"
        assert syn_dict.get_canonical_form("저장부") == "저장_장치"

    def test_are_synonyms(self):
        """Test synonym matching"""
        syn_dict = SynonymDictionary()

        assert syn_dict.are_synonyms("디스플레이", "화면")
        assert syn_dict.are_synonyms("메모리", "저장부")
        assert not syn_dict.are_synonyms("디스플레이", "메모리")

    def test_unknown_term(self):
        """Test handling of unknown terms"""
        syn_dict = SynonymDictionary()

        # Unknown term should return itself
        assert syn_dict.get_canonical_form("미지의용어") == "미지의용어"


class TestClaimComponentParser:
    """Test claim parsing functionality"""

    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return create_claim_parser()

    def test_parse_simple_claim(self, parser):
        """Test parsing a simple claim"""
        claim_text = "청구항 1. 디스플레이를 포함하는 휴대용 전자 기기"

        result = parser.parse_claim(claim_text)

        assert isinstance(result, ParsedClaim)
        assert result.original_text == claim_text
        assert len(result.components) == 3

    def test_extract_preamble(self, parser):
        """Test preamble extraction"""
        claim_text = "청구항 1. 표시 장치를 포함하는 기기에 있어서, 다음과 같이 구성된다"

        result = parser.parse_claim(claim_text)

        # Should identify first part as preamble
        assert "청구항" in result.preamble or "표시" in result.preamble

    def test_extract_technical_features(self, parser):
        """Test technical feature extraction"""
        claim_text = "청구항 1. 메모리 장치, 프로세서 장치, 통신 부"

        result = parser.parse_claim(claim_text)

        # Should extract device/part related features
        assert len(result.all_features) > 0

    def test_synonym_normalization(self, parser):
        """Test that synonyms are normalized"""
        claim_text1 = "청구항 1. 디스플레이를 포함하는 기기"
        claim_text2 = "청구항 2. 화면을 포함하는 기기"

        result1 = parser.parse_claim(claim_text1)
        result2 = parser.parse_claim(claim_text2)

        # Both should normalize to same canonical forms
        # At least should have overlap in normalized features
        assert len(result1.normalized_features & result2.normalized_features) > 0

    def test_calculate_claim_similarity(self, parser):
        """Test similarity calculation between claims"""
        claim1 = parser.parse_claim("청구항 1. 프로세서와 메모리를 포함하는 장치")
        claim2 = parser.parse_claim("청구항 2. 프로세서와 메모리를 포함하는 장치")  # Identical
        claim3 = parser.parse_claim("청구항 3. 센서를 포함하는 장치")  # Different

        # Identical claims should have high similarity
        similarity_same = parser.calculate_claim_similarity(claim1, claim2)
        assert similarity_same > 0.5  # Should be quite similar

        # Different claims should have lower similarity
        similarity_diff = parser.calculate_claim_similarity(claim1, claim3)
        assert similarity_diff < similarity_same

    def test_feature_vector_creation(self, parser):
        """Test feature vector creation"""
        claim = parser.parse_claim("청구항 1. 메모리, 센서, 프로세서를 포함하는 장치")

        feature_vector = parser.get_feature_vector(claim)

        assert isinstance(feature_vector, dict)
        assert len(feature_vector) > 0

    def test_empty_claim(self, parser):
        """Test handling of empty claim"""
        result = parser.parse_claim("")

        assert isinstance(result, ParsedClaim)
        assert result.original_text == ""

    def test_complex_claim(self, parser):
        """Test parsing a more complex claim"""
        claim_text = """청구항 1.
        표시 장치와 저장 부를 포함하는 전자 기기에 있어서,
        상기 표시 장치는 LCD 또는 LED 화면이고,
        상기 저장 부는 메모리 또는 SSD로 구성되며,
        상기 전자 기기는 무선 통신 기능을 포함하는
        휴대용 컴퓨팅 장치."""

        result = parser.parse_claim(claim_text)

        assert len(result.components) == 3
        # Should extract multiple features
        assert len(result.all_features) > 3

    def test_claim_with_english_terms(self, parser):
        """Test handling of English technical terms"""
        claim_text = "청구항 1. processor, memory, sensor를 포함하는 IoT 장치"

        result = parser.parse_claim(claim_text)

        # Should handle mixed Korean and English
        assert len(result.all_features) > 0


class TestClaimParserIntegration:
    """Integration tests for claim parser"""

    def test_real_patent_claim_similarity(self):
        """Test with real-world patent claim examples"""
        parser = create_claim_parser()

        # Two related claims about display devices
        claim_a = parser.parse_claim(
            "청구항 1. 디스플레이를 포함하는 모바일 기기"
        )
        claim_b = parser.parse_claim(
            "청구항 2. LCD 화면을 구비한 이동 통신 단말"
        )

        similarity = parser.calculate_claim_similarity(claim_a, claim_b)

        # Should have some similarity despite different terminology
        assert similarity > 0.0

    def test_claim_parser_consistency(self):
        """Test that parser gives consistent results"""
        parser = create_claim_parser()

        claim_text = "청구항 1. 메모리와 프로세서를 포함하는 장치"

        result1 = parser.parse_claim(claim_text)
        result2 = parser.parse_claim(claim_text)

        # Should get same features both times
        assert result1.all_features == result2.all_features
        assert result1.normalized_features == result2.normalized_features
