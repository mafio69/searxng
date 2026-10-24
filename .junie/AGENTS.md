# AGENTS.md — Developer & Agent Guide for `szukaj`

This document provides project-specific technical details, architecture overview, build/configuration instructions, testing procedures, and development conventions for advanced developers and autonomous agents working on `szukaj`.

---

## 1. Project Architecture & Component Overview

`szukaj` is a private search gateway combining a SearXNG meta-search backend, an MCP (Model Context Protocol) streamable HTTP service, and a lightweight React web UI.

### Key Directory Layout
- **`mcp/`**: Python backend application (FastAPI / Starlette + MCP SDK).
  - `server.py`: Core search coordinator, MCP tool registration (`web_search`), SearXNG client (`_searxng`), Perplexity fallback (`_perplexity`), and shared `httpx.AsyncClient`.
  - `web_app.py`: Starlette application assembling the MCP endpoints, JSON API (`/api/search`), health probe (`/healthz`), security middlewares (Host header check, Origin/Sec-Fetch-Site validation), and static SPA serving (`web/dist`).
  - `access.py`: Token authentication validation (constant-time token comparison).
  - `app_logging.py`: Logging configuration with `CompressedRotatingFileHandler` writing compressed logs to `.local/logs/szukaj.log`.
- **`web/`**: Frontend React SPA (React 19, Vite, Tailwind CSS, Lucide icons, Vitest).
- **`scripts/`**: Verification and smoke test tooling.
  - `check_project.py`: Complete offline pre-commit verification gate.
  - `check_tracked_files.py`: Git tracking and secret scanner enforcing security invariants on files and index.
  - `smoke_test.py`: End-to-end HTTP/SSE smoke test runner.
- **`tests/`**: Python unittest suite testing MCP contracts, concurrency, error states, and web endpoints.
- **`.local/`**: Ignored repository-local storage for dependencies, cache, temporary files, and logs. **Never use system `/tmp`**.

---

## 2. Build & Configuration Instructions

### Prerequisites & Dependencies
- **Python Runtime**: Python 3.12+ (local project dependencies reside in `.local/python`, Ruff linter in `.local/tools/ruff`).
- **Node.js**: Node.js 20+ with npm for building the web frontend.
- **Docker & Compose**: For running containerized SearXNG and MCP service.

### Environment Configuration
Copy the template to create `.env` (kept strictly local and uncommitted):
```bash
cp .env.example .env
```
Key configuration parameters:
- `SEARXNG_URL`: HTTP URL of the internal SearXNG instance (default: `http://localhost:8080` or `http://szukaj:8080` in Compose).
- `SEARXNG_SECRET`: Random 32+ character hex string for SearXNG session encryption.
- `SEARCH_ALLOWED_HOSTS`: Comma-separated list of allowed HTTP `Host` header values (e.g. `localhost, 127.0.0.1, szukaj.dom, mcp-search`).
- `SEARCH_AUTH_TOKEN`: Optional Bearer token for securing `/mcp` and `/api/search`.
- `PERPLEXITY_API_KEY`: Optional fallback API key.
- `PERPLEXITY_DAILY_LIMIT`: Maximum daily fallback queries (default: `100`).
- `APP_ENV`: `prod` (masks internal errors) or `dev` (includes technical error details).
- `LOG_LEVEL`: Logging verbosity (default: `WARNING`; can be set to `INFO` or `DEBUG`).

### Frontend Build
The static build must be generated in `web/dist` so `mcp/web_app.py` can serve it:
```bash
npm --prefix web install
npm --prefix web run build
```

### Docker Service Execution
```bash
docker compose up -d
```
Services defined in `docker-compose.yml`:
- `szukaj`: SearXNG meta-search container (runs unprivileged UID `10001:10001`, port `8080`).
- `mcp-search`: MCP server + Web UI container (port `8890` mapped to container `8000`).

---

## 3. Testing Information & Guidelines

