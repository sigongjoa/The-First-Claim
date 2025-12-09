# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PROJECT: OVERRIDE is an interactive game-based learning platform for the Korean Patent Attorney Examination (변리사 시험). It transforms legal learning by treating patent law and civil law as executable code through a Domain-Specific Language (DSL) approach.

**Core Philosophy**: "법을 읽는 사용자가 아니라, 법을 설계하는 창조자가 된다" (Become a creator who designs law, not just a user who reads it)

## Common Commands

### Running Tests
```bash
# Run all tests (505+ tests)
pytest tests/ -v

# Run specific test file
pytest tests/test_claim_parser.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run integration tests only
pytest tests/integration/ -v

# Run a single test
pytest tests/test_game.py::test_specific_function -v
```

### Running the Application
```bash
# Start the game (interactive CLI)
python src/main.py

# Start API server (requires Ollama running)
python -m src.api.server

# Start Ollama (in separate terminal)
ollama serve

# Pull required models
ollama pull nomic-embed-text
ollama pull mistral
```

### Code Quality
```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Ensure Ollama is running and models are pulled
ollama pull nomic-embed-text
ollama pull mistral
```

## Architecture Overview

### Three-Layer DSL System

**1. Knowledge Base Layer** (`src/knowledge_base/`, `src/data_collection/`)
- Patent law articles (40+ articles in `data/patent_law_articles.json`)
- Precedent cases (12+ cases in `data/patent_precedent_cases.json`)
- Vector database for semantic search (ChromaDB)
- RAG (Retrieval-Augmented Generation) system for legal reasoning

**2. Logic Engine Layer** (`src/dsl/`)
- **Vocabulary** (`src/dsl/vocabulary/`): Legal terms as data structures
- **Grammar** (`src/dsl/grammar/`): Claim writing rules
- **Logic** (`src/dsl/logic/`): 3-stage hybrid evaluation engine
  - Stage 1: Rule-based (Jaccard similarity, <50ms)
  - Stage 2: RAG-based (vector search, 200-500ms)
  - Stage 3: LLM-based (Ollama, 1-3s)
- **Evaluators** (`src/dsl/evaluators/`): Specialized evaluators for novelty, inventive step, etc.

**3. Client Layer** (`src/ui/`, `web/`)
- Game interface (`src/ui/game.py`)
- React frontend with custom hooks (`web/src/hooks/`)
- FastAPI REST API (`src/api/server.py`)

### Critical Components

**Claim Parser** (`src/dsl/logic/claim_parser.py`)
- Decomposes claims into: preamble, body, characterizing part
- Normalizes synonyms (디스플레이 → 표시_장치)
- Semantic analysis of claim structure

**Hybrid Evaluator** (`src/dsl/logic/hybrid_evaluator.py`)
- Combines rule-based, RAG-based, and LLM-based evaluation
- Weighted scoring system
- Returns detailed evaluation results with reasoning

**Session Management** (`src/storage/sqlite_session_store.py`)
- SQLite-based persistent storage
- TTL-based expiration (default: 1 hour)
- Thread-safe with RLock
- Automatic cleanup

**Configuration** (`src/config/`)
- Centralized configuration management
- Eliminated 40+ magic numbers
- Environment variable based (`EvaluationConfig`, `NoveltyConfig`, etc.)

## Key Architectural Principles

### 1. DSL-First Approach
Legal concepts are modeled as code:
- Statutes → Data structures (`CivilLawStatute`, `PatentRequirement`)
- Claims → Syntax trees (`ClaimElement`, `ClaimGrammar`)
- Judgments → Functions (`evaluate_novelty()`, `evaluate_inventive_step()`)

### 2. Test-Driven Development (TDD)
- Start with exam questions (requirements)
- Write failing tests
- Implement minimal code to pass
- Refactor for clarity
- 505/513 tests passing (98.4%)

