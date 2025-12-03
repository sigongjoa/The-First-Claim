"""Vocabulary module - Core data models for legal domain."""

from .civil_law import CivilLawStatute, Person, Transaction, LegalRight

__all__ = [
    "CivilLawStatute",
    "Person",
    "Transaction",
    "LegalRight",
]
