# STATUS.md

Aktualizacja: 2026-10-16

## Stan projektu

- **MVP 1.0** — zakres zatwierdzony przez Mariusza; stabilizacja bez nowych funkcji.
- Interfejs React, wspólny backend Python dla API i MCP, SearXNG oraz opcjonalny Perplexity wyłącznie po pustym wyniku lub błędzie SearXNG.
- Dwa kontenery działają w sieci Docker `ai`; web: `http://127.0.0.1:8890/`, MCP: `/mcp`.

## Weryfikacja

- Backend: **17/17 testów** (walidacja, fallback, limity, MCP tools/call z atrapami).
- Frontend: **13/13 testów** (wyszukiwanie, historia, błędy i spóźnione odpowiedzi).
- Build Vite i `git diff --check`: PASS.
- Smoke HTTP działającego obrazu: PASS. Najnowsze poprawki kodu nie zostały jeszcze wdrożone.
- Mariusz potwierdził działające wyszukiwanie w przeglądarce. Agent nie wykonywał rzeczywistych zapytań podczas stabilizacji.

## Decyzje i ograniczenia

- Brak nowych funkcji, nowych zależności i zmian wersji podczas stabilizacji.
- W repo nie używamy `dxrun` — decyzja Mariusza.
- Agent nie ma dostępu do socketu Docker; operacje wymagające sudo wykonuje Mariusz.
- Licznik Perplexity pozostaje nietrwały i niesynchronizowany; aplikacja nie ma logowania. Szczegóły w README.
- Ostrzeżenie deprecacji Starlette TestClient/HTTPX nie blokuje testów; nie zmieniano zależności.
- Lokalnie brak `origin/develop`; praca na `feat/search-ui`. Agent ma zgodę na commit po zielonych testach; push czeka na osobne polecenie.

## Następny krok

1. Przebudować obraz po poprawkach: `sudo docker compose up -d --build`.
2. Powtórzyć `python3 scripts/smoke_test.py` i próbę w przeglądarce.
3. Przed publikacją zweryfikować integrację z wybranym klientem AI.
