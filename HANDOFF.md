# HANDOFF.md — audyt 2026-10-17

Aktualizacja: 2026-10-22.

## Przypomnienie na następną sesję (propozycje dla Mariusza — przypomnieć na starcie!)

1. **Porządek pod audyty (`qodana.yaml`, `composer.json`, `.run/`)**:
   - Ustawić w `qodana.yaml` właściwy linter pod Python/JS (zamiast domyślnego `jetbrains/qodana-php:2026.2`) i wykluczyć `.local/`, `web/node_modules/`, `web/dist/`.
   - Usunąć zbędny pusty `composer.json` (chyba że ma służyć pod GrumPHP) oraz dodać `.run/` do `.gitignore`, aby lokalne konfiguracje uruchomieniowe PhpStorma nie trafiały do publicznego repozytorium.
2. **GitHub Actions CI (`.github/workflows/ci.yml`)**:
   - Lekki workflow uruchamiający `python3 scripts/check_project.py` (Ruff + skaner sekretów `check_tracked_files.py` + testy Python + testy Vitest + `vite build`) na PR do `develop` i `master` + zielona odznaka CI w `README.md`.
3. **Endpoint `GET /healthz` także dla `mcp-search`**:
   - Dodać route `/healthz` w `mcp/web_app.py` (zwracający `200 {"status": "ok"}`) oraz `healthcheck` dla usługi `mcp-search` w `docker-compose.yml` pod monitoring Dockera i Traefika.
4. **Trwały dzienny licznik Perplexity na dysku (`Q1`)**:
   - Zapisywać licznik `_pplx` (`day`, `count`) z `mcp/server.py` atomowo do małego pliku JSON w `.local/logs/` lub `.local/cache/`, aby restart kontenera `mcp-search` nie zerował dziennego limitu płatnego API.
5. **Krótki cache in-memory (`TTL 30–60 s`) dla identycznych zapytań (`W1`)**:
   - Mały słownik LRU (np. do 64 wpisów na 60 s) w `mcp/server.py`, chroniący przed duplikatami zapytań przy odświeżeniu strony lub powtórnym wywołaniu `web_search` przez agenta.
6. **Obsługa parametru `?q=...` w URL (`http://szukaj.dom/?q=hasło`)**:
   - Odczyt parametru `q` przy starcie `web/src/App.jsx`, aby można było ustawić `http://szukaj.dom/?q=%s` jako domyślną wyszukiwarkę w pasku adresu przeglądarki.

---

