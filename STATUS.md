# STATUS.md

Aktualizacja: 2026-10-19.

- Strona `szukaj.dom` działa w sieci domowej pod `http://szukaj.dom/` (Pi-hole `*.dom` → serwer, Traefik → `127.0.0.1:8000`, `SEARCH_ALLOWED_HOSTS` z `szukaj.dom`); tytuł w `web/index.html` i marka w `web/src/App.jsx` ustawione na `szukaj.dom`. Sprawdzone 2026-10-19: strona 200, `/api/search` 200 ze źródłem SearXNG. Dla MCP nadal stałe adresy HTTP.
- Wykonano wszystkie zadania kodu i dokumentacji z planu `docs/release-1.0.0-plan.md` oraz poprawki code review PR #2: skaner śledzonych plików i indeksu Git (`scripts/check_tracked_files.py`), poprawki dokumentacji `D1–D8`, optymalizacje serwera i Compose `O1–O5`, nagłówki `W3`, nieprzekazywany przy przekierowaniu `Authorization` w smoke teście i nieczuły na wielkość liter schemat `Bearer` w `mcp/access.py`.
- Instrukcja dla agenta wdrażającego MCP Search: `docs/instrukcja-integracji-mcp-search.md`. Na teraz dla MCP stałe adresy HTTP; `szukaj.dom` działa dla strony WWW. Dokumentacja obejmuje testy połączenia, kontraktu i odpowiedzi modelu w aplikacji.
- Przykład klienta z instrukcji sprawdzony bez wyszukiwania na działającej lokalnej usłudze: initialize/tools/list PASS, protokół 2025-11-25. Nie zastępuje to odbioru integracji przez WirralAI.
- Stabilne 1.0.0 czeka na pozytywną opinię WirralAI o integracji MCP (`R1`), zgodnie z decyzją Mariusza. Akceptacji jeszcze nie otrzymano.
- Obowiązkowa kontrola przed commitem: `python3 scripts/check_project.py` (Ruff, tracked-files, backend 53/53, frontend 18/18, build, diff, staged-diff) — wszystko PASS.
- Zamknięte `S1` (`R2`): nowy `SEARXNG_SECRET` ustawiony przez operatora i start potwierdzony; stary sekret pozostaje w historii.
- Do potwierdzenia po przebudowie obrazu z najnowszymi zmianami: `R3` (UID 10001 w kontenerze) oraz `R4` (`python3 scripts/smoke_test.py`).
