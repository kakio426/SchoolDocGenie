# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-30

### Added
- **Phase 1: Project Foundation**
  - FastAPI backend with CORS configuration
  - Next.js 15 frontend with TypeScript and TailwindCSS
  - Gemini 3.0 Flash integration
  - Loguru logging system
  - Health check endpoint

- **Phase 2: Client-side Privacy Masking**
  - Regex-based PII masking (주민번호, 전화번호, 이메일, 이름)
  - Whitelist functionality for excluded terms
  - Performance optimization (1.2MB text in <1s)
  - 8 unit tests with 100% pass rate

- **Phase 3: Document Converter**
  - HWP parser using pyhwpx
  - Excel parser using pandas with Markdown conversion
  - File upload API endpoint (`/upload`)
  - Windows file lock issue resolution
  - Automatic temp file cleanup

- **Phase 4: AI Analysis & Caching**
  - Gemini 3.0 Flash document analysis
  - Structured JSON output (summary, keywords, action_items)
  - Local LRU caching to prevent duplicate API calls
  - Error handling and JSON parsing stabilization

- **Phase 5: RAG & Archiving**
  - Supabase client integration
  - Google Text Embedding API (text-embedding-004)
  - Document storage and vector search functionality
  - 11 backend tests with 100% pass rate

### Technical Details
- **Backend**: FastAPI, Python 3.10+, pytest
- **Frontend**: Next.js 15, TypeScript, Jest
- **AI**: Google Gemini 3.0 Flash, Text Embedding 004
- **Database**: Supabase (PostgreSQL + pgvector)
- **Testing**: 19 tests total (11 backend + 8 frontend)

### Documentation
- Comprehensive README.md
- Detailed implementation plan (PLAN_School-Doc_Genie.md)
- Environment variable examples (.env.example)

[0.1.0]: https://github.com/yourusername/School-Doc-Genie/releases/tag/v0.1.0
