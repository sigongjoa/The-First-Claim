"""
Evaluation engine configuration - Defines all parameters for novelty and inventive step evaluation

This module eliminates magic numbers from the evaluator by centralizing all configuration
parameters with sensible defaults and environment-based overrides.
"""

from typing import Dict, Optional
import os
from dataclasses import dataclass, field


@dataclass
class NoveltyConfig:
    """Configuration for novelty evaluation

    Novelty evaluation has three stages:
    1. Rule-based: Fast Jaccard similarity check
    2. Vector-based: Semantic similarity via RAG
    3. LLM-based: Final judgment by language model
    """

    # Stage 1: Rule-based filtering
    min_similarity_threshold: float = 0.7
    """Jaccard similarity threshold for quick rejection (0.0-1.0)"""

    # Stage 2: RAG-based semantic search
    vector_search_top_k: int = 5
    """Number of top results to retrieve from vector database"""

    vector_similarity_threshold: float = 0.6
    """Minimum cosine similarity for RAG results (0.0-1.0)"""

    # Stage 3: LLM judgment
    use_llm_judgment: bool = True
    """Enable LLM final judgment for borderline cases"""

    vector_similarity_weight: float = 0.6
    """Weight for vector similarity in final score (0.0-1.0)"""

    llm_judgment_weight: float = 0.4
    """Weight for LLM judgment in final score (0.0-1.0)"""

    # Cache and performance
    enable_result_caching: bool = True
    """Cache novelty evaluation results"""

    cache_ttl_seconds: int = 3600
    """TTL for cached results"""


@dataclass
class InventiveStepConfig:
    """Configuration for inventive step evaluation

    Inventive step evaluation uses rule-based analysis followed by
    precedent case research and LLM judgment.
    """

    # Technical complexity levels by field
    technical_complexity: Dict[str, float] = field(default_factory=lambda: {
        "전자": 0.8,           # Electronics: high complexity
        "기계": 0.7,           # Mechanical: moderate-high
        "화학": 0.9,           # Chemical: very high
        "바이오": 0.9,         # Biotechnology: very high
        "소프트웨어": 0.6,     # Software: moderate
        "디자인": 0.5,         # Design: moderate-low
        "기타": 0.5            # Other: default
    })
    """Complexity factor for each technical field (0.0-1.0)"""

    # Feature-based evaluation
    min_feature_count: int = 10
    """Minimum feature count for significant innovation"""

    feature_weight: float = 0.3
    """Weight for feature count in inventive step judgment"""

    # Combination with prior art
    combination_weight: float = 0.6
    """Weight for novel combination of known features"""

    # Precedent reference
    use_precedent_search: bool = True
    """Search precedent cases for similar evaluations"""

    precedent_search_top_k: int = 5
    """Number of precedent cases to retrieve"""

    precedent_relevance_weight: float = 0.4
    """Weight for precedent case guidance"""

    # LLM judgment
    use_llm_judgment: bool = True
    """Enable LLM judgment for final decision"""

    llm_judgment_weight: float = 0.6
    """Weight for LLM judgment vs rule-based (0.0-1.0)"""


@dataclass
class EvaluationConfig:
    """Master configuration for the evaluation engine

    Combines novelty and inventive step configurations with system-wide settings.
    """

    # Evaluation engines
    novelty: NoveltyConfig = field(default_factory=NoveltyConfig)
    """Novelty evaluation configuration"""

    inventive_step: InventiveStepConfig = field(default_factory=InventiveStepConfig)
    """Inventive step evaluation configuration"""

    # Enable/disable evaluation stages
    enable_rule_based: bool = True
    """Enable rule-based filtering stage"""

    enable_rag: bool = True
    """Enable RAG (Retrieval-Augmented Generation) stage"""

    enable_llm: bool = True
    """Enable LLM judgment stage"""

    # LLM settings
    llm_model: str = "mistral"  # Ollama model
    """LLM model name for Ollama (mistral, llama2, etc.)"""

    llm_timeout_seconds: int = 30
    """Timeout for LLM calls"""

    llm_temperature: float = 0.3
    """LLM temperature (0.0-1.0) - lower = more deterministic"""

    # Logging and debugging
    debug_mode: bool = False
    """Enable debug logging for evaluation process"""

    log_evaluation_steps: bool = True
    """Log each stage of evaluation (rule → RAG → LLM)"""

    # Performance tuning
    evaluation_timeout_seconds: int = 5
    """Maximum time for complete evaluation"""

    enable_parallel_evaluation: bool = False
    """Enable parallel evaluation of novelty and inventive step"""


def get_evaluation_config() -> EvaluationConfig:
    """
    Load evaluation configuration from environment variables or defaults

    Environment variables:
    - EVAL_NOVELTY_THRESHOLD: min_similarity_threshold (default: 0.7)
    - EVAL_RAG_TOP_K: vector_search_top_k (default: 5)
    - EVAL_LLM_MODEL: llm_model (default: mistral)
    - EVAL_DEBUG: debug_mode (default: False)
    - EVAL_TIMEOUT: evaluation_timeout_seconds (default: 5)

    Returns:
        EvaluationConfig with environment-based overrides
    """
    config = EvaluationConfig()

    # Override from environment variables
    if os.getenv("EVAL_NOVELTY_THRESHOLD"):
        config.novelty.min_similarity_threshold = float(os.getenv("EVAL_NOVELTY_THRESHOLD"))

    if os.getenv("EVAL_RAG_TOP_K"):
        config.novelty.vector_search_top_k = int(os.getenv("EVAL_RAG_TOP_K"))

    if os.getenv("EVAL_LLM_MODEL"):
        config.llm_model = os.getenv("EVAL_LLM_MODEL")

    if os.getenv("EVAL_DEBUG"):
        config.debug_mode = os.getenv("EVAL_DEBUG").lower() == "true"

    if os.getenv("EVAL_TIMEOUT"):
        config.evaluation_timeout_seconds = int(os.getenv("EVAL_TIMEOUT"))

    if os.getenv("EVAL_ENABLE_LLM"):
        config.enable_llm = os.getenv("EVAL_ENABLE_LLM").lower() == "true"

    if os.getenv("EVAL_ENABLE_RAG"):
        config.enable_rag = os.getenv("EVAL_ENABLE_RAG").lower() == "true"

    return config
