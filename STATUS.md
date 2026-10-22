# STATUS.md

Aktualizacja: 2026-10-22.

- Dokumentacja główna przetłumaczona na język angielski (`README.md`), a pełna wersja polska zachowana w `README_PL.md` ze wzajemnymi odsyłaczami.
- Strona `szukaj.dom` (repozytorium `szukaj`) działa w sieci domowej pod `http://szukaj.dom/` (Pi-hole `*.dom` → serwer, Traefik → `127.0.0.1:8000`, `SEARCH_ALLOWED_HOSTS` z `szukaj.dom`); tytuł w `web/index.html` i marka w `web/src/App.jsx` ustawione na `szukaj.dom`, pakiet UI przemianowany na `szukaj-ui`, usługa silnika w `docker-compose.yml` nazwana `szukaj`, `README.md` odświeżone pod prezentację na GitHubie. Sprawdzone: strona 200, `/api/search` 200 ze źródłem SearXNG, `python3 scripts/smoke_test.py --url http://szukaj.dom` PASS (`R4`). Dla MCP nadal stałe adresy HTTP.
- Wykonano wszystkie zadania kodu i dokumentacji z planu `docs/release-1.0.0-plan.md`, poprawki code review PR #2, ostrzeżenia GitGuardian/Qodana oraz systemową obsługę błędów (`APP_ENV`: przyjazne „Błąd. Przepraszamy...” na `prod`, szczegóły diagnostyczne na `dev`, React `ErrorBoundary`) i logowanie od `WARNING` wzwyż (`LOG_LEVEL`) z automatyczną rotacją i archiwizacją `.gz` w `.local/logs/szukaj.log` (`mcp/app_logging.py`).
- Instrukcja dla agenta wdrażającego MCP Search: `docs/instrukcja-integracji-mcp-search.md`. Na teraz dla MCP stałe adresy HTTP; `szukaj.dom` działa dla strony WWW. Dokumentacja obejmuje testy połączenia, kontraktu i odpowiedzi modelu w aplikacji.
- Przykład klienta z instrukcji sprawdzony bez wyszukiwania na działającej lokalnej usłudze: initialize/tools/list PASS, protokół 2025-11-25. Nie zastępuje to odbioru integracji przez WirralAI.
- Stabilne 1.0.0 czeka na pozytywną opinię WirralAI o integracji MCP (`R1`), zgodnie z decyzją Mariusza. Akceptacji jeszcze nie otrzymano.
- Obowiązkowa kontrola przed commitem: `python3 scripts/check_project.py` (Ruff, tracked-files, backend 55/55, frontend 19/19, build, diff, staged-diff) — wszystko PASS.
- Zamknięte `S1` (`R2`): nowy `SEARXNG_SECRET` ustawiony przez operatora i start potwierdzony; stary sekret pozostaje w historii.
- Do potwierdzenia po przebudowie obrazu z najnowszymi zmianami: `R3` (UID 10001 w kontenerze).
