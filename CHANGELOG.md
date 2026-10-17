# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### K1 — Jednoznaczny wynik pusty i awaria — 2026-10-18
- Dodano status ok/empty/error. Poprawny brak wyników ma source null, results [] i errors []; awaria bez wyników zawsze error. Udany fallback ma ok bez errors. API oddaje 502 przy awarii. Dokumentacja zawiera nowe stany i negocjację protokołu.
- Walidacja: backend 36/36, frontend 17/17, build i diff-check PASS.

### S4 — Bezpieczne kody błędów dostawców — 2026-10-18
- Odpowiedź MCP zwraca kontrolowane kody timeout/http_error/error i lokalne no_key/limit. Testy podkładają wyjątki z prywatnym tekstem i sprawdzają brak ich treści w odpowiedzi.
- Walidacja: backend 33/33, frontend 17/17, build i diff-check PASS.

### K3 — Przypięcie MCP i negocjacja protokołu — 2026-10-18
- Biblioteka mcp==1.30.0 w mcp/requirements.txt. Test rzeczywistego initialize potwierdza wszystkie cztery wersje akceptowane przez WirralAI; nieznana wersja negocjuje 2025-11-25.
- Walidacja: backend 32/32, frontend 17/17, build i diff-check PASS.

### S3 — Opcjonalna kontrola dostępu MCP — 2026-10-18
- MCP_AUTH_TOKEN chroni /mcp i jego metody GET/POST/DELETE stałoczasowym porównaniem nagłówka Bearer. Dotyczy pełnej aplikacji i osobnego entrypointu MCP. Brak konfiguracji zachowuje poprzednie działanie; przeglądarkowe API i statyczne UI nie otrzymują ani nie wymagają tego sekretu. Smoke potrafi przekazać wartość z własnego środowiska wyłącznie do MCP.
- Walidacja: backend 30/30, frontend 17/17, build i diff-check PASS.

### Q1 — Atomowy limit prób Perplexity — 2026-10-18
- Limit jest rezerwowany pod krótką blokadą przed żądaniem HTTP. Nie zwracamy rezerwacji po błędzie ani anulowaniu, bo koszt po stronie dostawcy może już powstać. Test 100 równoległych prób przy limicie 50 potwierdza dokładnie 50 żądań. Licznik nadal jest lokalny dla procesu i resetuje się po restarcie; nie deklarujemy trwałego budżetu.
- Walidacja: backend 25/25, frontend 17/17, build i diff-check PASS.

### S2 — Asynchroniczne wyszukiwanie — 2026-10-18
- web_search i obaj dostawcy używają async/await oraz httpx.AsyncClient. Adapter API oczekuje na tę samą asynchroniczną usługę. Test sprawdza dwa opóźnienia po 1 s, wspólny czas poniżej 1,5 s oraz możliwość uruchomienia obu żądań przed ich zakończeniem.
- Walidacja: backend 23/23, frontend 17/17, build i diff-check PASS.

### S1 — Oddzielenie klucza od wersjonowanej konfiguracji — 2026-10-18
- Compose montuje pusty publiczny szablon i wymaga lokalnego SEARXNG_SECRET. Dawny plik usunięto wyłącznie ze śledzenia, bez odczytu i zmiany lokalnej wartości. Rotacja klucza i rzeczywisty start pozostają do potwierdzenia przez operatora; stara historia nie została usunięta.
- Walidacja: backend 22/22, frontend 17/17, build i diff-check PASS.

### Doprecyzowanie Git Flow — 2026-10-17
- Zapisano pełną kolejność zadania: gałąź z develop, testy i commit, lokalny merge, weryfikacja develop, oczekiwanie na zgodę, push wyłącznie develop i usunięcie lokalnej gałęzi po udanym pushu.
- Dodano obowiązek zgłaszania sprzecznych poleceń oraz omówienia uzasadnienia przed świadomym zatwierdzeniem wyjątku.
- Określono zakres fire: zgoda właściciela na pracę bezpośrednio na develop nie zastępuje zielonych testów, ochrony sekretów ani zgody na push. Bieżąca korekta otrzymała ten status od Mariusza.

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
