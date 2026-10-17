# HANDOFF.md — pałeczka między sesjami

## Stan po uporządkowaniu Git — 2026-10-17

- Lokalny develop zawiera w całości feat/search-ui oraz dokument audytu docs/AUDYT-2026-10-17.md. Scalenie 14e7c6a zostało wykonane lokalnie; nie wykonano push develop.
- Nie wdrożono żadnej poprawki z audytu. Nowy interfejs, wcześniejsze review i dokumentacja narzędzi są już częścią develop.
- Mariusz zatwierdził zapis pełnej kolejności w GIT-FLOW.md: branch z develop → zadanie → pełne testy → commit → lokalny merge do develop → weryfikacja stanu develop → oczekiwanie na zgodę na push → push wyłącznie develop → usunięcie lokalnej gałęzi po udanym pushu.
- Gałęzie feat/search-ui i codex/audit-search-hardening pozostają zachowane do spełnienia warunku udanego pushu develop. Gałąź porządków codex/git-handoff-cleanup podlega tej samej zasadzie.
- Lokalny plik diagnostyczny zachowano jako .local/tmp/http/server-diagnostic.http. Nie jest częścią publikacji.
- Kontrola porządków: backend 20/20, frontend 17/17, build Vite i diff-check — PASS. Nowe zmiany dokumentacji sprawdzono przed commitem pod kątem sekretów.

## Ograniczenia i następny krok

- Wyjątek fire zatwierdzony przez Mariusza: korekta GIT-FLOW.md jest naprawą wcześniejszego opisu zasad, więc wykonujemy ją bezpośrednio na develop. Wyjątek obejmuje tę korektę i commit dokumentacji; nie obejmuje pomijania testów ani pushu.
- Porządki dokumentacji scalono lokalnie do develop w e3f7a4d. Czekamy na decyzję Mariusza o dalszej pracy. Nie wykonywać push, wdrożenia ani kolejnych napraw audytu w ramach tej korekty.
- Kontrola historii wcześniej wskazała historycznie śledzony secret_key SearXNG. Nie ujawniać wartości. Usunięcie pliku z kolejnych commitów nie usuwa sekretu ze starej historii; rotacja i ewentualne czyszczenie historii pozostają nierozwiązane.
- Nie czytać .env, kluczy ani katalogów sekretów. Dane robocze wyłącznie w ignorowanym .local/, bez dostępu do .local/secret/.
- Wymagane testy: PYTHONPATH=.local/python PYTHONPYCACHEPREFIX=.local/cache/pycache python3 -m unittest discover -s tests; npm --prefix web test; npm --prefix web run build; git diff --check. TestClient wymagał wykonania poza sandboxem. Testy nie wywołują rzeczywistych dostawców.
- Nie zmieniać zaakceptowanego przez właściciela wyglądu UI. Integracja MCP na hoście działała, ale stan wdrożenia i połączenia kontenerów wymaga osobnej weryfikacji; nie przedstawiać wyników historycznych jako nowego testu.