- Stan na zamknięcie sesji (`develop` @ `bbb1943` + aktualizacja dokumentacji):
  - Domknięto i scalono `chore/secret-scan-and-s1-s5` (`2079165`) oraz `fix/gitguardian-false-positive-test` (`6acba93` / `5bdfc9d`): skaner śledzonych plików i indeksu Git `scripts/check_tracked_files.py` (w tym wykrywanie literałów `*_PASSWORD=`, `*_SECRET=`, `*_TOKEN=`, `*_API_KEY=` w kodzie i testach), usunięcie `searxng.geany` ze śledzenia oraz wyeliminowanie false-positive GitGuardiana w `tests/test_checks.py`.
  - `D1–D8` (`docs/release-1.0.0-docs`, `b65dd2d`): ujednolicono dokumentację w `docs/INSTRUKCJA.md`, `docs/MCP-USAGE.md`, `README.md` oraz wersję `0.1.0` w `web/package.json` i `web/package-lock.json` (do czasu wydania `1.0.0`).
  - `O1` (`perf/shared-httpx-client`, `c770db6`): współdzielony `httpx.AsyncClient` na proces w `mcp/server.py` z zamykaniem w `lifespan` aplikacji (`mcp/web_app.py`) i testami w `tests/test_concurrency.py` oraz `tests/test_web_app.py`.
  - `O2–O5` (`perf/searxng-and-compose-hardening`, `af372b5`): jawne timeouty wychodzące SearXNG (`3.0` / `8.0` s), zawieszenie `SearxEngineTooManyRequests: 600` w `searxng-settings.example.yml`, `healthcheck` (`/healthz`) z `condition: service_healthy` oraz rotacja logów `json-file` w `docker-compose.yml`.
  - `W3` (`chore/w3-headers-and-release-status`, `71eac05`): nagłówki `X-Content-Type-Options: nosniff` i `Referrer-Policy: no-referrer` dla odpowiedzi UI w `mcp/web_app.py`.
  - Poprawki review PR #2 (`fix/pr2-review-comments`, `bcf3384`): skanowanie zawartości indeksu Git (`git show :<path>`) oraz pełna walidacja pustego przypisania w szablonach `.env*` w `scripts/check_tracked_files.py`, nieprzekazywany przy przekierowaniach nagłówek `Authorization` (`add_unredirected_header`) w `scripts/smoke_test.py` oraz nieczuły na wielkość liter schemat `Bearer` (z zachowaniem stałoczasowego, czułego na wielkość liter porównania tokenu) w `mcp/access.py`.
  - Domena, zmiana nazwy repozytorium/usługi na `szukaj` i nowe `README.md` (`chore/szukaj-dom-branding-and-docs` `4158dc1`, `docs/repo-rename-szukaj-and-readme` `434434a`, `da6b544`): tytuł `<title>szukaj.dom</title>` w `web/index.html`, oznaczenie marki `szukaj.dom` w `web/src/App.jsx`, nazwa pakietu `szukaj-ui` w `web/package.json`, usługa `szukaj` (`SEARXNG_URL=http://szukaj:8080`) w `docker-compose.yml`, linki `mafio69/szukaj` w `CHANGELOG.md`, przebudowane `README.md` oraz ujednolicenie nazwy w `REPO.md`, `STATUS.md` i `HANDOFF.md`.
  - Systemowa obsługa błędów `dev`/`prod`, logowanie i Qodana (`feat/error-handling-and-logging`, `1ce1f20` / `bbb1943`): naprawiono zgłoszenie Qodana `JSIgnoredPromiseFromCall` (`void runSearch(...)` w `web/src/App.jsx`), dodano `ErrorBoundary` (`web/src/ErrorBoundary.jsx`), przyjazne komunikaty „Błąd. Przepraszamy...” bez szczegółów technicznych w `prod` i ze szczegółami diagnostycznymi w `dev` (`APP_ENV=dev` / `VITE_APP_ENV=dev`), oraz moduł `mcp/app_logging.py` z domyślnym poziomem `WARNING+` (łatwa zmiana przez `LOG_LEVEL=DEBUG`/`INFO`) i rotacją plikową z kompresją `.gz` (`CompressedRotatingFileHandler`, `.local/logs/szukaj.log`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`) + kompresją logów Dockera (`compress: "true"`) w `docker-compose.yml`.
  - `R2` (S1): operator skonfigurował nowy `SEARXNG_SECRET` w lokalnym `.env` i potwierdził start kontenera `mcp-search`; smoke test na `http://szukaj.dom` PASS (`R4`).
- Kontrole: `python3 scripts/check_project.py` (Ruff, tracked-files, backend 55/55, frontend 19/19, build, diff, staged-diff) — wszystkie PASS.
- Lokalne pliki polityki i narzędzi IDE (`opencode.json`, `.opencode/`, `.mcp.json`, `qodana.yaml`) pozostawiono nietknięte poza commitami zgodnie z `AGENTS.md`.

- Dokumentacja integracji K4: docs/instrukcja-integracji-mcp-search.md jest punktem startowym dla agenta aplikacji. Zawiera ustalone adresy HTTP host/Docker, sesję MCP, przykład klienta 1.30.0, trzy stany i testy całej pętli model–narzędzie–UI. Domena `szukaj.dom` działa dla strony WWW; dla MCP obowiązują stałe adresy HTTP. Bez nowych zależności, rzeczywistych wyszukiwań i zmian drugiego repozytorium.
- Weryfikacja instrukcji: składnia przykładu Pythona, JSON zgodny ze wspólnymi fixtures i odsyłacze lokalne PASS. Dokładny przykład uruchomiono na lokalnym działającym MCP bez --live: initialize/tools/list PASS, protocol 2025-11-25. Nie wykonano rzeczywistego wyszukiwania ani odbioru z WirralAI.

- Q3 zakończone w kodzie: rozdzielone importy, nazwane walidatory w Python/JS. Ruff 0.17.1 jest przypięty w requirements-dev.txt, zainstalowany wyłącznie w ignorowanym .local/tools/ruff i włączony do python3 scripts/check_project.py.
- Mariusz zatwierdził instalację Ruff, stałe kontrole przed commitem i allow używania przez agentów. Zapis w AGENTS.md, bez zmiany opencode ani konfiguracji uprawnień. Domyślnie bez --fix; chronione ścieżki wykluczone.
- Raport dla WirralAI: docs/contract/MCP-COMPATIBILITY.md. Biblioteka MCP 1.30.0; wszystkie cztery wersje initialize i trzy syntetyczne stany narzędzia potwierdzone testami pełnego transportu MCP.
- Etapy kodu wykonane: S1–S5, K1–K4, Q1–Q3, D1–D8, O1–O5, W3.
- S1 (R2): nowy `SEARXNG_SECRET` ustawiony przez operatora, start potwierdzony. Stary klucz pozostaje w historii Git; nie używać go. Nie czytano ani nie zmieniano rzeczywistego .env i wartości sekretów.
- S5: runtime UID/build niepotwierdzone — brak dostępu do docker.sock. Obraz deklaruje UID 10001:10001; SearXNG ma stały digest. Nie uruchamiano sudo ani wdrożenia.
- K1/K4: klient WirralAI musi wykonać własne testy wspólnego docs/contract/web_search.example.json; nie zmieniano drugiego repozytorium.
- Warunek stabilnego wydania 1.0.0 ustalony przez Mariusza: wymagana jest pozytywna opinia projektu WirralAI po teście integracji MCP. Status: oczekujemy. Zielone testy repozytorium `szukaj` nie zastępują tej akceptacji; pozostałe kontrole wdrożenia nadal obowiązują.
- Q1: licznik Perplexity jest atomowy tylko w jednym procesie, nietrwały; restart zeruje limit.
- Lokalny dawny searxng-settings.yml pozostaje ignorowany, bez odczytu i modyfikacji. Diagnostyka HTTP w .local/tmp/http/. Nie czytać .local/secret/.
