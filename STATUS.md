# STATUS.md

Aktualizacja: 2026-10-18.

- Wykonujemy audyt z docs/AUDYT-2026-10-17.md na docs/audyt-2026-10-17. Każdy etap kończy się testami, commitem i lokalnym merge do develop; następnie powrót na gałąź audytu. Bez push.
- Etapy kodu zakończone w tej sesji: S1, S2, Q1, S3, K3, S4, K1, K4. Ostatni: K4 — Wspólne przykłady i testy transportu MCP.
- docs/contract/web_search.example.json zawiera syntetyczne ok/empty/error. Trzy testy pełnych sesji initialize → tools/list → tools/call porównują sparsowany blok tekstowy JSON ze wspólnym plikiem. Testy klienta WirralAI pozostają do uruchomienia po jego stronie.
- Kontrole: backend 39/39, frontend 17/17, build i diff-check PASS. Testy offline; rzeczywistego wdrożenia nie potwierdzano.
- Otwarta czynność operatora S1: nowy SEARXNG_SECRET i start SearXNG; nie używać starej wartości z historii. Brak zgody na przepisywanie historii GitHuba.
- MCP nadal wymaga zgodnego kontraktu z wirralAI; punkty K1–K4 weryfikujemy na wspólnych przykładach.
