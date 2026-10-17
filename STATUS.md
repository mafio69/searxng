# STATUS.md

Aktualizacja: 2026-10-18.

- Wykonujemy audyt z docs/AUDYT-2026-10-17.md na docs/audyt-2026-10-17. Każdy etap kończy się testami, commitem i lokalnym merge do develop; następnie powrót na gałąź audytu. Bez push.
- Etapy kodu zakończone w tej sesji: S1, S2, Q1, S3. Ostatni: S3 — Opcjonalna kontrola dostępu MCP.
- MCP_AUTH_TOKEN chroni /mcp i jego metody GET/POST/DELETE stałoczasowym porównaniem nagłówka Bearer. Dotyczy pełnej aplikacji i osobnego entrypointu MCP. Brak konfiguracji zachowuje poprzednie działanie; przeglądarkowe API i statyczne UI nie otrzymują ani nie wymagają tego sekretu. Smoke potrafi przekazać wartość z własnego środowiska wyłącznie do MCP.
- Kontrole: backend 30/30, frontend 17/17, build i diff-check PASS. Testy offline; rzeczywistego wdrożenia nie potwierdzano.
- Otwarta czynność operatora S1: nowy SEARXNG_SECRET i start SearXNG; nie używać starej wartości z historii. Brak zgody na przepisywanie historii GitHuba.
- MCP nadal wymaga zgodnego kontraktu z wirralAI; punkty K1–K4 weryfikujemy na wspólnych przykładach.
