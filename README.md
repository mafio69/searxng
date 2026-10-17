# szukaj. — Twoja wyszukiwarka, także dla AI

**Wielki internet. Twoje pytania. Jeden punkt dostępu dla Ciebie i Twoich agentów AI.**

Projekt łączy metawyszukiwarkę **SearXNG**, polski interfejs przeglądarkowy i serwer **MCP**. Możesz szukać samodzielnie albo udostępnić wyszukiwanie swojej aplikacji i agentom. Gdy SearXNG zwróci puste wyniki lub błąd, serwer próbuje opcjonalnego źródła awaryjnego: Perplexity Search API.

## Co tu znajdziesz

- **Wyszukiwarkę dla ludzi** — interfejs React z tytułami, adresami i opisami wyników, wyborem 5 lub 10 wyników oraz skrótem `Ctrl/Cmd + K`.
- **Historię pod Twoją kontrolą** — do 30 ostatnich zapytań w pamięci przeglądarki, usuwanie pojedynczych wpisów lub całości i opcję niezapisywania nowych zapytań.
- **Wyszukiwanie dla AI** — narzędzie MCP `web_search` przez Streamable HTTP, do podłączenia do własnego klienta lub backendu aplikacji.
- **Wspólny mechanizm** — interfejs i MCP korzystają z tej samej logiki: najpierw SearXNG, potem ewentualnie Perplexity.
- **Własne środowisko** — dwie usługi Docker Compose; frontend buduje się razem z obrazem aplikacji. Wariant kontenerowy nie wymaga lokalnego Node.js ani Pythona.

Perplexity nie jest wymagane do wyszukiwania przez SearXNG. Bez klucza API źródło awaryjne pozostaje niedostępne. Opcja niezapisywania historii dotyczy przeglądarki — zapytania nadal trafiają do serwera i dostawców wyszukiwania.

## Jak to działa

```text
Przeglądarka → /api/search ─┐
                          ├→ wspólna logika → SearXNG → wyniki
Klient AI   → /mcp ───────┘                       │
                                        pusto lub błąd
                                                 ↓
                                      Perplexity (opcjonalnie)
```

Serwer zwraca tytuły, URL i fragmenty do 400 znaków. Nie pobiera pełnej treści znalezionych stron i nie generuje odpowiedzi modelem językowym.

## Uruchomienie przez Docker Compose

Potrzebujesz Dockera z Compose, dostępu do Internetu dla wyszukiwania i pobrania obrazów oraz wolnego portu `8890`. Polecenia wykonuj w katalogu sklonowanego repozytorium.

### 1. Przygotuj konfigurację

Utwórz lokalny plik `.env` na podstawie `.env.example` i ustaw nowy `SEARXNG_SECRET`. Pozostałe puste pola używają domyślnych wartości lub wyłączają opcjonalną integrację. Compose wymaga pliku i klucza. Nie dodawaj rzeczywistego `.env` do Gita.

| Zmienna | Domyślne zachowanie / zastosowanie |
|---|---|
| `SEARXNG_SECRET` | Wymagany nowy losowy klucz SearXNG, ustawiany wyłącznie lokalnie; Compose nie wystartuje bez wartości |
| `MCP_AUTH_TOKEN` | Opcjonalny sekret Bearer dla wszystkich żądań `/mcp`; konfiguruj tylko lokalnie, nigdy w kodzie UI |
| `PPLX_API_KEY` | Opcjonalny klucz Perplexity; brak uniemożliwia użycie źródła awaryjnego |
| `PPLX_DAILY_LIMIT` | Domyślnie `50`; limit prób Perplexity rezerwowanych w procesie |
| `SEARXNG_LANG` | Domyślnie `auto`; język wyszukiwania |
| `SEARCH_ALLOWED_HOSTS` | Zaufane nazwy hostów oddzielone przecinkami; domyślnie `127.0.0.1,localhost,mcp-search`. Przy własnym adresie LAN/domenie dodaj go jawnie, zachowując potrzebne dotychczasowe nazwy. Nie używaj `*`. |
| `SEARCH_PORT` | Domyślnie `8890`; port publikowany na hoście |
| `SEARCH_BIND_ADDRESS` | Domyślnie `127.0.0.1`; adres nasłuchiwania na hoście |

