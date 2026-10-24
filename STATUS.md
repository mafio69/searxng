# STATUS.md

Aktualizacja: 2026-10-23.

- Wydano stabilną wersję `1.0.0` (Production Ready MVP) na zlecenie Mariusza: wersja podbita w `web/package.json`, `web/package-lock.json`, `CHANGELOG.md`, `README.md` i `README_PL.md`.
- Główna wizytówka na GitHubie (`README.md`) w języku angielskim z odznakami 1.0.0, bramki jakości i technologii; pełna dokumentacja w języku polskim w `README_PL.md`.
- Strona `szukaj.dom` (repozytorium `szukaj`) działa w sieci domowej pod `http://szukaj.dom/` (Pi-hole `*.dom` → serwer, Traefik → `127.0.0.1:8000`, `SEARCH_ALLOWED_HOSTS` z `szukaj.dom`); tytuł w `web/index.html` i marka w `web/src/App.jsx` ustawione na `szukaj.dom`, pakiet UI `szukaj-ui`, usługa silnika w `docker-compose.yml` nazwana `szukaj`.
- Wykonano wszystkie zadania kodu i dokumentacji z planu `docs/release-1.0.0-plan.md`, poprawki code review PR #2, ostrzeżenia GitGuardian/Qodana oraz systemową obsługę błędów (`APP_ENV`: przyjazne „Błąd. Przepraszamy...” na `prod`, szczegóły diagnostyczne na `dev`, React `ErrorBoundary`) i logowanie od `WARNING` wzwyż (`LOG_LEVEL`) z automatyczną rotacją i archiwizacją `.gz` w `.local/logs/szukaj.log` (`mcp/app_logging.py`).
- Instrukcja dla agenta wdrażającego MCP Search: `docs/instrukcja-integracji-mcp-search.md`.
- Obowiązkowa kontrola przed commitem: `python3 scripts/check_project.py` (Ruff, tracked-files, backend 55/55, frontend 19/19, build, diff, staged-diff) — wszystko PASS.
- Zamknięte `S1` (`R2`): nowy `SEARXNG_SECRET` ustawiony przez operatora i start potwierdzony; stary sekret pozostaje w historii.
- Do potwierdzenia po przebudowie obrazu przez operatora z najnowszymi zmianami: `R3` (UID 10001 w kontenerze).
