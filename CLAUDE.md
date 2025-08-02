# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Backend Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI backend
python scripts/start.py
# Or directly with uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run Python tests
pytest
pytest tests/ -v  # verbose mode
pytest tests/test_specific.py::test_function  # run single test

# Format Python code
black src/
black src/ --check  # check without modifying

# Lint Python code  
flake8 src/
mypy src/  # type checking
```

### Frontend Development
```bash
# Install Node.js dependencies
npm install

# Run frontend development server
npm run dev

# Build for production
npm run build

# Run frontend tests
npm test
npm run test:watch  # watch mode

# Lint frontend code
npm run lint
```

## High-Level Architecture

### Project Structure
This is a merged project combining two systems:
1. **Fantasy AI Ultimate** - AI-powered fantasy sports analysis platform
2. **Yahoo Fantasy Wrapper** - Python wrapper for Yahoo Fantasy Sports API

### Key Components

#### Backend (FastAPI)
- **src/main.py**: Main FastAPI application that serves as the API gateway
  - Handles OAuth2 authentication flow with Yahoo
  - Provides REST endpoints for Yahoo Fantasy data
  - Exposes AI analysis endpoints
  - Serves static files and web interface

- **src/shared/**:
  - **database.py**: DatabaseManager class for async database operations
  - **ai_engine.py**: AIAnalysisEngine for player analysis and predictions
  - **models.py**: Pydantic models and SQLAlchemy ORM models

- **src/yahoo_wrapper/**: Python wrapper for Yahoo Fantasy API
  - Handles OAuth2 token management
  - Provides typed interfaces for Yahoo Fantasy endpoints
  - Manages rate limiting and caching

#### Configuration
- **config/settings.py**: Centralized configuration using Pydantic BaseSettings
  - Environment-based configuration
  - Database URL construction based on environment
  - Yahoo API credentials management

#### Yahoo Fantasy Integration
The project uses OAuth2 for Yahoo authentication:
1. User initiates auth via `/auth/authorize`
2. Yahoo redirects to `/auth/callback` with authorization code
3. Backend exchanges code for access/refresh tokens
4. Tokens are used for subsequent Yahoo API calls

#### Data Flow
1. **Frontend** → FastAPI endpoints → Yahoo API/Database
2. **Yahoo API** → Data processing → AI Engine → Analysis results
3. **Database** stores player stats, predictions, and cached data

### Important Implementation Details

- **Async Architecture**: Uses async/await throughout for performance
- **Token Management**: Automatic refresh token handling for Yahoo OAuth2
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **CORS**: Configured to allow frontend communication
- **Caching**: Optional Redis caching for improved performance

### Environment Setup
Required environment variables:
- `YAHOO_CLIENT_ID`: Yahoo app client ID
- `YAHOO_CLIENT_SECRET`: Yahoo app client secret
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `REDIS_URL`: Redis connection for caching (optional)
- `SECRET_KEY`: Application secret key for security

### Testing Strategy
- Unit tests for individual components
- Integration tests for API endpoints
- Mock Yahoo API responses for consistent testing
- Frontend component testing with Jest/React Testing Library