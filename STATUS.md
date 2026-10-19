# STATUS.md

Aktualizacja: 2026-10-19.

- Wykonano wszystkie zadania kodu i dokumentacji z planu `docs/release-1.0.0-plan.md`: skaner śledzonych plików (`scripts/check_tracked_files.py`), poprawki dokumentacji `D1–D8`, optymalizacje serwera i Compose `O1–O5` (współdzielony `httpx.AsyncClient`, timeouty SearXNG `3.0`/`8.0` s, `healthcheck` `/healthz`, rotacja logów `json-file`) oraz nagłówki `W3`.
- Instrukcja dla agenta wdrażającego MCP Search: `docs/instrukcja-integracji-mcp-search.md`. Na teraz stałe adresy HTTP; `wyszukaj.dom` jest wyłącznie planowane.
- Stabilne `1.0.0` czeka na pozytywną opinię WirralAI o integracji MCP (`R1`), zgodnie z decyzją Mariusza.
- Obowiązkowa kontrola przed commitem: `python3 scripts/check_project.py` (Ruff, tracked-files, backend 50/50, frontend 18/18, build, diff, staged-diff) — wszystko PASS.
- Zamknięte `S1` (`R2`): nowy `SEARXNG_SECRET` ustawiony lokalnie przez operatora i start kontenera potwierdzony; stary sekret pozostaje w historii.
- Do potwierdzenia we wdrożeniu po przebudowie obrazu z najnowszymi zmianami: `R3` (UID 10001 w kontenerze) oraz `R4` (`python3 scripts/smoke_test.py`).
