# STATUS.md

Aktualizacja: 2026-10-19.

- Strona „Szukaj” działa w sieci domowej pod `http://szukaj.dom/` (Pi-hole `*.dom` → serwer, Traefik → `127.0.0.1:8000`, `SEARCH_ALLOWED_HOSTS` z `szukaj.dom`). Sprawdzone 2026-10-19: strona 200, `/api/search` 200 ze źródłem SearXNG. Dla MCP nadal stałe adresy HTTP.

- Instrukcja dla agenta wdrażającego MCP Search: docs/instrukcja-integracji-mcp-search.md. Na teraz dla MCP stałe adresy HTTP; `szukaj.dom` działa dla strony WWW. Dokumentacja obejmuje testy połączenia, kontraktu i odpowiedzi modelu w aplikacji.
- Przykład klienta z instrukcji sprawdzony bez wyszukiwania na działającej lokalnej usłudze: initialize/tools/list PASS, protokół 2025-11-25. Nie zastępuje to odbioru integracji przez WirralAI.

- Stabilne 1.0.0 czeka na pozytywną opinię WirralAI o integracji MCP, zgodnie z decyzją Mariusza. Akceptacji jeszcze nie otrzymano; nadal wymagane są pozostałe otwarte kontrole wdrożenia.

- Etapy kodu audytu S1–S5, K1–K4, Q1–Q3 wykonane. Każdy punkt: testy, commit i lokalny merge do develop; powrót na gałąź audytu. Bez push.
- Obowiązkowa kontrola przed commitem: python3 scripts/check_project.py. Ruff 0.17.1 lokalnie, stała zgoda dla agentów w AGENTS.md.
- Ruff PASS, backend 46/46, frontend 18/18, build i diff-check roboczy/staged PASS. Testy offline.
- Raport dla WirralAI: docs/contract/MCP-COMPATIBILITY.md; wspólne trzy przykłady JSON przeszły pełny transport MCP. Testy klienta WirralAI i rzeczywiste wdrożenie pozostają niepotwierdzone.
- Otwarte S1: nowy SEARXNG_SECRET i start operatora; stary sekret pozostaje w historii.
- Otwarte S5: potwierdzenie UID i budowy działającego obrazu — brak dostępu do Dockera w bieżącej sesji.
