# STATUS.md

Aktualizacja: 2026-10-18.

- Wykonujemy audyt z docs/AUDYT-2026-10-17.md na docs/audyt-2026-10-17. Każdy etap kończy się testami, commitem i lokalnym merge do develop; następnie powrót na gałąź audytu. Bez push.
- Etapy kodu zakończone w tej sesji: S1, S2, Q1. Ostatni: Q1 — Atomowy limit prób Perplexity.
- Limit jest rezerwowany pod krótką blokadą przed żądaniem HTTP. Nie zwracamy rezerwacji po błędzie ani anulowaniu, bo koszt po stronie dostawcy może już powstać. Test 100 równoległych prób przy limicie 50 potwierdza dokładnie 50 żądań. Licznik nadal jest lokalny dla procesu i resetuje się po restarcie; nie deklarujemy trwałego budżetu.
- Kontrole: backend 25/25, frontend 17/17, build i diff-check PASS. Testy offline; rzeczywistego wdrożenia nie potwierdzano.
- Otwarta czynność operatora S1: nowy SEARXNG_SECRET i start SearXNG; nie używać starej wartości z historii. Brak zgody na przepisywanie historii GitHuba.
- MCP nadal wymaga zgodnego kontraktu z wirralAI; punkty K1–K4 weryfikujemy na wspólnych przykładach.
