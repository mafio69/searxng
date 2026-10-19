# Plan wydania 1.0.0 — zadania dla agenta wykonawczego

Przygotowano: 2026-10-18 (przegląd dokumentacji, kodu i źródeł zewnętrznych). Zakres: **bez nowych funkcji**. Każde zadanie realizuj zgodnie z GIT-FLOW.md (gałąź z develop, `python3 scripts/check_project.py`, commit, lokalny merge, bez push bez zgody).

## 0. Warunki blokujące 1.0.0 (nie do zrobienia przez agenta)

| ID | Warunek | Kto |
|---|---|---|
| R1 | Pozytywna opinia WirralAI po teście integracji MCP (decyzja Mariusza, STATUS.md) | WirralAI / Mariusz |
| R2 | S1: nowy `SEARXNG_SECRET` ustawiony i start potwierdzony | operator |
| R3 | S5: zbudowany obraz, potwierdzony UID 10001 w działającym kontenerze | operator (docker.sock) |
| R4 | Smoke test na działającej instancji: `python3 scripts/smoke_test.py` (oraz raz `--query` za zgodą) | operator / agent za zgodą na Bash |

Dopóki R1–R4 nie są zamknięte, nie zmieniaj `## [Unreleased]` na `## [1.0.0]` i nie twórz taga.

## 1. Dokumentacja — niespójności do poprawienia

| ID | Plik | Problem | Poprawka |
|---|---|---|---|
| D1 | `docs/INSTRUKCJA.md:72` | Opis wyniku bez `status` i `errors` | Odesłać do kontraktu z MCP-USAGE.md (`status`, `source`, `results`, `errors`) |
| D2 | `docs/INSTRUKCJA.md:136` | Wskazuje `searxng-settings.yml`, który nie jest już śledzony ani montowany | Zmienić na `searxng-settings.example.yml` |
| D3 | `docs/INSTRUKCJA.md:139` | „`mcp` przypięty do `<2`” | Obecnie `mcp==1.30.0` |
| D4 | `docs/INSTRUKCJA.md:22,25,130` | Ścieżki środowiska autora `/home/mariusz/app/...` | Zamienić na polecenia względne z katalogu repo (`docker compose ...`) jak w README |
| D5 | `docs/INSTRUKCJA.md:117-125` | Szybki test bez nagłówka `Authorization` przy `MCP_AUTH_TOKEN`; `docker exec` wbrew zasadom agentów | Dopisać uwagę o tokenie; oznaczyć `docker exec` jako polecenie operatora |
| D6 | `docs/MCP-USAGE.md:165` | Lista zmiennych bez `MCP_AUTH_TOKEN`, `SEARCH_ALLOWED_HOSTS` | Uzupełnić lub odesłać do tabeli w README |
| D7 | `web/package.json:4` | `"version": "1.0.0"` przy projekcie w stanie 0.1.0 + Unreleased | Ujednolicić wersję w chwili wydania (jedno źródło wersji: CHANGELOG + tag) |
| D8 | `README.md` | Brak sekcji „Wersja / status wydania” | Krótka informacja: wersja, warunek R1, link do CHANGELOG |

## 2. Strona WWW (UI wyszukiwania) — kontrola przed wydaniem

Kod UI/API przejrzany (`mcp/web_app.py`): walidacja JSON, Origin, `Sec-Fetch-Site`, limit body 4096 B, TrustedHost — bez uwag blokujących. Do wykonania przez agenta za zgodą na Bash lub przez operatora:

- W1: `python3 scripts/smoke_test.py` na zbudowanym obrazie (strona, JS/CSS, favicon, odrzucanie obcych żądań, MCP initialize).
- W2: Ręcznie w przeglądarce: wyszukanie, stan `empty`, stan błędu (502), historia, `Ctrl/Cmd+K`, widok mobilny.
- W3: Nagłówki odpowiedzi strony — rozważyć (bez nowych funkcji, jako hardening) `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`; tylko za zgodą Mariusza.

## 3. Optymalizacja serwera (bez zmiany funkcji)

Źródła: dokumentacja SearXNG (outgoing, Granian, container), dokumentacja i dyskusje HTTPX.

| ID | Zmiana | Uzasadnienie | Ryzyko / test |
|---|---|---|---|
| O1 | `mcp/server.py`: jeden współdzielony `httpx.AsyncClient` na proces dla SearXNG (i osobny lub ten sam dla Perplexity) zamiast nowego klienta przy każdym zapytaniu; zamykanie w lifespan aplikacji | HTTPX zaleca jeden klient na czas życia procesu — pula połączeń i keep-alive; tworzenie klienta per żądanie kosztuje (kontekst SSL, nowe połączenie TCP) | Testy podmieniają dostawców atrapami — dostosować; test S2 (równoległość) musi przejść |
| O2 | `searxng-settings.example.yml`: jawne `outgoing.request_timeout` (np. 3.0) i `outgoing.max_request_timeout` (< 10 s timeoutu MCP, np. 8.0) | SearXNG odpowie częściowymi wynikami przed timeoutem MCP zamiast powodować `searxng_timeout` i płatny fallback | Bez rzeczywistych zapytań — test konfiguracji |
| O3 | `searxng-settings.example.yml`: `search.suspended_times.SearxEngineTooManyRequests` (np. 600) i wyłączenie silników, które w logach stale zwracają błędy/CAPTCHA (decyzja na podstawie logów operatora) | Mniej czekania na zablokowane silniki | Lista silników wyłącznie na podstawie logów, nie zgadywać |
| O4 | `docker-compose.yml`: healthcheck SearXNG (`/healthz`) i `depends_on: condition: service_healthy` dla `mcp-search` | Po restarcie MCP nie zwraca błędów zanim SearXNG wstanie | Wymaga `docker compose up` przez operatora |
| O5 | `docker-compose.yml`: rotacja logów (`logging: json-file`, `max-size`, `max-file`) dla obu usług | Brak niekontrolowanego wzrostu logów na VPS | Konfiguracja, bez wpływu na kod |
| O6 | NIE zmieniać liczby workerów Granian w SearXNG | Oficjalna dokumentacja: zmiana liczby workerów niezalecana (zasoby, bot detection) | — |
| O7 | NIE uruchamiać uvicorn z wieloma workerami | Licznik Perplexity i sesje MCP są w pamięci jednego procesu (Q1) | — |

Kolejność sugerowana: D1–D8 (jeden commit dokumentacji) → O1 → O2/O3 → O4/O5 → kontrola R4 → po R1–R3: wydanie 1.0.0 (CHANGELOG, wersje, tag — za zgodą).

## Źródła

- https://docs.searxng.org/admin/settings/settings_outgoing.html
- https://docs.searxng.org/admin/installation-granian.html
- https://docs.searxng.org/admin/installation-docker.html
- https://github.com/searxng/searxng/discussions/4972 (Granian zamiast uWSGI w obrazach od 2025.7.4)
- https://www.python-httpx.org/advanced/clients/
- https://github.com/encode/httpx/discussions/2719
