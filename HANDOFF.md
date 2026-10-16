# HANDOFF.md — pałeczka między sesjami

## Koniec sesji — 2026-10-17

- Poprawki review zapisane w commicie `d5336b6` i wysłane na `origin/feat/search-ui`, PR #1. Brak merge i wdrożenia.
- Ostateczna decyzja Mariusza: obecny wygląd ma pozostać, także kontrast. Nie zmieniać kolorów, typografii ani układu. Uwaga review o kontraście jest świadomie nieprzyjęta.
- Rzeczywiste MCP z hosta działało: „SearXNG documentation” — 3 wyniki w 0,78 s; „Najważniejsze wydarzenia tygodnia w IT” — 5 wyników w 1,6 s. Źródło SearXNG, bez błędów i bez Perplexity.
- Nierozwiązane zgłoszenie VirralAI: PHP w `slim_ovh_ai_app` zwracało `dns_failed` dla `http://mcp-search:8000/mcp`. Mariusz potwierdził, że oba kontenery są na Latitude. Trzeba potwierdzić wspólną sieć `ai` i alias `mcp-search`; wynik poprawnego inspect nie został dostarczony. Nie potwierdzono wpływu Pi-hole ani naprawy integracji.
- Nie wykonywać pracy na Optiplexie ani poza bieżącym repo. Wklejony prompt dotyczący `/home/mariusz/app/searxng` nie został wykonany.
- Zakończenie sesji obejmuje tylko HANDOFF, CHANGELOG i STATUS. Lokalny commit dokumentacji; bez kolejnego pushu. Zachować niezacommitowany `tests/http/server-diagnostic.http`.

## Szczegóły poprawek — 2026-10-17

- Poprawki PR #1: niezależna lista zaufanych hostów (TrustedHostMiddleware), brak awarii dla `https://www./`, fokus/trap klawiatury mobilnej historii i wyłączenie ukrytego panelu z interakcji/drzewa dostępności.
- Mariusz zabronił zmian wyglądu: kolory, układ i typografia zachowane. Uwaga review o kontraście celowo pozostaje otwarta. CSS zmienia wyłącznie visibility zamkniętego panelu mobilnego.
- `SEARCH_ALLOWED_HOSTS`: domyślnie `127.0.0.1,localhost,mcp-search`; własne IP/domeny wymagają jawnego wpisu. Nazwy bez portów, nie stosować wildcardu.
- Kontrole po poprawkach: backend 20/20, frontend 17/17, build Vite, diff check i smoke nowego kodu na porcie 8891 — PASS. Testowy serwer zatrzymano. Kontenerów nie przebudowywano.
- Zgoda Mariusza na commit i push poprawek review na `feat/search-ui`. Nie obejmuje wdrożenia.
- `tests/http/server-diagnostic.http` pozostaje osobnym, niezacommitowanym plikiem z wcześniejszej diagnostyki PhpStorm; nie dodawać go do commita poprawek review.

## Poprzednie przekazanie — 2026-10-16

- Mariusz określił obecny zakres jako **MVP 1.0**. Zadanie: stabilizacja bez nowych funkcji.
- Gałąź `feat/search-ui`, zastane niezacommitowane zmiany zachowane. Zgoda Mariusza: agent sam wykonuje commit po zielonych kontrolach; push dopiero na osobne polecenie. Bez zmiany polityk.
- Poprawiono odczyt historii zawierającej wpis `null`: pozostałe poprawne wpisy są zachowane.
- Frontend i adapter HTTP odrzucają niepoprawną strukturę wyników: czytelny błąd UI / HTTP 502 zamiast awarii renderowania lub nieobsłużonego wyjątku.
- Komunikat o braku frontendu odsyła do istniejącego README.
- Testy: backend **17/17**, frontend **13/13**, build Vite i `git diff --check` — PASS. Testy obejmują także MCP tools/call z atrapą dostawcy, błędy odpowiedzi, ochronę cross-site i spóźnione odpowiedzi UI.
- Smoke działających kontenerów na `http://127.0.0.1:8890` — PASS: frontend, zasoby, favicon, walidacja API, sesja MCP i tools/list. Test dotyczy dotychczasowego obrazu; najnowsze poprawki wymagają przebudowania.
- Mariusz potwierdził działające wyszukiwanie screenem. W tej kontroli agent nie wykonywał rzeczywistych ani płatnych wyszukiwań.
- Sieć `ai` i kontenery uruchomił Mariusz przez sudo. Agent nie ma dostępu do socketu Docker; nie zmieniać uprawnień systemowych. Przebudowanie po poprawkach: `sudo docker compose up -d --build`, następnie `python3 scripts/smoke_test.py`.
- W tym repo nie używamy `dxrun` — decyzja Mariusza w rozmowie. Zależności testów lokalnie w `.local/python`; backend: `PYTHONPATH=.local/python python3 -m unittest discover -s tests -v`. TestClient wymagał uruchomienia poza sandboxem.
- Starlette zgłasza ostrzeżenie deprecacji TestClient z HTTPX; testy przechodzą. Nie dodawano zależności ani nie zmieniano wersji w ramach stabilizacji.
- Znane ograniczenia MVP: brak logowania, dostęp domyślnie przez loopback i sieć Docker `ai`, licznik Perplexity nietrwały i niesynchronizowany między równoległymi wywołaniami. Opis w README i docs/MCP-USAGE.md.
- Integracja z docelowym klientem AI wymaga osobnej weryfikacji. Brak lokalnego `origin/develop`; nie wykonywano fetch ani zmian gałęzi podczas stabilizacji istniejącej pracy.
