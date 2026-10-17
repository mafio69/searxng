# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Porządki Git — 2026-10-17
- Uaktualniono HANDOFF i STATUS po lokalnym scaleniu całego search-ui i dokumentu audytu do develop.
- Zachowano diagnostykę HTTP w ignorowanym katalogu lokalnym; nie jest częścią publikacji.
- Zapisano oczekiwanie na zgodę na push develop oraz warunek usuwania lokalnych gałęzi dopiero po udanym pushu.

### Dokumentacja narzędzi — 2026-10-17
- Usunięto odniesienia do nieużywanego narzędzia środowiskowego i ujednolicono odwołania do bezpośrednich poleceń testów w README oraz REPO.
- Zachowano wymóg zgody na Bash oraz zakazy odczytu i publikowania sekretów.

### Zamknięcie sesji — 2026-10-17
- Poprawki review wysłano na GitHub w commicie `d5336b6` (PR #1); bez merge i wdrożenia.
- Zapisano ostateczną decyzję o zachowaniu obecnego wyglądu i świadomym nieprzyjęciu uwagi o kontraście.
- Potwierdzono rzeczywiste wyszukiwanie MCP z hosta przez SearXNG; problem DNS klienta VirralAI w kontenerze pozostaje do zdiagnozowania.

### Poprawki code review — 2026-10-17
- Ochrona Host niezależną listą `SEARCH_ALLOWED_HOSTS`; test odrzucenia zgodnych, ale obcych nagłówków Host/Origin i zachowania dostępu Docker.
- Usunięto awarię renderowania wyniku z adresem `https://www./`.
- Poprawiono fokus mobilnej historii: wejście do panelu, Tab/Shift+Tab, Escape, powrót do przycisku lub wyszukiwarki. Zamknięty panel wyłączono z interakcji i drzewa dostępności.
- Zachowano wygląd na polecenie Mariusza; uwaga review o kontraście nie jest realizowana.
- Kontrole: backend 20/20, frontend 17/17, build i smoke nowego kodu — PASS.

### MVP 1.0 stabilization — 2026-10-16
- Preserved valid history entries when storage contains null items.
- Rejected malformed search responses with controlled API/UI errors instead of crashes.
- Corrected the missing-frontend help reference to README.
- Verified 17 backend tests, 13 frontend tests, production frontend build and the running deployment smoke test. Latest fixes still require rebuilding the Docker image.

### Added
- Dependency-free Python deployment smoke test for frontend assets, API validation and MCP initialization/tool discovery, with optional live search.
- Backend tests for provider limits, daily reset, failed HTTP requests, fallback and the smoke flow; isolated MCP instances between tests.

### Fixed
- Added the missing `web/package-lock.json` required by the Docker frontend build and `npm ci`. Verified npm ci, all 7 frontend tests, and the production frontend build.

## [0.1.0] - 2026-10-16

### Added
- **MCP Search Server**: Python FastMCP server (`mcp/server.py`) providing the `web_search` tool with SearXNG querying and fallback to Perplexity API ([7b00209](https://github.com/mafio69/searxng/commit/7b00209d03ff680ab7bb48f857f290297b08b065)).
- **Docker Compose Stack**: Containerized deployment (`docker-compose.yml`) containing SearXNG and MCP search services attached to the external `ai` network ([7b00209](https://github.com/mafio69/searxng/commit/7b00209d03ff680ab7bb48f857f290297b08b065)).
- **SearXNG Engine Settings**: Configuration (`searxng-settings.yml`) with JSON API response format enabled and rate limiter disabled ([7b00209](https://github.com/mafio69/searxng/commit/7b00209d03ff680ab7bb48f857f290297b08b065)).
- **Project Documentation & AI Policies**: Core documentation (`README.md`, `REPO.md`, `docs/INSTRUKCJA.md`), environment configuration template (`.env.example`), AI agent policies (`AGENTS.md`, `GIT-FLOW.md`), and session tracking templates (`STATUS.md`, `HANDOFF.md`) ([7b00209](https://github.com/mafio69/searxng/commit/7b00209d03ff680ab7bb48f857f290297b08b065)).

[0.1.0]: https://github.com/mafio69/searxng/releases/tag/v0.1.0
