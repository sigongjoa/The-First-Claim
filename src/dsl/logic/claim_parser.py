"""
Patent Claim Component Parser - Decomposes claims into semantic components

This module parses patent claims into their component parts (preamble, body,
characterizing part) and extracts technical, functional, and structural features.
It handles Korean patent claim terminology and provides synonym normalization.
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set

from src.knowledge_base.models import ClaimComponent

logger = logging.getLogger(__name__)


@dataclass
class ParsedClaim:
    """Result of parsing a patent claim"""
    original_text: str
    preamble: str  # 전제부
    body: str  # 본문
    characterizing_part: str  # 특징부

    components: List[ClaimComponent] = field(default_factory=list)
    all_features: Set[str] = field(default_factory=set)
    normalized_features: Set[str] = field(default_factory=set)


class SynonymDictionary:
    """Korean patent terminology synonym dictionary"""

    def __init__(self):
        """Initialize with built-in synonym mappings"""
        self.synonyms = {
            # Display terms
            "표시_장치": {
                "display", "displays", "표시장치", "디스플레이", "화면",
                "모니터", "판넬", "lcd", "led", "oled", "LCD", "LED", "OLED"
            },
            # Storage terms
            "저장_장치": {
                "storage", "메모리", "스토리지", "저장부", "저장소",
                "HDD", "SSD", "EEPROM"
            },
            # Processing terms
            "처리_장치": {
                "processor", "processing", "프로세서", "처리부", "CPU",
                "제어부", "연산부"
            },
            # Communication terms
            "통신_장치": {
                "communication", "통신부", "통신 인터페이스", "송수신부",
                "모뎀", "라우터", "게이트웨이"
            },
            # Sensor terms
            "센서": {
                "sensor", "감지", "감지기", "검출기", "감센", "디텍터"
            },
            # Connection terms
            "연결": {
                "connection", "연결부", "연결 수단", "접속", "결합",
                "커넥터", "케이블"
            },
            # Control terms
            "제어": {
                "control", "제어부", "제어 수단", "조정", "관리", "컨트롤러"
            },
            # Output terms
            "출력": {
                "output", "출력 수단", "표시", "표현", "전송"
            },
            # Input terms
            "입력": {
                "input", "입력 수단", "수신", "감지", "검출"
            },
        }

    def get_canonical_form(self, term: str) -> str:
        """
        Get the canonical form of a term

        Args:
            term: Input term

        Returns:
            Canonical form or original term if no mapping found
        """
        term_lower = term.lower().strip()

        for canonical, synonyms in self.synonyms.items():
            if term_lower in synonyms or term_lower.replace(" ", "_") in {s.replace(" ", "_") for s in synonyms}:
                return canonical

        return term

    def are_synonyms(self, term1: str, term2: str) -> bool:
        """
        Check if two terms are synonyms

        Args:
            term1: First term
            term2: Second term

        Returns:
            True if terms are synonyms
        """
        canonical1 = self.get_canonical_form(term1)
        canonical2 = self.get_canonical_form(term2)
        return canonical1 == canonical2


class ClaimComponentParser:
    """Parses patent claims into semantic components"""

    def __init__(self):
        """Initialize the parser"""
        self.synonym_dict = SynonymDictionary()

        # Korean patent claim markers
        self.preamble_markers = ["청구항", "특허청구범위", "발명의 범위"]
        self.body_markers = ["다음", "이하", "다음과 같은"]
        self.characterizing_markers = ["특징부", "특징은", "특이한 점", "포함"]

    def parse_claim(self, claim_text: str) -> ParsedClaim:
        """
        Parse a patent claim into components

        Args:
            claim_text: Full claim text

        Returns:
            ParsedClaim with extracted components
        """
        # Clean text
        claim_text = claim_text.strip()

        # Identify claim structure
        preamble = self._extract_preamble(claim_text)
        body = self._extract_body(claim_text)
        characterizing_part = self._extract_characterizing_part(claim_text)

        # Extract features from each part
        preamble_component = self._parse_component("preamble", preamble)
        body_component = self._parse_component("body", body)
        char_component = self._parse_component("characterizing_part", characterizing_part)

        # Collect all features
        all_features = set()
        all_features.update(preamble_component.technical_features)
        all_features.update(body_component.technical_features)
        all_features.update(char_component.technical_features)

        # Normalize features
        normalized_features = {self.synonym_dict.get_canonical_form(f) for f in all_features}

        return ParsedClaim(
            original_text=claim_text,
            preamble=preamble,
            body=body,
            characterizing_part=characterizing_part,
            components=[preamble_component, body_component, char_component],
            all_features=all_features,
            normalized_features=normalized_features
        )

    def _extract_preamble(self, claim_text: str) -> str:
        """Extract preamble (전제부) from claim"""
        # Preamble typically ends before "다음" or "다음과 같은"
        for marker in self.body_markers:
            idx = claim_text.find(marker)
            if idx != -1:
                return claim_text[:idx].strip()

        # If no marker found, assume first 30% or first sentence
        sentences = claim_text.split("。") + claim_text.split(".")
        return sentences[0].strip() if sentences else claim_text[:100]

    def _extract_body(self, claim_text: str) -> str:
        """Extract body (본문) from claim"""
        preamble = self._extract_preamble(claim_text)
        rest = claim_text[len(preamble):].strip()

        # Body ends before characteristic part
        for marker in self.characterizing_markers:
            idx = rest.find(marker)
            if idx != -1:
                return rest[:idx].strip()

        # If no marker, take middle portion
        return rest[:len(rest) // 2]

    def _extract_characterizing_part(self, claim_text: str) -> str:
        """Extract characterizing part (특징부) from claim"""
        # Look for characteristic part markers
        for marker in self.characterizing_markers:
            idx = claim_text.rfind(marker)  # Use rfind for last occurrence
            if idx != -1:
                return claim_text[idx:].strip()

        # Fallback: return last portion of claim
        return claim_text[len(claim_text) // 2:]

    def _parse_component(self, component_type: str, text: str) -> ClaimComponent:
        """
        Parse a claim component to extract features

        Args:
            component_type: Type of component (preamble, body, etc.)
            text: Component text

        Returns:
            ClaimComponent with extracted features
        """
        component = ClaimComponent(component_type=component_type)

        # Extract technical features (nouns)
        technical_features = self._extract_technical_features(text)
        component.technical_features = list(technical_features)

        # Extract functional features (verbs/actions)
        functional_features = self._extract_functional_features(text)
        component.functional_features = list(functional_features)

        # Extract structural elements
        structural_elements = self._extract_structural_elements(text)
        component.structural_elements = list(structural_elements)

        return component

    def _extract_technical_features(self, text: str) -> Set[str]:
        """
        Extract technical features (primarily nouns)

        Args:
            text: Component text

        Returns:
            Set of technical features
        """
        features = set()

        # Korean noun patterns
        # Simple regex-based extraction (replace with proper NLP for production)
        noun_patterns = [
            r"([가-힣]+장치)",  # X장치 (device)
            r"([가-힣]+부)",     # X부 (unit/part)
            r"([가-힣]+기)",     # X기 (apparatus)
            r"([가-힣]+막)",     # X막 (membrane)
            r"([가-힣]+체)",     # X체 (body)
            r"([가-힣]+선)",     # X선 (line/ray)
            r"([가-힣]+실)",     # X실 (thread)
            r"([가-힣]+판)",     # X판 (panel/plate)
            r"([가-힣]+화면)",   # X화면 (screen)
            r"([가-힣]{2,})",    # Any 2+ character Korean word (greedy fallback)
        ]

        for pattern in noun_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) >= 2:  # Only keep meaningful terms
                    features.add(match)

        # Also look for English technical terms
        english_patterns = [
            r"\b(processor|memory|sensor|device|module|controller|interface|display|LCD|LED|SSD|HDD|IoT)\b",
            r"([A-Z]{2,})",  # Acronyms like LCD, LED, SSD
        ]

        for pattern in english_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            features.update(matches)

        return features

    def _extract_functional_features(self, text: str) -> Set[str]:
        """
        Extract functional features (actions, behaviors)

        Args:
            text: Component text

        Returns:
            Set of functional features
        """
        features = set()

        # Korean verb patterns
        verb_patterns = [
            r"([가-힣]+)(한다|한다|하여|하고|함)",  # X한다 patterns
            r"([가-힣]+)(에 의해|에 의하여)",        # Passive patterns
        ]

        for pattern in verb_patterns:
            matches = re.findall(pattern, text)
            features.update([m[0] if isinstance(m, tuple) else m for m in matches])

        return features

    def _extract_structural_elements(self, text: str) -> Set[str]:
        """
        Extract structural elements (materials, connections)

        Args:
            text: Component text

        Returns:
            Set of structural elements
        """
        features = set()

        # Material and connection patterns
        material_patterns = [
            r"([가-힣]+)로 된|([가-힣]+)로 구성",  # Made of X
            r"([가-힣]+)과 ([가-힣]+)의 결합",     # Combination of X and Y
        ]

        for pattern in material_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    features.update([m for m in match if m])
                else:
                    features.add(match)

        return features

    def get_feature_vector(self, parsed_claim: ParsedClaim) -> Dict[str, int]:
        """
        Convert parsed claim to feature vector for comparison

        Args:
            parsed_claim: ParsedClaim object

        Returns:
            Dictionary of normalized features with counts
        """
        feature_counts = {}

        for feature in parsed_claim.all_features:
            canonical = self.synonym_dict.get_canonical_form(feature)
            feature_counts[canonical] = feature_counts.get(canonical, 0) + 1

        return feature_counts

    def calculate_claim_similarity(self, claim1: ParsedClaim, claim2: ParsedClaim) -> float:
        """
        Calculate similarity between two parsed claims using normalized features

        Args:
            claim1: First parsed claim
            claim2: Second parsed claim

        Returns:
            Similarity score (0.0-1.0)
        """
        features1 = claim1.normalized_features
        features2 = claim2.normalized_features

        if not features1 or not features2:
            return 0.0

        intersection = len(features1 & features2)
        union = len(features1 | features2)

        if union == 0:
            return 0.0

        return intersection / union  # Jaccard similarity


def create_claim_parser() -> ClaimComponentParser:
    """Factory function to create a claim parser"""
    return ClaimComponentParser()