### 3. Separation of Concerns
- **Game logic** is separate from **UI**
- **Evaluation engine** is separate from **data sources**
- **API contracts** are versioned and stable
- Frontend uses custom hooks for state management:
  - `useGameSession()` - session management
  - `useClaimValidation()` - claim validation and submission
  - `useGameTimer()` - timer control

### 4. Hybrid Evaluation Pipeline
Never rely on a single evaluation method:
1. **Fast path**: Rule-based checks (<50ms)
2. **Smart path**: RAG retrieval from legal knowledge base (200-500ms)
3. **Deep path**: LLM reasoning when needed (1-3s)

## Important File Locations

### Configuration
- `.env.example` - Environment variable template (copy to `.env`)
- `src/config/evaluation_config.py` - Central evaluation parameters
- `pytest.ini` - Test configuration
- `requirements.txt` - Python dependencies

### Data Sources
- `data/patent_law_articles.json` - 40+ patent law articles
- `data/patent_precedent_cases.json` - 12+ precedent cases
- `data/sessions.db` - SQLite session database (auto-created)

### Entry Points
- `src/main.py` - Interactive CLI game
- `src/api/server.py` - FastAPI server
- `tests/integration/` - Integration test suite

### Documentation
- `docs/02_architecture/01_technical_architecture.md` - Full system architecture
- `docs/02_architecture/02_dsl_design.md` - DSL design philosophy
- `docs/02_architecture/05_evaluation_system.md` - Evaluation engine details
- `README.md` - Project status and quick start

## Development Workflow

### When Adding New Features

1. **Configuration First**: If adding thresholds/parameters, define them in `src/config/`
2. **Test First**: Write tests in `tests/` before implementation
3. **DSL Thinking**: Model legal concepts as data structures, not strings
4. **Evaluation Strategy**: Consider all 3 stages (rule/RAG/LLM) in evaluation logic
5. **Documentation**: Update relevant docs in `docs/` if architecture changes

### When Working with Evaluation Logic

- **Rule-based**: Modify `src/dsl/logic/evaluator.py` for simple pattern matching
- **RAG-based**: Update knowledge base in `src/knowledge_base/` and data files
- **LLM-based**: Adjust prompts in `src/dsl/evaluators/ollama_evaluator.py`
- **Configuration**: All thresholds and weights go in `src/config/evaluation_config.py`

### When Adding Legal Knowledge

1. Add articles to `data/patent_law_articles.json` or `data/patent_precedent_cases.json`
2. Run data collection scripts in `src/data_collection/`
3. Vector embeddings are automatically generated on server startup
4. Test with integration tests in `tests/integration/`

## Current Status (Phase D' Complete)

**Completed**:
- ✅ 40+ patent law articles + 12+ precedent cases
- ✅ 3-stage hybrid evaluation engine (rule → RAG → LLM)
- ✅ Centralized configuration (40+ magic numbers eliminated)
- ✅ Semantic claim parser with synonym normalization
- ✅ SQLite session storage with TTL
- ✅ React custom hooks for frontend state management
- ✅ 505/513 tests passing (98.4%)
- ✅ Core coverage: 85%+ (claim_parser: 95%, evaluator: 96%, config: 92%)

**Next Phase**:
- Web UI completion
- Additional legal knowledge expansion
- Performance optimization

## Testing Guidelines

- Unit tests go in `tests/test_*.py`
- Integration tests go in `tests/integration/`
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`
- Mock external services (Ollama) in unit tests
- Integration tests can use real Ollama if available
- Target: 95%+ coverage for core modules

## Special Notes

- **Ollama Required**: The LLM evaluation stage requires Ollama running locally
- **Environment Variables**: Always configure via `.env`, never hardcode
- **Session Persistence**: Sessions are stored in SQLite (`data/sessions.db`)
- **Thread Safety**: Session store uses RLock for concurrent access
- **Timeout Handling**: Evaluation has 5-second default timeout (configurable)
- **Korean Language**: Legal content is in Korean; code/comments mix Korean and English
