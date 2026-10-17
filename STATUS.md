# STATUS.md

Aktualizacja: 2026-10-18.

- Wykonujemy audyt z docs/AUDYT-2026-10-17.md na docs/audyt-2026-10-17. Każdy etap kończy się testami, commitem i lokalnym merge do develop; następnie powrót na gałąź audytu. Bez push.
- Etapy kodu zakończone w tej sesji: S1, S2. Ostatni: S2 — Asynchroniczne wyszukiwanie.
- web_search i obaj dostawcy używają async/await oraz httpx.AsyncClient. Adapter API oczekuje na tę samą asynchroniczną usługę. Test sprawdza dwa opóźnienia po 1 s, wspólny czas poniżej 1,5 s oraz możliwość uruchomienia obu żądań przed ich zakończeniem.
- Kontrole: backend 23/23, frontend 17/17, build i diff-check PASS. Testy offline; rzeczywistego wdrożenia nie potwierdzano.
- Otwarta czynność operatora S1: nowy SEARXNG_SECRET i start SearXNG; nie używać starej wartości z historii. Brak zgody na przepisywanie historii GitHuba.
- MCP nadal wymaga zgodnego kontraktu z wirralAI; punkty K1–K4 weryfikujemy na wspólnych przykładach.
