# HANDOFF.md — pałeczka między sesjami

## Aktualne przekazanie — 2026-10-16

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
