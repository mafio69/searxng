# STATUS.md

Aktualizacja: 2026-10-17

## Stan projektu

- MVP 1.0: React, backend Python, SearXNG i opcjonalny Perplexity wyłącznie po pustym wyniku lub błędzie źródła podstawowego.
- Lokalny develop zawiera cały feat/search-ui i dokument audytu. Nie wykonano push develop.
- Poprawki audytu nie zostały wdrożone. Zakres i kryteria: docs/AUDYT-2026-10-17.md.
- Śledzone pliki są zapisane w Git; diagnostykę HTTP zachowano lokalnie w .local/tmp/http/.

## Weryfikacja

- Przy porządkach ponownie: backend 20/20, frontend 17/17, build Vite i diff-check — PASS. Skan nowych zmian dokumentacji przed commitem.
- Wyniki nie potwierdzają wdrożenia ani bezpieczeństwa starej historii. Historyczne wykrycie secret_key pozostaje nierozwiązane.
- Testy i kontrole uruchamiamy bezpośrednio według README.md i REPO.md, zgodnie z AGENTS.md.

## Git i następny krok

- Gałąź zadania zawsze z develop; po pracy i zielonych testach commit oraz lokalny merge do develop.
- Push wyłącznie develop, po zgodzie Mariusza. Lokalną gałąź usuwa się dopiero po udanym pushu.
- Istniejące scalone gałęzie zachowane do spełnienia tego warunku.
- Przedstawiono potrzebę doprecyzowania GIT-FLOW.md; zmiana jego treści czeka na zatwierdzenie.
- Dalsze naprawy audytu, testy rzeczywistych usług i wdrożenie wymagają wznowienia zadania przez Mariusza.
