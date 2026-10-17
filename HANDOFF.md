# HANDOFF.md — audyt 2026-10-17

Aktualizacja: 2026-10-18.

- Pracujemy do końca audytu na docs/audyt-2026-10-17, zgodnie z poleceniem Mariusza. Każdy punkt: pełne testy → commit → lokalny merge do develop → powrót na tę samą gałąź. Bez push.
- Ostatni etap: K2 — Walidacja zapytań MCP. Narzędzie i jego schemat ograniczają query do 1–1000 znaków Unicode; białe znaki są odrzucane przed dostawcami. Testy sprawdzają puste/1001 znaków bez HTTP oraz akceptację 1000 polskich znaków. UI/API zachowuje udokumentowany limit 500.
- Kontrole: backend 41/41, frontend 17/17, build i diff-check PASS. Brak rzeczywistych zapytań do wyszukiwarek.
- Etapy kodu zakończone w tej sesji: S1, S2, Q1, S3, K3, S4, K1, K4, K2. Stan i ograniczenia zapisano też w docs/AUDYT-2026-10-17.md.
- S1 wymaga ustawienia przez operatora nowej wartości SEARXNG_SECRET i potwierdzenia startu; starego klucza z historii nie używać. Nie czytać ani nie ujawniać wartości. Historia pozostaje nierotowana przez agenta.
- Lokalny dawny searxng-settings.yml zachowany bez odczytu i bez modyfikacji, ignorowany przez Git. Diagnostyka HTTP w .local/tmp/http/.
- Nie usuwać gałęzi audytu do zakończenia wszystkich punktów i udanego, osobno zatwierdzonego pushu develop.
