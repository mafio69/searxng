# szukaj (`szukaj.dom`) — Twoja wyszukiwarka, także dla AI

![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=111827)
![MCP 1.30.0](https://img.shields.io/badge/MCP-Streamable%20HTTP%20(1.30.0)-0F766E)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

> **Wielki internet. Twoje pytania. Jeden punkt dostępu dla Ciebie i Twoich agentów AI.**

**`szukaj`** (`https://github.com/mafio69/szukaj`, w sieci domowej dostępny jako **`http://szukaj.dom/`**) łączy prywatną metawyszukiwarkę **SearXNG**, dopracowany polski interfejs przeglądarkowy w React oraz serwer **Model Context Protocol (MCP)**. Możesz korzystać z wyszukiwarki bezpośrednio w przeglądarce albo podpiąć narzędzie `web_search` do swoich agentów i aplikacji AI. Gdy SearXNG zwróci puste wyniki lub błąd, serwer automatycznie próbuje opcjonalnego źródła awaryjnego — **Perplexity Search API**.

---

## Najważniejsze możliwości

| Obszar | Co otrzymujesz |
|---|---|
| **Wyszukiwarka dla ludzi (`szukaj.dom`)** | Przejrzysty polski interfejs React 19 z tytułami, domenami i fragmentami wyników, wyborem `5` lub `10` wyników, obsługą klawiatury i skrótem `Ctrl/Cmd + K`. |
| **Historia pod Twoją kontrolą** | Do 30 ostatnich zapytań wyłącznie w `localStorage` przeglądarki, usuwanie pojedynczych wpisów lub całości oraz tryb *Bez zapisywania historii*. |
| **Wyszukiwanie dla AI (MCP)** | Narzędzie `web_search` przez **MCP Streamable HTTP** (`/mcp`) z negocjacją protokołu (`2024-11-05` – `2025-11-25`) i opcjonalną autoryzacją `Bearer`. |
| **Wspólny silnik i kontrolowany fallback** | UI i MCP korzystają z tej samej asynchronicznej logiki (`httpx.AsyncClient` z pulą połączeń): najpierw **SearXNG**, a przy pustym wyniku lub błędzie opcjonalnie **Perplexity** z atomowym dziennym limitem. |
| **Gotowy stack Docker Compose** | Dwie usługi (`searxng` ze sprawdzaniem zdrowia `/healthz` oraz nieuprzywilejowany `mcp-search` `UID 10001:10001`) z rotacją logów; obraz sam buduje frontend i nie wymaga lokalnego Node.js ani Pythona. |

> [!NOTE]
> Perplexity nie jest wymagane do działania wyszukiwarki przez SearXNG — bez klucza API źródło awaryjne pozostaje wyłączone. Tryb *Bez zapisywania historii* dotyczy wyłącznie pamięci przeglądarki; samo zapytanie wyszukiwania trafia do backendu i dostawców.

---

## Architektura i przepływ zapytania

```text
Przeglądarka (szukaj.dom) ──► POST /api/search ──┐
                                                 ├──► web_search (async) ──► SearXNG (JSON, timeout 10 s)
Klient AI / Backend       ──► POST /mcp ─────────┘                                │
                              (Streamable HTTP)                         pusto lub błąd HTTP
                                                                                  ▼
                                                                   Perplexity Search API (opcjonalnie,
                                                                   dzienny limit w pamięci, timeout 20 s)
```

Serwer zwraca ustrukturyzowane wyniki (`title`, `url`, `snippet` do 400 znaków) oraz jednoznaczny status (`ok`, `empty`, `error`). Nie pobiera pełnej treści stron docelowych i nie generuje odpowiedzi modelem językowym.

---

## Szybki start (Docker Compose)

Potrzebujesz Dockera z Compose, dostępu do Internetu oraz wolnego portu na hoście (domyślnie `8890`). Polecenia wykonuj w katalogu głównym sklonowanego repozytorium `szukaj`.

### 1. Przygotuj konfigurację (`.env`)

Skopiuj szablon `.env.example` do `.env` i wygeneruj lokalnie własny klucz `SEARXNG_SECRET` (np. `openssl rand -hex 32`). Pozostałe puste zmienne przyjmą wartości domyślne. **Nigdy nie dodawaj prawdziwego `.env` do Gita.**

| Zmienna | Domyślne zachowanie / zastosowanie |
|---|---|
| `SEARXNG_SECRET` | Wymagany nowy losowy klucz SearXNG, ustawiany wyłącznie lokalnie; Compose nie wystartuje bez wartości |
| `MCP_AUTH_TOKEN` | Opcjonalny sekret Bearer dla wszystkich żądań `/mcp` (schemat `Bearer` jest nieczuły na wielkość liter, token porównywany stałoczasowo); konfiguruj tylko lokalnie |
| `PPLX_API_KEY` | Opcjonalny klucz Perplexity; brak uniemożliwia użycie źródła awaryjnego |
| `PPLX_DAILY_LIMIT` | Domyślnie `50`; limit prób Perplexity rezerwowanych atomowo w procesie |
| `SEARXNG_LANG` | Domyślnie `auto`; język wyszukiwania przekazywany do SearXNG |
| `SEARCH_ALLOWED_HOSTS` | Zaufane nazwy hostów oddzielone przecinkami; domyślnie `127.0.0.1,localhost,mcp-search`. Dla domeny lokalnej dopisz np. `szukaj.dom`. Nie używaj `*`. |
| `SEARCH_PORT` | Domyślnie `8890`; port publikowany na hoście |
| `SEARCH_BIND_ADDRESS` | Domyślnie `127.0.0.1`; adres nasłuchiwania na hoście |
| `SEARXNG_URL` | Domyślnie `http://searxng:8080`; adres usługi SearXNG wewnątrz sieci Docker |
| `MCP_HOST` | Domyślnie `0.0.0.0`; adres nasłuchiwania serwera wewnątrz kontenera |
| `MCP_PORT` | Domyślnie `8000`; port nasłuchiwania serwera wewnątrz kontenera |

SearXNG montuje w trybie tylko do odczytu publiczny szablon `searxng-settings.example.yml` (z pustym `server.secret_key` oraz skonfigurowanymi timeoutami `3.0` / `8.0` s); właściwy klucz pochodzi wyłącznie ze zmiennej `SEARXNG_SECRET`.

### 2. Utwórz sieć i uruchom kontenery

Usługi komunikują się w zewnętrznej sieci Docker `ai`. Utwórz ją jednorazowo:

```bash
docker network create ai
```

Zbuduj i uruchom stack:

```bash
docker compose up -d --build
docker compose ps
```

Otwórz **`http://127.0.0.1:8890/`** (lub **`http://szukaj.dom/`**, jeśli skonfigurowałeś lokalny DNS / reverse proxy i dodałeś `szukaj.dom` do `SEARCH_ALLOWED_HOSTS`). Kontener `mcp-search` startuje po przejściu `healthcheck` (`/healthz`) przez `searxng`.

---

## Podłączenie agenta AI (MCP Streamable HTTP)

W kliencie obsługującym **MCP Streamable HTTP** wskaż adres odpowiedni dla miejsca, w którym działa klient:

| Lokalizacja klienta MCP | Endpoint MCP |
|---|---|
| Na tym samym hoście co Docker | `http://127.0.0.1:8890/mcp` |
| W kontenerze podłączonym do sieci Docker `ai` | `http://mcp-search:8000/mcp` |

Jeżeli ustawiono `MCP_AUTH_TOKEN`, klient musi dołączać nagłówek `Authorization: Bearer <token>` do każdego żądania `/mcp` (inicjalizacja, odczyt strumienia, wywołania narzędzi, zamknięcie sesji).

### Sygnatura i odpowiedź narzędzia `web_search`

```text
web_search(query: string, max_results: integer = 5)
```

Przykładowe wywołanie:

```json
{"query": "jak działa metawyszukiwarka", "max_results": 3}
```

Narzędzie przyjmuje `query` o długości `1–1000` znaków Unicode (`max_results` w zakresie `1–10`) i zwraca tekst JSON:
- `status`: `"ok"` | `"empty"` | `"error"`
- `source`: `"searxng"` | `"perplexity-fast"` | `null`
- `results`: lista obiektów `{"title", "url", "snippet"}`
- `errors`: lista kontrolowanych kodów błędów dostawców (bez ujawniania surowych wyjątków ani sekretów)

Szczegółowy przewodnik wdrożeniowy dla agentów i aplikacji znajdziesz w **[docs/instrukcja-integracji-mcp-search.md](docs/instrukcja-integracji-mcp-search.md)** oraz **[docs/MCP-USAGE.md](docs/MCP-USAGE.md)**.

---

## Endpoint HTTP dla przeglądarki (`POST /api/search`)

Interfejs webowy korzysta z tego samego silnika przez endpoint `POST /api/search`:

```bash
curl http://127.0.0.1:8890/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"metawyszukiwarka SearXNG","max_results":5}'
```

- Przyjmuje obiekt JSON (do `4096` bajtów) z niepustym `query` (`1–500` znaków) i `max_results` (`1–10`).
- Zwraca `status` (`ok` / `empty`), `source` oraz `results`.
- Odrzuca żądania z obcych hostów (`TrustedHostMiddleware`) oraz żądania cross-site (`Origin` / `Sec-Fetch-Site`).
- W razie awarii dostawców zwraca kontrolowany kod `HTTP 502` bez szczegółów wewnętrznych.

---

## Smoke test wdrożenia

Po uruchomieniu kontenerów możesz zweryfikować działanie całego stacku (UI, zasobów statycznych, nagłówków, walidacji API oraz inicjalizacji sesji MCP i `tools/list`) bez zużywania zapytań wyszukiwarek:

```bash
python3 scripts/smoke_test.py
# lub dla domeny lokalnej / innego portu:
python3 scripts/smoke_test.py --url http://szukaj.dom
```

Pełną próbę wyszukiwania na żywo włączasz jawnie flagą `--query` (może użyć płatnego fallbacku Perplexity, jeśli SearXNG nie zwróci wyników):

```bash
python3 scripts/smoke_test.py --url http://szukaj.dom --query "SearXNG documentation"
```

---

## Rozwiązywanie problemów

| Objaw | Co sprawdzić |
|---|---|
| Compose zgłasza brak sieci `ai` | Wykonaj `docker network create ai` przed startem usług |
| Compose zgłasza brak `.env` lub `SEARXNG_SECRET` | Utwórz lokalny `.env` na bazie `.env.example` i wpisz niepusty `SEARXNG_SECRET` |
| `400 Invalid host header` pod własną domeną | Dopisz domenę (np. `szukaj.dom`) po przecinku do `SEARCH_ALLOWED_HOSTS` w `.env` i zrestartuj `mcp-search` |
| Kontener klienta nie łączy się z MCP | Podłącz kontener klienta do sieci `ai` i użyj `http://mcp-search:8000/mcp` zamiast `127.0.0.1` |
| Brak wyników wyszukiwania | Sprawdź logi (`docker compose logs --tail=50 searxng mcp-search`) oraz dostęp kontenera `searxng` do Internetu |

---

## Dla rozwijających projekt

- **Backend:** Python 3.12, FastMCP v1 (`mcp==1.30.0`), HTTPX (`AsyncClient`), Starlette, Uvicorn.
- **Frontend:** React 19, Vite 7, Vitest + Testing Library (lokalnie Node.js `>=22.12`, w Dockerze budowany na Node.js 24).

| Ścieżka | Odpowiedzialność |
|---|---|
| `mcp/server.py` | Narzędzie MCP `web_search`, współdzielony `httpx.AsyncClient`, dostawcy i atomowy limit Perplexity |
| `mcp/web_app.py` | Aplikacja ASGI (Starlette), `POST /api/search`, serwowanie UI, nagłówki bezpieczeństwa i `lifespan` |
| `mcp/access.py` | Middleware autoryzacji `Bearer` dla `/mcp` |
| `web/src/` | Interfejs React (`szukaj.dom`), historia w `localStorage` i klient API |
| `scripts/check_project.py` | Obowiązkowa bramka jakości przed każdym commitem |
| `scripts/check_tracked_files.py` | Skaner sekretów i zabronionych plików w drzewie roboczym oraz indeksie Git |
| `scripts/smoke_test.py` | Bezależnościowy test dymny wdrożenia |
| `tests/` i `web/src/App.test.jsx` | Testy jednostkowe i integracyjne backendu (53) oraz frontendu (18) |

### Kontrola jakości przed commitem

Jednorazowa lokalna instalacja przypiętego lintera Ruff do ignorowanego katalogu `.local/`:

```bash
mkdir -p .local/tmp/pip
TMPDIR="$PWD/.local/tmp/pip" python3 -m pip install --only-binary=:all: --no-deps --target .local/tools/ruff --cache-dir .local/cache/pip -r requirements-dev.txt
```

Przed każdym commitem uruchom pełną bramkę jakości:

```bash
python3 scripts/check_project.py
```

Skrypt wykonuje kolejno:
1. `ruff` — lint kodu Pythona (`mcp`, `scripts`, `tests`),
2. `tracked-files` — skanowanie plików śledzonych i indeksu Git pod kątem sekretów i niepustych szablonów `.env*`,
3. `backend` — 53 testy jednostkowe i integracyjne Pythona (offline),
4. `frontend` — 18 testów komponentów React (Vitest),
5. `build` — produkcyjny build frontendu (Vite),
6. `diff` oraz `staged-diff` — kontrola formatowania zmian Git (`git diff --check`).

---

## Dokumentacja projektu

- **[Instrukcja integracji MCP Search dla agenta](docs/instrukcja-integracji-mcp-search.md)** — punkt startowy wdrożenia w aplikacji klienckiej, adresy HTTP, sesja MCP i testy odbioru.
- **[MCP dla AI i integratorów](docs/MCP-USAGE.md)** — pełny kontrakt narzędzia `web_search`, kody błędów i negocjacja protokołu.
- **[Zgodność kontraktu MCP](docs/contract/MCP-COMPATIBILITY.md)** — raport weryfikacji transportu i wspólnych fixtures JSON.
- **[Codzienna instrukcja operacyjna](docs/INSTRUKCJA.md)** — komendy Docker Compose i konfiguracja klientów MCP.
- **[Mapa techniczna repozytorium](REPO.md)**, **[Stan projektu](STATUS.md)** i **[Historia zmian](CHANGELOG.md)**.
- **[Zasady pracy agentów AI](AGENTS.md)**, **[Git Flow](GIT-FLOW.md)** i **[Przekazanie sesji](HANDOFF.md)**.

## Wersja i status wydania

Ostatnie oznaczone wydanie to `0.1.0` (bieżące zmiany rozwojowe znajdują się w sekcji `[Unreleased]` w [CHANGELOG.md](CHANGELOG.md)). Oznaczenie stabilnego wydania `1.0.0` wymaga pozytywnego potwierdzenia testu integracji MCP przez aplikację kliencką WirralAI oraz zamknięcia kontroli wdrożeniowych opisanych w [STATUS.md](STATUS.md).
