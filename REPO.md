# REPO.md — mapa techniczna

## Przeznaczenie i architektura

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
- Smoke: `python3 scripts/smoke_test.py`; opcja `--query` wykonuje rzeczywiste wyszukiwanie i może użyć płatnego Perplexity.
- Development UI: `npm --prefix web run dev`, proxy `/api` do backendu na porcie 8890.

## Mechanizmy i ograniczenia

- MCP używa Streamable HTTP; inicjalizacja i sesja są wymagane. Wynik narzędzia jest tekstem JSON. Kontrakt: `docs/MCP-USAGE.md`.
- `web_search` ogranicza wynik do 1–10 pozycji, fragment do 400 znaków. Timeouty HTTP: SearXNG 10 s, Perplexity 20 s.
- Perplexity uruchamia się wyłącznie po pustym wyniku/błędzie SearXNG. Domyślny licznik 50 dziennie jest w pamięci, resetuje się po restarcie/zmianie daty i nie jest synchronizowany między równoległymi wywołaniami.
- Wszystkie trasy HTTP sprawdzają Host przez TrustedHostMiddleware. `SEARCH_ALLOWED_HOSTS` zawiera nazwy oddzielone przecinkami, domyślnie `127.0.0.1,localhost,mcp-search`; dodatkowe IP/domeny wymagają jawnego wpisu. Origin API musi odpowiadać zaufanemu hostowi.
- Przeglądarkowe API wymaga application/json, zapytania do 500 znaków, limitu 1–10, odrzuca żądania cross-site i body powyżej 4096 bajtów. Nie ujawnia szczegółów błędów dostawców.
- Historia jest wyłącznie w localStorage. Wyłączenie historii nie blokuje przekazania zapytania do backendu i wyszukiwarek.
- Aplikacja nie ma logowania; port hosta domyślnie dostępny tylko przez loopback. Sieć `ai` daje dostęp innym podłączonym kontenerom.
- `python mcp/server.py` uruchamia samo MCP; pełna aplikacja startuje przez `mcp/web_app.py`. Frontend jest kopiowany do obrazu podczas budowania.
- FastMCP session manager uruchamia się raz na instancję; testy aplikacji izolują instancje MCP.
- Dane robocze/cache/testy tymczasowe trafiają do ignorowanego `.local/`; nie czytać `.local/secret/`.
