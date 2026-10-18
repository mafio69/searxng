# MCP — potwierdzenie zgodności z kontraktem WirralAI

Data: 2026-10-18. Raport z lokalnych testów kodu repozytorium, bez rzeczywistych
zapytań do wyszukiwarek. Nie potwierdza aktualizacji działającego kontenera
ani wykonania testów klienta WirralAI.

## Biblioteka i protokół

- Przypięta biblioteka: `mcp==1.30.0` w `mcp/requirements.txt`.
- `initialize` negocjuje wersję klienta zgodnie z tabelą:

| Wersja żądana | Wersja zwrócona |
|---|---|
| 2024-11-05 | 2024-11-05 |
| 2025-03-26 | 2025-03-26 |
| 2025-06-18 | 2025-06-18 |
| 2025-11-25 | 2025-11-25 |
| nieobsługiwana, syntetyczna 2099-01-01 | 2025-11-25 |

Wszystkie zwracane wersje mieszczą się na liście akceptowanej przez WirralAI.
Test: `tests/test_mcp_protocol.py` (wersja zainstalowana i negocjacja).

## Syntetyczne odpowiedzi web_search

To JSON **wewnątrz tekstowego bloku MCP content**, nie cała koperta JSON-RPC.
Wspólny plik dla obu projektów: [web_search.example.json](web_search.example.json).

Wyniki:

```json
{"status":"ok","source":"searxng","results":[{"title":"Example","url":"https://example.org/","snippet":"Synthetic fixture"}],"errors":[]}
```

Poprawne wyszukanie bez wyników:

```json
{"status":"empty","source":null,"results":[],"errors":[]}
```

Awaria:

```json
{"status":"error","source":null,"results":[],"errors":["searxng_timeout","perplexity_no_key"]}
```

`empty` ma zawsze puste `errors`. Brak skonfigurowanego opcjonalnego Perplexity
po poprawnym pustym SearXNG oznacza brak wyników, nie awarię.
Błąd dowolnego dostawcy bez uzyskania wyników daje `error`, także jeśli drugi
dostawca zwrócił poprawną pustą listę. Wyczerpany limit fallbacku daje `error`.
Udany fallback z wynikami daje `ok` i puste `errors`.

## Wyniki kontroli

- Trzy testy kontraktu **3/3 PASS**: pełne sesje `initialize` →
  `notifications/initialized` → `tools/list` → `tools/call`, porównanie tekstowego
  JSON ze wspólnym plikiem (`tests/test_mcp_contract.py`).
- Dodatkowe testy rozróżniają timeouty, błędy dostawcy, limit i wyłączony fallback
  (`tests/test_search_status.py`).
- Cały zestaw: **46 testów backendu, 18 frontendu — PASS**; Ruff, build i kontrole
  zmian Git — PASS. Polecenie: `python3 scripts/check_project.py`.

Użyto wyłącznie atrap i syntetycznych danych. Raport nie zawiera sekretów,
danych użytkowników ani logów rzeczywistych wyszukiwań.
