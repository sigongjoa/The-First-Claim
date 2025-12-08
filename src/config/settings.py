"""
Application-wide settings and configuration

This module provides centralized configuration for the entire application,
including database settings, API settings, and integration with evaluation config.
"""

import os
from dataclasses import dataclass
from typing import Optional

from .evaluation_config import EvaluationConfig, get_evaluation_config


@dataclass
class DatabaseConfig:
    """Database configuration"""

    # SQLite settings
    sqlite_path: str = "data/sessions.db"
    """Path to SQLite database file"""

    session_ttl_seconds: int = 3600
    """Session TTL (1 hour default)"""

    # Vector database settings
    vector_db_path: str = "data/vector_db"
    """Path to vector database"""

    use_chromadb: bool = True
    """Use ChromaDB for vector storage"""


@dataclass
class ServerConfig:
    """Server configuration"""

    host: str = "0.0.0.0"
    """Server host"""

    port: int = 8000
    """Server port"""

    workers: int = 1
    """Number of worker processes"""

    reload: bool = False
    """Auto-reload on file changes"""

    environment: str = "development"
    """Environment: development or production"""


@dataclass
class OllamaConfig:
    """Ollama LLM configuration"""

    base_url: str = "http://localhost:11434"
    """Ollama API base URL"""

    embedding_model: str = "nomic-embed-text"
    """Model for text embeddings"""

    embedding_dimension: int = 768
    """Embedding vector dimension"""

    generation_model: str = "mistral"
    """Model for text generation"""

    timeout_seconds: int = 30
    """API call timeout"""

    max_retries: int = 3
    """Maximum retry attempts"""


@dataclass
class Settings:
    """Master application settings"""

    # Core configuration
    debug: bool = False
    """Debug mode"""

    app_name: str = "PROJECT: OVERRIDE"
    """Application name"""

    version: str = "0.2.0"
    """Application version"""

    # Component configs
    database: DatabaseConfig = None
    server: ServerConfig = None
    ollama: OllamaConfig = None
    evaluation: EvaluationConfig = None

    def __post_init__(self):
        """Initialize nested configs with defaults"""
        if self.database is None:
            self.database = DatabaseConfig()
        if self.server is None:
            self.server = ServerConfig()
        if self.ollama is None:
            self.ollama = OllamaConfig()
        if self.evaluation is None:
            self.evaluation = get_evaluation_config()

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables"""
        settings = cls()

        # Debug mode
        settings.debug = os.getenv("DEBUG", "false").lower() == "true"

        # Server config
        if os.getenv("SERVER_HOST"):
            settings.server.host = os.getenv("SERVER_HOST")
        if os.getenv("SERVER_PORT"):
            settings.server.port = int(os.getenv("SERVER_PORT"))
        if os.getenv("SERVER_ENVIRONMENT"):
            settings.server.environment = os.getenv("SERVER_ENVIRONMENT")

        # Database config
        if os.getenv("DB_PATH"):
            settings.database.sqlite_path = os.getenv("DB_PATH")
        if os.getenv("SESSION_TTL"):
            settings.database.session_ttl_seconds = int(os.getenv("SESSION_TTL"))

        # Ollama config
        if os.getenv("OLLAMA_BASE_URL"):
            settings.ollama.base_url = os.getenv("OLLAMA_BASE_URL")
        if os.getenv("OLLAMA_EMBEDDING_MODEL"):
            settings.ollama.embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL")
        if os.getenv("OLLAMA_GENERATION_MODEL"):
            settings.ollama.generation_model = os.getenv("OLLAMA_GENERATION_MODEL")

        return settings


def get_settings() -> Settings:
    """Get application settings (cached singleton)"""
    if not hasattr(get_settings, "_instance"):
        get_settings._instance = Settings.from_env()
    return get_settings._instance
