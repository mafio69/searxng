# HANDOFF.md — audyt 2026-10-17

Aktualizacja: 2026-10-18.

- Pracujemy do końca audytu na docs/audyt-2026-10-17, zgodnie z poleceniem Mariusza. Każdy punkt: pełne testy → commit → lokalny merge do develop → powrót na tę samą gałąź. Bez push.
- Ostatni etap: S2 — Asynchroniczne wyszukiwanie. web_search i obaj dostawcy używają async/await oraz httpx.AsyncClient. Adapter API oczekuje na tę samą asynchroniczną usługę. Test sprawdza dwa opóźnienia po 1 s, wspólny czas poniżej 1,5 s oraz możliwość uruchomienia obu żądań przed ich zakończeniem.
- Kontrole: backend 23/23, frontend 17/17, build i diff-check PASS. Brak rzeczywistych zapytań do wyszukiwarek.
- Etapy kodu zakończone w tej sesji: S1, S2. Stan i ograniczenia zapisano też w docs/AUDYT-2026-10-17.md.
- S1 wymaga ustawienia przez operatora nowej wartości SEARXNG_SECRET i potwierdzenia startu; starego klucza z historii nie używać. Nie czytać ani nie ujawniać wartości. Historia pozostaje nierotowana przez agenta.
- Lokalny dawny searxng-settings.yml zachowany bez odczytu i bez modyfikacji, ignorowany przez Git. Diagnostyka HTTP w .local/tmp/http/.
- Nie usuwać gałęzi audytu do zakończenia wszystkich punktów i udanego, osobno zatwierdzonego pushu develop.
