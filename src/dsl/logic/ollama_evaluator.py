"""
Ollama-Based Patent Claim Evaluator - Ollama를 이용한 청구항 평가

로컬 Ollama 서버를 사용하여 한국 특허법을 기반으로 청구항을 평가합니다.
"""

from __future__ import annotations

import json
import requests
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime


@dataclass
class OllamaEvaluationResult:
    """Ollama 평가 결과"""

    claim_number: int
    claim_content: str
    is_approvable: bool
    
    # 점수
    clarity_score: float
    antecedent_basis_score: float
    unity_score: float
    definiteness_score: float
    novelty_score: float
    inventive_step_score: float
    
    # 의견
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    overall_opinion: str = ""
    estimated_approval_probability: float = 0.0
    
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """결과 검증"""
        if not (0.0 <= self.clarity_score <= 1.0):
            raise ValueError("clarity_score는 0.0 ~ 1.0 범위여야 합니다")

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


class OllamaClaimEvaluator:
    """Ollama 기반 청구항 평가 엔진"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2:7b"):
        """OllamaClaimEvaluator 초기화
        
        Args:
            base_url: Ollama 서버 URL
            model: 사용할 모델 (default: mistral)
        """
        self.base_url = base_url
        self.model = model
        self.health_check_url = f"{base_url}/api/tags"

    def is_available(self) -> bool:
        """Ollama 서버 사용 가능 여부 확인"""
        response = requests.get(self.health_check_url, timeout=2)
        return response.status_code == 200

    def evaluate_claim(
        self,
        claim_number: int,
        claim_content: str,
        claim_type: str = "independent",
        prior_claims: Optional[List[str]] = None,
    ) -> OllamaEvaluationResult:
        """청구항 평가

        Args:
            claim_number: 청구항 번호
            claim_content: 청구항 내용
            claim_type: 청구항 타입 (independent/dependent)
            prior_claims: 선행 청구항 리스트

        Returns:
            OllamaEvaluationResult
        """
        prompt = self._build_evaluation_prompt(
            claim_number, claim_content, claim_type, prior_claims
        )

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=30,
        )

        if response.status_code != 200:
            raise RuntimeError(f"Ollama API 오류: {response.text}")

        result_text = response.json().get("response", "")
        return self._parse_evaluation_result(
            claim_number, claim_content, result_text
        )

    def evaluate_claims(
        self,
        claims: Dict[int, Tuple[str, str]],  # {number: (type, content)}
    ) -> List[OllamaEvaluationResult]:
        """청구항 세트 평가"""
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
        prompt = f"""당신은 한국 특허청의 심사관입니다. 다음 청구항을 한국 특허법 기준에 따라 평가하세요.

청구항 번호: {claim_number}
청구항 타입: {'독립항' if claim_type == 'independent' else '종속항'}
청구항 내용: {claim_content}

"""
        
        if prior_claims and claim_type == "dependent":
            prompt += f"선행 청구항:\n"
            for i, prior in enumerate(prior_claims, 1):
                prompt += f"  {i}. {prior}\n"
            prompt += "\n"
        
        prompt += """다음 항목들을 평가하세요 (JSON 형식):

{
    "is_approvable": boolean (등록 가능 여부),
    "clarity_score": float (0.0~1.0, 명확성 - 제42조),
    "antecedent_basis_score": float (0.0~1.0, 선행기술 기반 - 제45조),
    "unity_score": float (0.0~1.0, 단일성),
    "definiteness_score": float (0.0~1.0, 확정성),
    "novelty_score": float (0.0~1.0, 신규성 - 제32조),
    "inventive_step_score": float (0.0~1.0, 진보성 - 제33조),
    "strengths": ["강점1", "강점2"],
    "weaknesses": ["약점1", "약점2"],
    "improvements": ["개선방안1", "개선방안2"],
    "overall_opinion": "종합 의견",
    "estimated_approval_probability": float (0.0~1.0)
}

한국 특허법을 엄격하게 적용하세요."""
        
        return prompt

    def _parse_evaluation_result(
        self,
        claim_number: int,
        claim_content: str,
        result_text: str,
    ) -> OllamaEvaluationResult:
        """평가 결과 파싱"""
        # JSON 추출
        json_start = result_text.find("{")
        json_end = result_text.rfind("}") + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("응답에서 JSON을 찾을 수 없습니다")

        json_str = result_text[json_start:json_end]
        # LLM이 때로 single quote를 사용하는 경우 처리
        json_str = json_str.replace("'", '"')
        data = json.loads(json_str)

        return OllamaEvaluationResult(
            claim_number=claim_number,
            claim_content=claim_content,
            is_approvable=data.get("is_approvable", False),
            clarity_score=float(data.get("clarity_score") or 0.5),
            antecedent_basis_score=float(data.get("antecedent_basis_score") or 0.5),
            unity_score=float(data.get("unity_score") or 0.5),
            definiteness_score=float(data.get("definiteness_score") or 0.5),
            novelty_score=float(data.get("novelty_score") or 0.5),
            inventive_step_score=float(data.get("inventive_step_score") or 0.5),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            improvements=data.get("improvements", []),
            overall_opinion=data.get("overall_opinion", ""),
            estimated_approval_probability=float(
                data.get("estimated_approval_probability") or 0.5
            ),
        )
