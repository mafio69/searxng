# HANDOFF.md — audyt 2026-10-17

Aktualizacja: 2026-10-19.

- Wykonano zadania z planu wydania `docs/release-1.0.0-plan.md`:
  - Domknięto i scalono `chore/secret-scan-and-s1-s5`: skaner śledzonych plików `scripts/check_tracked_files.py` włączony do `scripts/check_project.py`, usunięcie `searxng.geany` ze śledzenia i testy w `tests/test_checks.py`.
  - `D1–D8` (`docs/release-1.0.0-docs`): ujednolicono dokumentację w `docs/INSTRUKCJA.md`, `docs/MCP-USAGE.md`, `README.md` oraz wersję `0.1.0` w `web/package.json` i `web/package-lock.json` (do czasu wydania `1.0.0`).
  - `O1` (`perf/shared-httpx-client`): współdzielony `httpx.AsyncClient` na proces w `mcp/server.py` z zamykaniem w `lifespan` aplikacji (`mcp/web_app.py`) i testami w `tests/test_concurrency.py` oraz `tests/test_web_app.py`.
  - `O2–O5` (`perf/searxng-and-compose-hardening`): jawne timeouty wychodzące SearXNG (`3.0` / `8.0` s), zawieszenie `SearxEngineTooManyRequests: 600` w `searxng-settings.example.yml`, `healthcheck` (`/healthz`) z `condition: service_healthy` oraz rotacja logów `json-file` w `docker-compose.yml`.
  - `W3` (`chore/w3-headers-and-release-status`): nagłówki `X-Content-Type-Options: nosniff` i `Referrer-Policy: no-referrer` dla odpowiedzi UI w `mcp/web_app.py`.
  - Poprawki review PR #2 (`fix/pr2-review-comments`): skanowanie zawartości indeksu Git (`git show :<path>`) oraz pełna walidacja pustego przypisania w szablonach `.env*` w `scripts/check_tracked_files.py`, nieprzekazywany przy przekierowaniach nagłówek `Authorization` (`add_unredirected_header`) w `scripts/smoke_test.py` oraz nieczuły na wielkość liter schemat `Bearer` (z zachowaniem stałoczasowego, czułego na wielkość liter porównania tokenu) w `mcp/access.py`.
  - Domena i tytuł UI (`chore/szukaj-dom-branding-and-docs`): tytuł `<title>szukaj.dom</title>` w `web/index.html`, oznaczenie marki `szukaj.dom` w `web/src/App.jsx` oraz ujednolicenie nazwy domeny `szukaj.dom` w `REPO.md`, `STATUS.md` i `HANDOFF.md`.
  - `R2` (S1): operator skonfigurował nowy `SEARXNG_SECRET` w lokalnym `.env` i potwierdził start kontenera `mcp-search`.
- Kontrole: `python3 scripts/check_project.py` (Ruff, tracked-files, backend 53/53, frontend 18/18, build, diff, staged-diff) — wszystkie PASS.
- Lokalne pliki polityki (`opencode.json`, `.opencode/`, `.mcp.json`) pozostawiono nietknięte poza commitami zgodnie z `AGENTS.md`.

- Dokumentacja integracji K4: docs/instrukcja-integracji-mcp-search.md jest punktem startowym dla agenta aplikacji. Zawiera ustalone adresy HTTP host/Docker, sesję MCP, przykład klienta 1.30.0, trzy stany i testy całej pętli model–narzędzie–UI. Domena `szukaj.dom` działa dla strony WWW; dla MCP obowiązują stałe adresy HTTP. Bez nowych zależności, rzeczywistych wyszukiwań i zmian drugiego repozytorium.
- Weryfikacja instrukcji: składnia przykładu Pythona, JSON zgodny ze wspólnymi fixtures i odsyłacze lokalne PASS. Dokładny przykład uruchomiono na lokalnym działającym MCP bez --live: initialize/tools/list PASS, protocol 2025-11-25. Nie wykonano rzeczywistego wyszukiwania ani odbioru z WirralAI.

- Q3 zakończone w kodzie: rozdzielone importy, nazwane walidatory w Python/JS. Ruff 0.17.1 jest przypięty w requirements-dev.txt, zainstalowany wyłącznie w ignorowanym .local/tools/ruff i włączony do python3 scripts/check_project.py.
- Mariusz zatwierdził instalację Ruff, stałe kontrole przed commitem i allow używania przez agentów. Zapis w AGENTS.md, bez zmiany opencode ani konfiguracji uprawnień. Domyślnie bez --fix; chronione ścieżki wykluczone.
- Raport dla WirralAI: docs/contract/MCP-COMPATIBILITY.md. Biblioteka MCP 1.30.0; wszystkie cztery wersje initialize i trzy syntetyczne stany narzędzia potwierdzone testami pełnego transportu MCP.
- Etapy kodu wykonane: S1–S5, K1–K4, Q1–Q3, D1–D8, O1–O5, W3.
- S1 (R2): nowy `SEARXNG_SECRET` ustawiony przez operatora, start potwierdzony. Stary klucz pozostaje w historii Git; nie używać go. Nie czytano ani nie zmieniano rzeczywistego .env i wartości sekretów.
- S5: runtime UID/build niepotwierdzone — brak dostępu do docker.sock. Obraz deklaruje UID 10001:10001; SearXNG ma stały digest. Nie uruchamiano sudo ani wdrożenia.
- K1/K4: klient WirralAI musi wykonać własne testy wspólnego docs/contract/web_search.example.json; nie zmieniano drugiego repozytorium.
- Warunek stabilnego wydania 1.0.0 ustalony przez Mariusza: wymagana jest pozytywna opinia projektu WirralAI po teście integracji MCP. Status: oczekujemy. Zielone testy searxng nie zastępują tej akceptacji; pozostałe kontrole wdrożenia nadal obowiązują.
- Q1: licznik Perplexity jest atomowy tylko w jednym procesie, nietrwały; restart zeruje limit.
- Lokalny dawny searxng-settings.yml pozostaje ignorowany, bez odczytu i modyfikacji. Diagnostyka HTTP w .local/tmp/http/. Nie czytać .local/secret/.