### 3.1 Pre-Commit Offline Quality Gate (`scripts/check_project.py`)
Before any commit, run the mandatory offline verification suite:
```bash
python3 scripts/check_project.py
```
This script executes in sequence:
1. **Ruff linting**: `ruff check --config ruff.toml mcp scripts tests`
2. **Tracked files scanner**: `scripts/check_tracked_files.py` (detects untracked secrets, forbidden files, `.env` leaks, and credential patterns)
3. **Backend tests**: Python `unittest` suite across `tests/`
4. **Frontend tests**: Vitest suite in `web/`
5. **Frontend build**: Vite production build (`web/dist`)
6. **Git diff checks**: `git diff --check` and `git diff --cached --check`

### 3.2 Running Backend Tests
Because local Python dependencies reside in `.local/`, set `PYTHONPATH` when running tests manually:

- **Run all backend tests**:
  ```bash
  PYTHONPATH=.local/tools/ruff:.local/python python3 -m unittest discover -s tests -v
  ```
- **Run a single test module**:
  ```bash
  PYTHONPATH=.local/tools/ruff:.local/python python3 -m unittest tests/test_search_status.py -v
  ```
- **Run a specific test case / method**:
  ```bash
  PYTHONPATH=.local/tools/ruff:.local/python python3 -m unittest tests.test_search_status.SearchStatusTests.test_successfully_empty_with_disabled_fallback -v
  ```

### 3.3 Running Frontend Tests
Frontend tests use Vitest and React Testing Library:
- **Run all frontend tests**:
  ```bash
  npm --prefix web test
  ```
- **Run in watch mode**:
  ```bash
  npm --prefix web run test:watch
  ```

### 3.4 Adding New Tests

#### Backend Test Guidelines:
1. Place new test files in `tests/test_<name>.py`.
2. Inherit from `unittest.TestCase` or `unittest.IsolatedAsyncioTestCase` (for async code).
3. Always isolate external services using `unittest.mock.patch` on `server._searxng` and `server._perplexity`.
4. Keep temporary directories within `.local/tmp/` (e.g. `Path(__file__).resolve().parents[1] / ".local" / "tmp"`).
5. **Important**: Never use credential patterns in test literals (e.g., avoid literal string keys matching `*_PASSWORD=`, `*_SECRET=`, `*_TOKEN=`, `*_API_KEY=`) as they will trigger `scripts/check_tracked_files.py`.

#### Example Backend Test Structure:
```python
import unittest
from unittest.mock import patch, AsyncMock
import server

class ExampleSearchTest(unittest.IsolatedAsyncioTestCase):
    @patch.object(server, "_searxng", new_callable=AsyncMock)
    async def test_searxng_invocation(self, mock_searxng):
        mock_searxng.return_value = [{"title": "Example", "url": "https://example.com", "snippet": "Test"}]
        result = await server.web_search("sample query")
        self.assertIn("Example", result)
        mock_searxng.assert_awaited_once_with("sample query", 5)
```

#### Frontend Test Guidelines:
1. Create or update test files under `web/src/*.test.jsx`.
2. Mock `fetch` / API calls using `vi.stubGlobal("fetch", ...)` or `vi.fn()`.
3. Use `@testing-library/react` utilities (`render`, `screen`, `fireEvent`, `waitFor`).

---

## 4. Development & Code Conventions

### Code Style & Linters
- **Python**: Formatted and linted with Ruff. Configuration is in `ruff.toml` (target Python 3.12+, max line length 120 chars, rules: `E`, `F`, `W`, `I`, `UP`, `B`, `SIM`).
  - Run linter directly: `PYTHONPATH=.local/tools/ruff python3 -m ruff check --config ruff.toml mcp scripts tests`
- **JavaScript/React**: Linted with ESLint (`web/eslint.config.js`).

### Security & Repository Isolation Invariants
- **Local Directory Isolation**: Always use `.local/` (`.local/tmp`, `.local/logs`, `.local/cache`) for transient data. Never use `/tmp` or other system paths.
- **Secret Protection**: Never commit or display real secret values. `.env` and `.local/secret/` must remain untouched and uncommitted.
- **Host & Origin Validation**: `mcp/web_app.py` enforces strict `Host` header checks against `SEARCH_ALLOWED_HOSTS` and rejects untrusted `Origin` and cross-site `Sec-Fetch-Site` requests on `/api/search`.
- **MCP Protocol Conformance**: MCP endpoints support JSON-RPC over Streamable HTTP/SSE with protocol versions `2024-11-05` to `2025-11-25`.
