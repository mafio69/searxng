# HANDOFF.md — audyt 2026-10-17

Aktualizacja: 2026-10-18.

- NASTĘPNY AGENT: plan doprowadzenia do 1.0.0 bez nowych funkcji — docs/release-1.0.0-plan.md (blokery R1–R4, poprawki dokumentacji D1–D8, kontrola UI W1–W3, optymalizacje O1–O7 ze źródłami). Plik nie jest jeszcze w commicie. Bieżąca gałąź chore/secret-scan-and-s1-s5 zawiera cudze niezacommitowane zmiany — nie mieszać z zadaniami planu.

- Dokumentacja integracji K4: docs/instrukcja-integracji-mcp-search.md jest punktem startowym dla agenta aplikacji. Zawiera ustalone adresy HTTP host/Docker, sesję MCP, przykład klienta 1.30.0, trzy stany i testy całej pętli model–narzędzie–UI. Domena wyszukaj.dom pozostaje planowana; nie wdrażano DNS/proxy. Bez nowych zależności, rzeczywistych wyszukiwań i zmian drugiego repozytorium.
- Weryfikacja instrukcji: składnia przykładu Pythona, JSON zgodny ze wspólnymi fixtures i odsyłacze lokalne PASS. Dokładny przykład uruchomiono na lokalnym działającym MCP bez --live: initialize/tools/list PASS, protocol 2025-11-25. Pełne kontrole: Ruff, backend 46/46, frontend 18/18, build i diff-check PASS. Nie wykonano rzeczywistego wyszukiwania ani odbioru z WirralAI.

- Pracujemy na docs/audyt-2026-10-17. Każdy punkt: testy → commit → lokalny merge do develop → powrót. Bez push i bez usuwania gałęzi.
- Q3 zakończone w kodzie: rozdzielone importy, nazwane walidatory w Python/JS. Ruff 0.17.1 jest przypięty w requirements-dev.txt, zainstalowany wyłącznie w ignorowanym .local/tools/ruff i włączony do python3 scripts/check_project.py.
- Mariusz zatwierdził instalację Ruff, stałe kontrole przed commitem i allow używania przez agentów. Zapis w AGENTS.md, bez zmiany opencode ani konfiguracji uprawnień. Domyślnie bez --fix; chronione ścieżki wykluczone.
- Kontrole: Ruff PASS, backend 46/46, frontend 18/18, build i diff-check roboczy/staged PASS. Testy sprawdzają także zatrzymanie kontroli po błędzie lintingu i braku narzędzia. Brak rzeczywistych zapytań do wyszukiwarek.
- Raport dla WirralAI: docs/contract/MCP-COMPATIBILITY.md. Biblioteka MCP 1.30.0; wszystkie cztery wersje initialize i trzy syntetyczne stany narzędzia potwierdzone testami pełnego transportu MCP.
- Etapy kodu wykonane: S1–S5, K1–K4, Q1–Q3 (w tym uzupełnienie UI dla empty). Nie oznacza to zakończenia poniższych kontroli operatora/integracji.
- S1: operator musi ustawić nowy SEARXNG_SECRET i potwierdzić start. Stary klucz pozostaje w historii Git; nie używać go. Nie czytano ani nie zmieniano rzeczywistego .env i wartości sekretów. Nie przepisano historii.
- S5: runtime UID/build niepotwierdzone — brak dostępu do docker.sock. Obraz deklaruje UID 10001:10001; SearXNG ma stały digest. Nie uruchamiano sudo ani wdrożenia.
- K1/K4: klient WirralAI musi wykonać własne testy wspólnego docs/contract/web_search.example.json; nie zmieniano drugiego repozytorium.
- Warunek stabilnego wydania 1.0.0 ustalony przez Mariusza: wymagana jest pozytywna opinia projektu WirralAI po teście integracji MCP. Status: oczekujemy. Zielone testy searxng nie zastępują tej akceptacji; pozostałe kontrole wdrożenia nadal obowiązują.
- Q1: licznik Perplexity jest atomowy tylko w jednym procesie, nietrwały; restart zeruje limit.
- Lokalny dawny searxng-settings.yml pozostaje ignorowany, bez odczytu i modyfikacji. Diagnostyka HTTP w .local/tmp/http/. Nie czytać .local/secret/.