Compose ustawia `SEARXNG_URL` na `http://searxng:8080`. Zostaw domyślne `MCP_HOST` (`0.0.0.0`) i `MCP_PORT` (`8000`) wewnątrz kontenera, aby zachować zgodność z mapowaniem portów.

SearXNG montuje publiczny `searxng-settings.example.yml` z pustym `server.secret_key`; rzeczywista wartość pochodzi wyłącznie ze zmiennej `SEARXNG_SECRET` ustawionej lokalnie w `.env` lub środowisku operatora. Wygeneruj nową losową wartość — starego klucza z historii nie używaj ponownie. Nie wklejaj go do czatu ani logów. Dotychczasowy lokalny `searxng-settings.yml` pozostaje na dysku, ale nie jest już śledzony ani montowany przez Compose. Ta zmiana nie usuwa starego klucza z historii Git; rotację i uruchomienie nowego obrazu potwierdza operator.

### 2. Przygotuj sieć i uruchom usługi

Compose korzysta z istniejącej sieci Docker `ai`. Jeśli jeszcze jej nie masz, utwórz ją jednorazowo:

```bash
docker network create ai
```

Następnie zbuduj i uruchom projekt:

```bash
docker compose up -d --build
docker compose ps
```

Otwórz **http://127.0.0.1:8890/**. Pierwszy start trwa dłużej, ponieważ Docker pobiera zależności i buduje frontend. Po zmianie portu użyj wybranej wartości zamiast `8890`.

Domyślna konfiguracja udostępnia aplikację tylko lokalnie na hoście. Aplikacja nie ma własnego logowania; udostępnienie jej poza hostem wymaga przygotowania kontroli dostępu. Kontenery w sieci `ai` również mają dostęp do usługi.

## Podłącz agenta AI

W kliencie obsługującym **MCP Streamable HTTP** dodaj adres właściwy dla jego lokalizacji:

| Klient | Adres |
|---|---|
| Na tym samym hoście co Docker | `http://127.0.0.1:8890/mcp` |
| W kontenerze podłączonym do sieci `ai` | `http://mcp-search:8000/mcp` |

Jeżeli operator ustawił `MCP_AUTH_TOKEN`, klient musi wysyłać `Authorization: Bearer <wartość z bezpiecznej konfiguracji>` w każdym żądaniu MCP, także podczas inicjalizacji, odczytu strumienia i zamykania sesji. Bez konfiguracji ochrona jest wyłączona. Dotyczy tylko MCP; udostępnienie całego UI/API poza zaufaną siecią wymaga osobnej kontroli dostępu.

Po inicjalizacji sesji klient znajdzie narzędzie:

```text
web_search(query: string, max_results: integer = 5)
```

Przykładowe argumenty:

```json
{"query": "jak działa metawyszukiwarka", "max_results": 3}
```

Narzędzie zwraca tekst JSON z polami `status`, `source`, `results`, `errors`. Status to `ok`, `empty` lub `error`; przy braku wyników i awarii źródło jest `null`, a rozróżnienie wynika ze statusu. Limit wyników jest ograniczany do zakresu 1–10.

Pełny kontrakt, obsługę błędów i instrukcję dla agentów znajdziesz w **[docs/MCP-USAGE.md](docs/MCP-USAGE.md)**. Endpoint `/mcp` wymaga protokołu MCP, więc nie przyjmuje samego JSON-a z zapytaniem jak zwykłe API REST.

## API dla własnej aplikacji

Interfejs przeglądarkowy używa `POST /api/search`. Poniższe żądanie wykona rzeczywiste wyszukiwanie i może uruchomić opcjonalne płatne źródło awaryjne:

```bash
curl http://127.0.0.1:8890/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"metawyszukiwarka SearXNG","max_results":5}'
```

API przyjmuje niepuste zapytanie do 500 znaków i `max_results` od 1 do 10. Zwraca `status`, `source` oraz `results` z polami `title`, `url`, `snippet`. `status: empty`, pusta lista i `source: null` oznaczają poprawne wyszukanie bez wyników. Awaria daje HTTP 502 bez szczegółów dostawców. Narzędzie MCP dopuszcza do 1000 znaków Unicode i odrzuca puste zapytania przed HTTP.

## Gdy coś nie działa

