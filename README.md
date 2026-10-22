# szukaj (`szukaj.dom`) — Your Search Engine, Also for AI

[![English](https://img.shields.io/badge/lang-English-blue.svg)](#)
[![Polski](https://img.shields.io/badge/język-Polski-red.svg)](README_PL.md)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=111827)
![MCP 1.30.0](https://img.shields.io/badge/MCP-Streamable%20HTTP%20(1.30.0)-0F766E)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

> **The vast internet. Your questions. A single access point for you and your AI agents.**
>
> 🇵🇱 *Polska wersja dokumentacji jest dostępna w pliku [README_PL.md](README_PL.md).*

**`szukaj`** (`https://github.com/mafio69/szukaj`, accessible in the local home network as **`http://szukaj.dom/`**) combines the private meta-search engine **SearXNG**, a polished web browser UI built with React, and a **Model Context Protocol (MCP)** server. You can use the search engine directly in your browser or attach the `web_search` tool to your AI agents and applications. When SearXNG returns empty results or an error, the server automatically attempts an optional fallback source — **Perplexity Search API**.

---

## Key Features

| Area | What You Get |
|---|---|
| **Search Engine for Humans (`szukaj.dom`)** | Clean React 19 web interface displaying result titles, domains, and snippets, customizable `5` or `10` results, keyboard navigation, and the `Ctrl/Cmd + K` shortcut. |
| **History Under Your Control** | Up to 30 recent queries stored strictly in browser `localStorage`, removal of individual entries or complete clearing, and a *Do not save history* mode. |
| **Search for AI (MCP)** | `web_search` tool over **MCP Streamable HTTP** (`/mcp`) supporting protocol version negotiation (`2024-11-05` to `2025-11-25`) and optional `Bearer` token authentication. |
| **Unified Engine & Managed Fallback** | UI and MCP share the same asynchronous engine (`httpx.AsyncClient` with connection pooling): **SearXNG** first, and upon empty/failed results, optional **Perplexity** fallback with atomic daily rate limiting. |
| **Ready-to-use Docker Compose Stack** | Two container services (`searxng` with `/healthz` healthchecks and unprivileged `mcp-search` running as `UID 10001:10001`) with log rotation; image builds frontend automatically without requiring local Node.js or Python. |

> [!NOTE]
> Perplexity is not required for search functionality via SearXNG — without an API key, fallback remains disabled. The *Do not save history* toggle applies only to browser local storage; the query itself is still sent to the backend and search providers.

---

## Architecture & Query Flow

```text
Browser (szukaj.dom)     ──► POST /api/search ──┐
                                                 ├──► web_search (async) ──► SearXNG (JSON, timeout 10 s)
AI Client / Backend      ──► POST /mcp ─────────┘                                │
                              (Streamable HTTP)                         empty or HTTP error
                                                                                  ▼
                                                                   Perplexity Search API (optional,
                                                                   in-memory daily limit, timeout 20 s)
```

The server returns structured search results (`title`, `url`, `snippet` up to 400 characters) and a distinct status (`ok`, `empty`, `error`). It does not scrape full webpage contents or generate LLM answers.

---

## Quick Start (Docker Compose)

Prerequisites: Docker with Compose plugin, Internet access, and an available host port (default: `8890`). Run all commands from the root directory of the cloned `szukaj` repository.

### 1. Prepare Environment Configuration (`.env`)

Copy the template `.env.example` to `.env` and generate your own local `SEARXNG_SECRET` key (e.g. `openssl rand -hex 32`). Other empty variables will assume their defaults. **Never commit a real `.env` file to Git.**

| Variable | Default Behavior / Usage |
|---|---|
| `SEARXNG_SECRET` | Required random SearXNG session key, set only locally; Compose will fail to start without it |
| `MCP_AUTH_TOKEN` | Optional Bearer secret for all `/mcp` requests (the `Bearer` scheme is case-insensitive, token comparison is constant-time); configure only locally |
| `PPLX_API_KEY` | Optional Perplexity API key; without it fallback is disabled |
| `PPLX_DAILY_LIMIT` | Default `50`; maximum daily Perplexity requests reserved atomically per process |
| `SEARXNG_LANG` | Default `auto`; search language passed to SearXNG |
| `SEARCH_ALLOWED_HOSTS` | Comma-separated list of trusted host headers; default `127.0.0.1,localhost,mcp-search`. For a custom domain append e.g. `szukaj.dom`. Do not use `*`. |
| `SEARCH_PORT` | Default `8890`; published host port |
| `SEARCH_BIND_ADDRESS` | Default `127.0.0.1`; listening bind address on host |
| `SEARXNG_URL` | Default `http://searxng:8080`; internal URL to SearXNG service inside Docker network |
| `MCP_HOST` | Default `0.0.0.0`; listening address inside the container |
| `MCP_PORT` | Default `8000`; listening port inside the container |
| `APP_ENV` | Default `prod` (user-friendly error messages without internal stack traces); set to `dev` to display diagnostic technical details |
| `LOG_LEVEL` | Default `WARNING` (logs warnings, errors and critical events); set `INFO` or `DEBUG` for verbose diagnostic logs |
| `LOG_FILE` | Default `.local/logs/szukaj.log`; application log file path |
| `LOG_MAX_BYTES` | Default `5242880` (`5 MB`); maximum single log file size before rotation |
| `LOG_BACKUP_COUNT` | Default `5`; number of compressed `.gz` log backup archives preserved (`szukaj.log.1.gz` … `szukaj.log.5.gz`) |

SearXNG mounts the public read-only template `searxng-settings.example.yml` (with an empty `server.secret_key` and configured timeouts `3.0` / `8.0` s); the active secret key is injected exclusively via the `SEARXNG_SECRET` environment variable.

### 2. Create Network and Start Containers

Services communicate over an external Docker bridge network named `ai`. Create it once:

```bash
docker network create ai
```

Build and launch the stack:

```bash
docker compose up -d --build
docker compose ps
```

Open **`http://127.0.0.1:8890/`** (or **`http://szukaj.dom/`** if you configured local DNS / reverse proxy and added `szukaj.dom` to `SEARCH_ALLOWED_HOSTS`). The `mcp-search` container starts automatically once `searxng` passes its `/healthz` healthcheck.

---

## Connecting AI Agents (MCP Streamable HTTP)

In your client supporting **MCP Streamable HTTP**, configure the appropriate endpoint URL:

| MCP Client Location | MCP Endpoint |
|---|---|
| On the same host as Docker | `http://127.0.0.1:8890/mcp` |
| Inside a container connected to Docker network `ai` | `http://mcp-search:8000/mcp` |

If `MCP_AUTH_TOKEN` is set, the client must include the header `Authorization: Bearer <token>` on all `/mcp` requests (initialization, event stream, tool execution, session teardown).

### `web_search` Tool Signature & Response

```text
web_search(query: string, max_results: integer = 5)
```

Example tool call:

```json
{"query": "how meta search engine works", "max_results": 3}
```

The tool accepts `query` (`1–1000` Unicode characters) and `max_results` (`1–10`), returning a JSON text response:
- `status`: `"ok"` | `"empty"` | `"error"`
- `source`: `"searxng"` | `"perplexity-fast"` | `null`
- `results`: list of objects `{"title", "url", "snippet"}`
- `errors`: list of controlled provider error codes (no raw stack traces or internal secrets leaked)

For in-depth agent integration guides, see **[docs/instrukcja-integracji-mcp-search.md](docs/instrukcja-integracji-mcp-search.md)** and **[docs/MCP-USAGE.md](docs/MCP-USAGE.md)**.

---

## Browser HTTP Endpoint (`POST /api/search`)

The web frontend interacts with the backend engine via `POST /api/search`:

```bash
curl http://127.0.0.1:8890/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"SearXNG meta search","max_results":5}'
```

- Accepts JSON body (up to `4096` bytes) with non-empty `query` (`1–500` characters) and `max_results` (`1–10`).
- Returns `status` (`ok` / `empty`), `source`, and `results`.
- Enforces Host header validation (`TrustedHostMiddleware`) and blocks untrusted cross-site requests (`Origin` / `Sec-Fetch-Site`).
- On search provider failures, returns controlled `HTTP 502 Bad Gateway` without exposing internal implementation details.

---

## Deployment Smoke Test

After running containers, verify the entire stack (UI assets, security headers, API validation, and MCP initialization/tool discovery) without consuming search provider credits:

```bash
python3 scripts/smoke_test.py
# or for a custom local domain / port:
python3 scripts/smoke_test.py --url http://szukaj.dom
```

To run a live end-to-end search verification, pass the `--query` option (may trigger paid Perplexity fallback if SearXNG yields no results):

```bash
python3 scripts/smoke_test.py --url http://szukaj.dom --query "SearXNG documentation"
```

---

## Troubleshooting

| Symptom | What to Check |
|---|---|
| Compose complains about missing network `ai` | Run `docker network create ai` before starting services |
| Compose complains about missing `.env` or `SEARXNG_SECRET` | Create `.env` from `.env.example` and set a non-empty `SEARXNG_SECRET` |
| `400 Invalid host header` on custom domain | Add your domain (e.g. `szukaj.dom`) to `SEARCH_ALLOWED_HOSTS` in `.env` and restart `mcp-search` |
| Client container cannot connect to MCP | Attach client container to network `ai` and use `http://mcp-search:8000/mcp` instead of `127.0.0.1` |
| No search results | Check logs (`docker compose logs --tail=50 searxng mcp-search`) and verify `searxng` internet access |

---

## For Developers

- **Backend:** Python 3.12, FastMCP v1 (`mcp==1.30.0`), HTTPX (`AsyncClient`), Starlette, Uvicorn.
- **Frontend:** React 19, Vite 7, Vitest + Testing Library (locally Node.js `>=22.12`, Docker build uses Node.js 24).

| Path | Responsibility |
|---|---|
| `mcp/server.py` | FastMCP `web_search` tool, shared `httpx.AsyncClient`, search providers, and atomic Perplexity rate limit |
| `mcp/web_app.py` | ASGI application (Starlette), `POST /api/search`, static UI serving, security middleware, and `lifespan` |
| `mcp/access.py` | `Bearer` token authorization middleware for `/mcp` |
| `web/src/` | React frontend (`szukaj.dom`), `localStorage` history, and search API client |
| `scripts/check_project.py` | Mandatory pre-commit quality gate |
| `scripts/check_tracked_files.py` | Git working tree & index scanner detecting untracked secrets and non-empty `.env*` templates |
| `scripts/smoke_test.py` | Dependency-free deployment smoke tester |
| `tests/` & `web/src/App.test.jsx` | Unit and integration test suites for backend (55) and frontend (19) |

### Pre-Commit Quality Checks

One-time local installation of pinned Ruff linter into ignored `.local/`:

```bash
mkdir -p .local/tmp/pip
TMPDIR="$PWD/.local/tmp/pip" python3 -m pip install --only-binary=:all: --no-deps --target .local/tools/ruff --cache-dir .local/cache/pip -r requirements-dev.txt
```

Before every commit, execute the full offline quality gate:

```bash
python3 scripts/check_project.py
```

The script runs in sequence:
1. `ruff` — Python linting (`mcp`, `scripts`, `tests`),
2. `tracked-files` — Git repository and index secret scanner,
3. `backend` — 55 offline Python unit/integration tests,
4. `frontend` — 19 React component tests (Vitest),
5. `build` — Vite production build,
6. `diff` and `staged-diff` — Git whitespace and formatting checks (`git diff --check`).

---

## Project Documentation

- **[Agent MCP Integration Guide](docs/instrukcja-integracji-mcp-search.md)** — Starting point for client integrations, HTTP endpoints, MCP sessions, and acceptance testing.
- **[MCP for AI & Integrators](docs/MCP-USAGE.md)** — Full specification of `web_search` tool contract, error codes, and protocol negotiation.
- **[MCP Compatibility Report](docs/contract/MCP-COMPATIBILITY.md)** — Protocol verification report against shared JSON fixtures.
- **[Daily Operations Guide](docs/INSTRUKCJA.md)** — Docker Compose commands and MCP client configurations.
- **[Technical Architecture Map](REPO.md)**, **[Project Status](STATUS.md)**, and **[Changelog](CHANGELOG.md)**.
- **[AI Agent Rules](AGENTS.md)**, **[Git Flow Rules](GIT-FLOW.md)**, and **[Session Handoff](HANDOFF.md)**.
- **[Polska dokumentacja (Polish README)](README_PL.md)**.

## Version & Release Status

The latest tagged release is `0.1.0` (in-progress changes are recorded in the `[Unreleased]` section of [CHANGELOG.md](CHANGELOG.md)). Tagging stable `1.0.0` requires explicit confirmation of MCP integration tests by the client application WirralAI and verification of all operational checklist items in [STATUS.md](STATUS.md).
