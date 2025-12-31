## [v0.7.0] - 2025-12-31 "The Power Up Update"
### Added
- **Local AI support (Ollama)**: Integrated Ollama for local document analysis with automatic `exaone3.5:2.4b` model sanitization.
- **Gemini 3.0 Flash Integration**: Fully stabilized Gemini 3.0 Flash engine as the primary analysis provider.
- **Poppler Auto-Detection**: Implemented automatic search for Poppler bin paths to enable PDF OCR without manual configuration.
- **Smart ICS Export**: Added date-matching logic for schedule extraction and a "One-Click" Google Calendar import workflow (Open URL + Open Folder).
- **History Deletion**: Added a delete button (X) to the analysis archive to manage and remove past records.
- **Settings UI Revamp**: Dynamic engine switching with clean layout and API Key management.

### Fixed
- **Startup UX**: Resolved window flickering by deferring deiconify until UI construction is complete.
- **Threading Stability**: Applied thread-safe UI updates to prevent "Not Responding" errors during heavy analysis.
- **Ollama Error Handling**: Added explicit error reporting for missing models and backend connection failures.

## [0.2.0] - 2025-12-30

### Added
- **Phase 6: Enhanced Client-side Masking**
  - Robust masking for text files on the client side
- **Phase 7: AI Analysis Backend Integration**
  - Metadata extraction using Gemini (Title, Date, Doc Number)
  - Unified `/analyze` endpoint with automatic conversion
- **Phase 8: AI Analysis Result UI**
  - Stunning UI for displaying AI analysis results
  - Keywords, Summary, and Action items visualization
- **Phase 9: Supabase Document Storage**
  - Automatic archiving of analyzed documents to Supabase
  - Vector embedding storage for RAG support
- **Phase 10: Search and Reference Copy**
  - Full-text and similarity search for documents
  - "Copy Reference" feature for administrative efficiency

## [v0.6.0] - 2025-12-31
### Added
- **Intelligent Analysis Engine**: Enhanced Gemini prompt for logical reasoning and complex table parsing.
- **Interactive Chat (Q&A)**: Added "Chat with Document" feature in the Detail View for natural language queries.
- **Multi-Document Comparison**: Implemented side-by-side comparison of two documents to identify changes (e.g., Year-over-Year differences).
- **Startup Optimization**: Applied lazy loading for heavy libraries (`pandas`, `pyhwpx`) to significantly speed up agent launch.
- **Enhanced Privacy Masking**: Restored and improved name, phone, and email masking patterns.

### Changed
- **UI UX**: Renamed "Server Transfer" button to "AI Analysis Start" to better reflect the action.
- **Terms of Service**: Updated disclaimer to clarify BYOK model and local/stateless data handling.
- **Version**: Bumped version to `v0.6.0 Intelligent Hybrid`.

### Changed
- Improved HWP conversion using HTML intermediary for better table support
- Updated Gemini model to `gemini-3-flash-preview` for latest performance
- Enhanced backend logging and error handling

---

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
