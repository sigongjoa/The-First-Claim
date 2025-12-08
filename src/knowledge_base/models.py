"""
Data models for legal knowledge base - Patents, laws, and precedents
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class LawArticle:
    """Represents a law article with all metadata"""
    article_number: str  # "제30조"
    title: str  # "특허를 받을 수 없는 발명"
    content: str  # Full text of the article
    category: str  # "특허법", "민법", etc.
    subsections: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    effective_date: Optional[date] = None
    amendment_history: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "number": self.article_number,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "subsections": self.subsections,
            "requirements": self.requirements,
            "effects": self.effects,
            "exceptions": self.exceptions,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "amendment_history": self.amendment_history,
        }


@dataclass
class PrecedentCase:
    """Represents a legal precedent case with full metadata"""
    case_number: str  # "2020후1234"
    court: str  # "대법원" (Supreme Court), "특허법원" (Patent Court)
    decision_date: date
    case_type: str  # "신규성", "진보성", "권리범위"
    summary: str  # Brief summary (500 chars max)
    full_text: str  # Complete decision document
    key_holdings: List[str]  # Main legal principles
    cited_articles: List[str]  # Referenced law articles (e.g., ["제29조", "제30조"])
    outcome: str  # "인용" (granted), "기각" (rejected), "파기환송" (reversed and remanded)
    patent_field: Optional[str] = None  # Technical field (e.g., "전자", "기계")
    applicant_type: Optional[str] = None  # "개인", "회사", etc.

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "case_number": self.case_number,
            "court": self.court,
            "decision_date": self.decision_date.isoformat(),
            "case_type": self.case_type,
            "summary": self.summary,
            "full_text": self.full_text,
            "key_holdings": self.key_holdings,
            "cited_articles": self.cited_articles,
            "outcome": self.outcome,
            "patent_field": self.patent_field,
            "applicant_type": self.applicant_type,
        }


@dataclass
class ClaimComponent:
    """Represents parsed components of a patent claim"""
    component_type: str  # "preamble" (전제부), "body" (본문), "characterizing_part" (특징부)
    technical_features: List[str] = field(default_factory=list)
    functional_features: List[str] = field(default_factory=list)
    structural_elements: List[str] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "component_type": self.component_type,
            "technical_features": self.technical_features,
            "functional_features": self.functional_features,
            "structural_elements": self.structural_elements,
            "materials": self.materials,
        }
