"""Vocabulary module - Core data models for legal domain."""

from .civil_law import CivilLawStatute, Person, Transaction, LegalRight
from .patent_law import PatentArticle, Invention, PatentClaim, PatentExamination

__all__ = [
    "CivilLawStatute",
    "Person",
    "Transaction",
    "LegalRight",
    "PatentArticle",
    "Invention",
    "PatentClaim",
    "PatentExamination",
]
