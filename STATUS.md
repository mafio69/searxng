# STATUS.md

Aktualizacja: 2026-10-24.

- Wydano stabilną wersję `1.0.0` (Production Ready MVP) na zlecenie Mariusza: gałąź `release/1.0.0` scommitowana i wypchnięta do `origin/release/1.0.0`.
- Zweryfikowano działanie protokołu MCP Streamable HTTP na żywo oraz dodano kompletny zestaw testów w `http/mcp-test.http` (w tym test wywołania `web_search` dla zapytania „Słuchawki do 500zł” oraz skrypt CLI `scripts/test_mcp_client.py`).
- Rozwiązano problem botdetection SearXNG w kontenerze (`X-Forwarded-For: 127.0.0.1`) i poprawiono resolver logów kontenerowych w `mcp/app_logging.py`.
- Zaktualizowano `opencode.json` (poluzowanie reguł uprawnień).
- Główna wizytówka na GitHubie (`README.md`) w języku angielskim z odznakami 1.0.0, bramki jakości i technologii; pełna dokumentacja w języku polskim w `README_PL.md`.
- Strona `szukaj.dom` (repozytorium `szukaj`) działa w sieci domowej pod `http://szukaj.dom/` (Pi-hole `*.dom` → serwer, Traefik → `127.0.0.1:8000`, `SEARCH_ALLOWED_HOSTS` z `szukaj.dom`); tytuł w `web/index.html` i marka w `web/src/App.jsx` ustawione na `szukaj.dom`, pakiet UI `szukaj-ui`, usługa silnika w `docker-compose.yml` nazwana `szukaj`.
- Instrukcja dla agenta wdrażającego MCP Search: `docs/instrukcja-integracji-mcp-search.md`.
- Obowiązkowa kontrola przed commitem: `python3 scripts/check_project.py` (Ruff, tracked-files, backend 55/55, frontend 19/19, build, diff, staged-diff) — wszystko PASS.
- Następny priorytet: Pull Request z `release/1.0.0` do `master` i wdrożenie produkcyjne.
