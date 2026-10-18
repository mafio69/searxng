# REPO.md — mapa techniczna

## Przeznaczenie i architektura

Agent wdrażający wyszukiwanie w aplikacji zaczyna od [instrukcji integracji MCP Search](docs/instrukcja-integracji-mcp-search.md). Dokument rozstrzyga wybór obecnego endpointu HTTP i opisuje test pełnej pętli narzędzia; przyszła domena wyszukaj.dom nie jest jeszcze adresem wdrożonym.

MVP 1.0: wyszukiwanie dla użytkowników przeglądarki i klientów MCP. Bez generowania odpowiedzi modelem i bez pobierania pełnej treści stron.

```text
React → POST /api/search ─┐
                         ├→ web_search → SearXNG → opcjonalnie Perplexity
Klient MCP → /mcp ────────┘
```

| Obszar | Plik / katalog | Odpowiedzialność |
|---|---|---|
| Wyszukiwanie | `mcp/server.py` | FastMCP v1, dostawcy, fallback, limit liczby wyników |
| HTTP i frontend | `mcp/web_app.py` | Starlette/Uvicorn, walidacja API, pliki statyczne, transport MCP |
| UI | `web/src/App.jsx` | Wyszukiwanie, stany UI, anulowanie i odrzucanie spóźnionych odpowiedzi |
| Klient API | `web/src/api.js` | Żądania, kontrola struktury odpowiedzi, dozwolone URL HTTP/HTTPS |
| Historia | `web/src/storage.js` | localStorage, maksymalnie 30 zapytań, deduplikacja przy zapisie |
| Backend tests | `tests/test_web_app.py` | unittest, TestClient, atrapy dostawców |
| Frontend tests | `web/src/App.test.jsx` | Vitest, Testing Library, atrapa fetch |
| Smoke | `scripts/smoke_test.py` | Standardowa biblioteka Pythona, kontrola uruchomionej aplikacji |

## Uruchamianie i kontrole

- Docker Compose buduje frontend na Node.js 24 i backend na Pythonie 3.12. Lokalny frontend wymaga Node.js >=22.12.
- `docker-compose.yml` wymaga istniejącej sieci `ai`, lokalnego `.env` oraz nowej wartości `SEARXNG_SECRET` w środowisku operatora. Publiczny `searxng-settings.example.yml` ma pusty klucz; dawny lokalny `searxng-settings.yml` jest ignorowany i nie jest montowany.
- Start: `docker compose up -d --build`. Przy wymaganym sudo polecenie wykonuje operator.
- Web: `http://127.0.0.1:8890/`. MCP na hoście: `http://127.0.0.1:8890/mcp`; w sieci `ai`: `http://mcp-search:8000/mcp`.
- Testy backendu po instalacji `mcp/requirements.txt`: `python3 -m unittest discover -s tests -v`.
- Testy i build frontendu po `npm --prefix web ci`: `npm --prefix web test`, `npm --prefix web run build`.
- Kontrola zmian: `git diff --check`.
- Pełna obowiązkowa kontrola przed commitem: `python3 scripts/check_project.py` — Ruff → unittest → Vitest → build → diff-check roboczy i staged. Pierwszy błąd kończy kontrolę kodem 1; raporty pozostają w `.local/logs/checks/`.
- Ruff jest przypięty w `requirements-dev.txt`, konfigurowany w `ruff.toml`, instalowany lokalnie w `.local/tools/ruff`. Runner korzysta także z istniejących lokalnych zależności backendu w `.local/python`, jeśli są zainstalowane. Brak narzędzia blokuje kontrolę; nie ma automatycznego pobierania ani auto-fix.
- Smoke: `python3 scripts/smoke_test.py`; opcja `--query` wykonuje rzeczywiste wyszukiwanie i może użyć płatnego Perplexity.
- Development UI: `npm --prefix web run dev`, proxy `/api` do backendu na porcie 8890.

## Mechanizmy i ograniczenia

- MCP używa Streamable HTTP; inicjalizacja i sesja są wymagane. Wynik narzędzia jest tekstem JSON. Kontrakt: `docs/MCP-USAGE.md`.
- `web_search` i dostawcy są asynchroniczni (HTTPX AsyncClient); API i MCP oczekują na tę samą usługę bez blokowania pętli zdarzeń. Limit wyniku 1–10, fragment do 400 znaków. Timeouty HTTP: SearXNG 10 s, Perplexity 20 s.
- Perplexity uruchamia się wyłącznie po pustym wyniku/błędzie SearXNG. Domyślny licznik 50 dziennie jest w pamięci, resetuje się po restarcie/zmianie daty. Rezerwacja próby przed HTTP jest chroniona krótką blokadą, bez oczekiwania na sieć pod blokadą.
- Wszystkie trasy HTTP sprawdzają Host przez TrustedHostMiddleware. `SEARCH_ALLOWED_HOSTS` zawiera nazwy oddzielone przecinkami, domyślnie `127.0.0.1,localhost,mcp-search`; dodatkowe IP/domeny wymagają jawnego wpisu. Origin API musi odpowiadać zaufanemu hostowi.
- Przeglądarkowe API wymaga application/json, zapytania do 500 znaków, limitu 1–10, odrzuca żądania cross-site i body powyżej 4096 bajtów. Nie ujawnia szczegółów błędów dostawców.
- Historia jest wyłącznie w localStorage. Wyłączenie historii nie blokuje przekazania zapytania do backendu i wyszukiwarek.
- Aplikacja nie ma logowania; port hosta domyślnie dostępny tylko przez loopback. Sieć `ai` daje dostęp innym podłączonym kontenerom.
- `python mcp/server.py` uruchamia samo MCP; pełna aplikacja startuje przez `mcp/web_app.py`. Frontend jest kopiowany do obrazu podczas budowania.
- FastMCP session manager uruchamia się raz na instancję; testy aplikacji izolują instancje MCP.
- Obraz aplikacji deklaruje USER 10001:10001. SearXNG jest przypięty do manifestu sha256 z oficjalnego Docker Hub (metadane 2026-10-18); aktualizacja wymaga świadomej zmiany digestu. Test konfiguracji nie zastępuje zbudowania obrazu i sprawdzenia UID we wdrożeniu.
- Dane robocze/cache/testy tymczasowe trafiają do ignorowanego `.local/`; nie czytać `.local/secret/`.

- Opcjonalny MCP_AUTH_TOKEN chroni wszystkie metody /mcp (także samodzielny entrypoint). Bez konfiguracji zachowany jest dotychczasowy tryb. Nie jest to logowanie do przeglądarkowego UI/API.
