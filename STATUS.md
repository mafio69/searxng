# STATUS.md

Aktualizacja: 2026-10-17

## Stan projektu

- **MVP 1.0** — zakres zatwierdzony przez Mariusza; stabilizacja bez nowych funkcji.
- Interfejs React, wspólny backend Python dla API i MCP, SearXNG oraz opcjonalny Perplexity wyłącznie po pustym wyniku lub błędzie SearXNG.
- Dwa kontenery działają w sieci Docker `ai`; web: `http://127.0.0.1:8890/`, MCP: `/mcp`.

## Weryfikacja

- Backend: **20/20 testów** (walidacja, fallback, limity, MCP tools/call z atrapami).
- Frontend: **17/17 testów** (wyszukiwanie, historia, błędy i spóźnione odpowiedzi).
- Build Vite i `git diff --check`: PASS.
- Smoke HTTP działającego obrazu: PASS. Najnowsze poprawki kodu nie zostały jeszcze wdrożone.
- Mariusz potwierdził działające wyszukiwanie w przeglądarce. Agent nie wykonywał rzeczywistych zapytań podczas stabilizacji.

## Poprawki review

- Naprawiono walidację Host, nietypowy URL i dostęp klawiaturą do mobilnej historii.
- Smoke najnowszego kodu na testowym porcie 8891: PASS; kontenery wymagają przebudowania po poprawkach.
- Ostateczna decyzja Mariusza: zachować obecny wygląd, w tym kontrast. Uwaga o kontraście świadomie nieprzyjęta.
- Commit `d5336b6` wysłany do PR #1 na GitHub; bez merge i wdrożenia.

## Decyzje i ograniczenia

- Brak nowych funkcji, nowych zależności i zmian wersji podczas stabilizacji.
- Testy i kontrole jakości uruchamiamy bezpośrednio według `README.md` i `REPO.md`, zgodnie z zasadami `AGENTS.md`.
- Agent nie ma dostępu do socketu Docker; operacje wymagające sudo wykonuje Mariusz.
- Licznik Perplexity pozostaje nietrwały i niesynchronizowany; aplikacja nie ma logowania. Szczegóły w README.
- Ostrzeżenie deprecacji Starlette TestClient/HTTPX nie blokuje testów; nie zmieniano zależności.
- Lokalnie brak `origin/develop`; praca na `feat/search-ui`. Agent ma zgodę na commit po zielonych testach; push czeka na osobne polecenie.

## Stan na koniec sesji

- Rzeczywiste MCP z hosta zwraca wyniki SearXNG (3 w 0,78 s i 5 w 1,6 s), bez Perplexity.
- VirralAI w kontenerze `slim_ovh_ai_app` zgłaszało `dns_failed` dla `mcp-search:8000`; nie potwierdzono jeszcze wspólnej sieci i aliasu. Oba kontenery według Mariusza działają na Latitude.
- `tests/http/server-diagnostic.http` pozostaje niezacommitowanym plikiem diagnostycznym.
- Końcowy zapis dokumentacji zostaje lokalnie; kolejny push wymaga polecenia.

## Następny krok

1. Przebudować obraz po poprawkach: `sudo docker compose up -d --build`.
2. Powtórzyć `python3 scripts/smoke_test.py` i próbę w przeglądarce.
3. Zweryfikować sieci i aliasy `slim_ovh_ai_app` oraz `mcp-search`, a potem inicjalizację MCP z PHP; nie traktować problemu DNS jako naprawionego.
