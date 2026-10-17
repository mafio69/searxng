# STATUS.md

Aktualizacja: 2026-10-18.

- Wykonujemy audyt z docs/AUDYT-2026-10-17.md na docs/audyt-2026-10-17. Każdy etap kończy się testami, commitem i lokalnym merge do develop; następnie powrót na gałąź audytu. Bez push.
- Etapy kodu zakończone w tej sesji: S1, S2, Q1, S3, K3, S4, K1. Ostatni: K1 — Jednoznaczny wynik pusty i awaria.
- Dodano status ok/empty/error. Poprawny brak wyników ma source null, results [] i errors []; awaria bez wyników zawsze error. Udany fallback ma ok bez errors. API oddaje 502 przy awarii. Dokumentacja zawiera nowe stany i negocjację protokołu.
- Kontrole: backend 36/36, frontend 17/17, build i diff-check PASS. Testy offline; rzeczywistego wdrożenia nie potwierdzano.
- Otwarta czynność operatora S1: nowy SEARXNG_SECRET i start SearXNG; nie używać starej wartości z historii. Brak zgody na przepisywanie historii GitHuba.
- MCP nadal wymaga zgodnego kontraktu z wirralAI; punkty K1–K4 weryfikujemy na wspólnych przykładach.