| Objaw | Co sprawdzić |
|---|---|
| Compose zgłasza brak sieci `ai` | Utwórz sieć przed uruchomieniem usług |
| Compose zgłasza brak `.env` | Utwórz lokalny plik; bez Perplexity może być pusty |
| Port `8890` jest zajęty | Ustaw inny `SEARCH_PORT` w lokalnej konfiguracji i odtwórz usługę przez Compose |
| Kontener klienta nie łączy się z MCP | Podłącz go do sieci `ai` i użyj `mcp-search:8000`, zamiast `127.0.0.1:8890` |
| Brak wyników | Sprawdź logi SearXNG, dostęp do Internetu i włączenie formatu JSON; bez klucza Perplexity nie pomoże awaryjnie |
| Strona zgłasza brak zbudowanego frontendu | Zbuduj obraz przez Compose; samo uruchomienie `mcp/server.py` udostępnia wyłącznie MCP |

```bash
docker compose logs --tail=50 searxng mcp-search
```

Limit Perplexity jest przechowywany w pamięci procesu i resetuje się po restarcie lub zmianie daty. Rezerwacja prób jest atomowa w jednym procesie; błędy i anulowanie nie zwracają rezerwacji. Nie jest to trwały ani współdzielony między procesami budżet.

## Smoke test po uruchomieniu

Po starcie kontenerów wykonaj z katalogu repozytorium:

```bash
python3 scripts/smoke_test.py
```

Skrypt wymaga tylko standardowej biblioteki Pythona. Sprawdza stronę, pliki JS/CSS, favicon, odrzucanie niepoprawnych i obcych żądań API oraz inicjalizację MCP i obecność `web_search`. Zwraca kod `0` po sukcesie, `1` po błędzie. Domyślnie nie wywołuje dostawców wyszukiwania, więc nie potwierdza dostępności SearXNG ani Perplexity.

Inny port/adres: `python3 scripts/smoke_test.py --url http://127.0.0.1:8891`.
Pełną próbę wyszukiwania włączasz jawnie:

```bash
python3 scripts/smoke_test.py --query "SearXNG documentation"
```

Ta opcja wymaga niepustych wyników i może użyć płatnego Perplexity, jeśli SearXNG zawiedzie. Nie przekazuj sekretów w zapytaniu.

## Dla rozwijających projekt

Backend obrazu używa Python 3.12, FastMCP v1, HTTPX i Starlette. Frontend to React 19 i Vite 7; lokalnie wymaga Node.js co najmniej 22.12. Docker buduje go na Node.js 24.

| Plik / katalog | Rola |
|---|---|
| `mcp/server.py` | Narzędzie MCP i wybór źródła wyników |
| `mcp/web_app.py` | API przeglądarkowe, pliki frontendu i wspólna aplikacja HTTP |
| `web/src/` | Interfejs, historia lokalna i klient API |
| `tests/test_web_app.py` | Testy backendu i mechanizmu awaryjnego z atrapami dostawców |
| `web/src/App.test.jsx` | Testy interfejsu |
| `docker-compose.yml` | Dwie usługi i ich połączenie |

Po zainstalowaniu zależności backendu z `mcp/requirements.txt` oraz frontendu z `web/package.json` dostępne kontrole to:

```bash
python -m unittest discover -s tests -v
npm --prefix web test
npm --prefix web run build
git diff --check
```

Repozytorium nie definiuje osobnego kompletnego zestawu lintingu, typechecka i skanowania bezpieczeństwa.

Do pracy nad frontendem służy `npm --prefix web run dev`. Serwer Vite przekazuje `/api` do backendu pod `http://127.0.0.1:8890`; backend musi być uruchomiony osobno.

## Dokumentacja

- [MCP dla AI i integratorów](docs/MCP-USAGE.md) — kontrakt narzędzia, protokół, błędy i plan testu integracyjnego.
- [Instrukcja integracji](docs/INSTRUKCJA.md) — przykłady klientów; zawiera także starsze ścieżki środowiska autora, które należy dostosować.
- [Stan projektu](STATUS.md) i [historia zmian](CHANGELOG.md).
- [Zasady pracy agentów](AGENTS.md), [Git flow](GIT-FLOW.md) i [przekazanie sesji](HANDOFF.md).

Opis odpowiada kodowi w repozytorium. Nie stanowi potwierdzenia działania konkretnego wdrożenia ani integracji z wybranym klientem MCP.
