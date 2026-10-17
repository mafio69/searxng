# STATUS.md

Aktualizacja: 2026-10-18.

- Wykonujemy audyt z docs/AUDYT-2026-10-17.md na docs/audyt-2026-10-17. Każdy etap kończy się testami, commitem i lokalnym merge do develop; następnie powrót na gałąź audytu. Bez push.
- Etapy kodu zakończone w tej sesji: S1. Ostatni: S1 — Oddzielenie klucza od wersjonowanej konfiguracji.
- Compose montuje pusty publiczny szablon i wymaga lokalnego SEARXNG_SECRET. Dawny plik usunięto wyłącznie ze śledzenia, bez odczytu i zmiany lokalnej wartości. Rotacja klucza i rzeczywisty start pozostają do potwierdzenia przez operatora; stara historia nie została usunięta.
- Kontrole: backend 22/22, frontend 17/17, build i diff-check PASS. Testy offline; rzeczywistego wdrożenia nie potwierdzano.
- Otwarta czynność operatora S1: nowy SEARXNG_SECRET i start SearXNG; nie używać starej wartości z historii. Brak zgody na przepisywanie historii GitHuba.
- MCP nadal wymaga zgodnego kontraktu z wirralAI; punkty K1–K4 weryfikujemy na wspólnych przykładach.
