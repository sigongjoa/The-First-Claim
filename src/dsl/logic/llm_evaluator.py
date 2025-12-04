"""
LLM-Based Patent Claim Evaluator - LLM을 이용한 청구항 평가

Claude API를 사용하여 한국 특허법을 기반으로 청구항을 실시간 평가합니다.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class EvaluationCritera(Enum):
    """평가 기준"""
    
    CLARITY = "명확성"  # 제42조 - 청구항은 명확해야 함
    ANTECEDENT_BASIS = "선행기술"  # 제45조 - 선행항 기반
    UNITY = "단일성"  # 제46조 - 청구항 단일성
    DEFINITENESS = "확정성"  # 청구항은 기술적으로 확정되어야 함
    NOVELTY = "신규성"  # 제32조 - 신규성
    INVENTIVE_STEP = "진보성"  # 제33조 - 진보성


@dataclass
class LLMEvaluationResult:
    """LLM 평가 결과"""
    
    claim_number: int
    claim_content: str
    is_approvable: bool  # 등록 가능 여부
    
    # 평가 점수
    clarity_score: float  # 0.0 ~ 1.0
    antecedent_basis_score: float
    unity_score: float
    definiteness_score: float
    novelty_score: float
    inventive_step_score: float
    
    # 평가 의견
    strengths: List[str] = field(default_factory=list)  # 강점
    weaknesses: List[str] = field(default_factory=list)  # 약점
    improvements: List[str] = field(default_factory=list)  # 개선 방안
    
    # 법적 참조
    relevant_articles: List[str] = field(default_factory=list)  # 관련 특허법 조항
    case_law_references: List[str] = field(default_factory=list)  # 판례 참조
    
    # 최종 의견
    overall_opinion: str = ""  # 종합 의견
    estimated_approval_probability: float = 0.0  # 승인 확률 추정치
    
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """결과 검증"""
        if not (0.0 <= self.clarity_score <= 1.0):
            raise ValueError("clarity_score는 0.0 ~ 1.0 범위여야 합니다")
        if not (0.0 <= self.estimated_approval_probability <= 1.0):
            raise ValueError("estimated_approval_probability는 0.0 ~ 1.0 범위여야 합니다")

    def get_overall_score(self) -> float:
        """종합 점수 계산"""
        scores = [
            self.clarity_score * 0.2,
            self.antecedent_basis_score * 0.2,
            self.unity_score * 0.15,
            self.definiteness_score * 0.15,
            self.novelty_score * 0.15,
            self.inventive_step_score * 0.15,
        ]
        return sum(scores)

    def __str__(self) -> str:
        """사용자 친화적 문자열 표현"""
        status = "✅ 등록 가능" if self.is_approvable else "❌ 등록 불가"
        score = self.get_overall_score()
        return (
            f"{status} (청구항 {self.claim_number})\n"
            f"종합 점수: {score:.2f}/1.0\n"
            f"승인 확률: {self.estimated_approval_probability:.1%}"
        )


class KoreanPatentLawContext:
    """한국 특허법 컨텍스트"""

    # 주요 특허법 조항
    ARTICLES = {
        "제2조": "발명의 정의",
        "제32조": "신규성 (자연법칙을 이용한 기술적 사상의 창작)",
        "제33조": "진보성 (통상의 지식을 가진 자가 용이하게 생각해낼 수 없는 발명)",
        "제34조": "산업상 이용가능성",
        "제42조": "청구항 명확성 (청구항은 명확해야 함)",
        "제45조": "종속항 (선행항의 전체 구성요소를 포함하고 제한을 가할 수 있음)",
        "제46조": "청구항 단일성 (동일한 발명적 사상의 범위 내에서 복수의 청구항)",
        "제64조": "침해 추정 (실질적으로 동일한 구성은 침해로 추정)",
        "제47조": "청구항 작성 형식",
    }

    # 한국 특허청 심사기준
    EXAMINATION_GUIDELINES = {
        "명확성": "청구항이 명백하고 과도하게 광범위하지 않아야 함",
        "단일성": "각 청구항은 기술적 관계를 가져야 함",
        "신규성": "선행 공개된 발명과 실질적으로 동일하지 않아야 함",
        "진보성": "통상의 지식을 가진 자가 용이하게 생각해낼 수 없어야 함",
    }

    @staticmethod
    def get_law_context() -> str:
        """법적 컨텍스트 생성"""
        context = "한국 특허법 컨텍스트:\n\n"
        context += "주요 조항:\n"
        for article, description in KoreanPatentLawContext.ARTICLES.items():
            context += f"  {article}: {description}\n"
        
        context += "\n심사 기준:\n"
        for criterion, guideline in KoreanPatentLawContext.EXAMINATION_GUIDELINES.items():
            context += f"  {criterion}: {guideline}\n"
        
        return context


class LLMClaimEvaluator:
    """LLM 기반 청구항 평가 엔진"""

    def __init__(self, api_key: Optional[str] = None):
        """LLMClaimEvaluator 초기화
        
        Args:
            api_key: Anthropic API 키 (없으면 환경변수에서 로드)
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic 패키지가 설치되지 않았습니다. "
                "pip install anthropic을 실행하세요."
            )
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다."
            )
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.law_context = KoreanPatentLawContext.get_law_context()

    def evaluate_claim(
        self,
        claim_number: int,
        claim_content: str,
        claim_type: str = "independent",
        prior_claims: Optional[List[str]] = None,
    ) -> LLMEvaluationResult:
        """청구항 평가
        
        Args:
            claim_number: 청구항 번호
            claim_content: 청구항 내용
            claim_type: 청구항 타입 (independent/dependent)
            prior_claims: 선행 청구항 리스트
            
        Returns:
            LLMEvaluationResult
        """
        prompt = self._build_evaluation_prompt(
            claim_number, claim_content, claim_type, prior_claims
        )
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            
            result_text = response.content[0].text
            return self._parse_evaluation_result(
                claim_number, claim_content, result_text
            )
        
        except Exception as e:
            raise RuntimeError(f"LLM 평가 중 오류 발생: {e}")

    def evaluate_claims(
        self,
        claims: Dict[int, Tuple[str, str]],  # {number: (type, content)}
    ) -> List[LLMEvaluationResult]:
        """청구항 세트 평가
        
        Args:
            claims: 청구항 딕셔너리
            
        Returns:
            평가 결과 리스트
        """
        results = []
        prior_claims = []
        
        for claim_number, (claim_type, claim_content) in sorted(claims.items()):
            result = self.evaluate_claim(
                claim_number=claim_number,
                claim_content=claim_content,
                claim_type=claim_type,
                prior_claims=prior_claims if claim_type == "dependent" else None,
            )
            
            results.append(result)
            prior_claims.append(claim_content)
        
        return results

    def _build_evaluation_prompt(
        self,
        claim_number: int,
        claim_content: str,
        claim_type: str,
        prior_claims: Optional[List[str]],
    ) -> str:
        """평가 프롬프트 구성"""
        prompt = f"""
{self.law_context}

당신은 한국 특허청의 심사관입니다. 다음 청구항을 한국 특허법 기준에 따라 평가하세요.

청구항 번호: {claim_number}
청구항 타입: {'독립항' if claim_type == 'independent' else '종속항'}
청구항 내용: {claim_content}

"""
        
        if prior_claims and claim_type == "dependent":
            prompt += f"선행 청구항:\n"
            for i, prior in enumerate(prior_claims, 1):
                prompt += f"  {i}. {prior}\n"
            prompt += "\n"
        
        prompt += """
다음 항목들을 JSON 형식으로 평가하세요:

{
    "is_approvable": boolean (등록 가능 여부),
    "scores": {
        "clarity": float (0.0~1.0, 명확성),
        "antecedent_basis": float (0.0~1.0, 선행기술 기반),
        "unity": float (0.0~1.0, 단일성),
        "definiteness": float (0.0~1.0, 확정성),
        "novelty": float (0.0~1.0, 신규성),
        "inventive_step": float (0.0~1.0, 진보성)
    },
    "strengths": ["강점1", "강점2", ...],
    "weaknesses": ["약점1", "약점2", ...],
    "improvements": ["개선방안1", "개선방안2", ...],
    "relevant_articles": ["제42조", "제45조", ...],
    "case_law_references": ["판례1", "판례2", ...],
    "overall_opinion": "종합 의견",
    "estimated_approval_probability": float (0.0~1.0)
}

한국 특허법의 심사 기준을 엄격하게 적용하세요.
"""
        return prompt

    def _parse_evaluation_result(
        self,
        claim_number: int,
        claim_content: str,
        result_text: str,
    ) -> LLMEvaluationResult:
        """평가 결과 파싱"""
        try:
            # JSON 추출
            json_start = result_text.find("{")
            json_end = result_text.rfind("}") + 1
            json_str = result_text[json_start:json_end]
            
            data = json.loads(json_str)
            
            return LLMEvaluationResult(
                claim_number=claim_number,
                claim_content=claim_content,
                is_approvable=data.get("is_approvable", False),
                clarity_score=float(data["scores"].get("clarity", 0.0)),
                antecedent_basis_score=float(data["scores"].get("antecedent_basis", 0.0)),
                unity_score=float(data["scores"].get("unity", 0.0)),
                definiteness_score=float(data["scores"].get("definiteness", 0.0)),
                novelty_score=float(data["scores"].get("novelty", 0.0)),
                inventive_step_score=float(data["scores"].get("inventive_step", 0.0)),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                improvements=data.get("improvements", []),
                relevant_articles=data.get("relevant_articles", []),
                case_law_references=data.get("case_law_references", []),
                overall_opinion=data.get("overall_opinion", ""),
                estimated_approval_probability=float(
                    data.get("estimated_approval_probability", 0.0)
                ),
            )
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"평가 결과 파싱 실패: {e}\n응답: {result_text}")


# 글로벌 인스턴스 (싱글톤)
_llm_evaluator: Optional[LLMClaimEvaluator] = None


def get_llm_evaluator(api_key: Optional[str] = None) -> LLMClaimEvaluator:
    """LLM 평가기 인스턴스 가져오기"""
    global _llm_evaluator
    if _llm_evaluator is None:
        _llm_evaluator = LLMClaimEvaluator(api_key=api_key)
    return _llm_evaluator
