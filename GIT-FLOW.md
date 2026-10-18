# GIT-FLOW.md — zasady pracy Git

## Złota zasada

Przed każdym commitem pełny zestaw testów wymagany przez repozytorium musi być zielony. Czerwone testy, linting, typecheck lub skaner bezpieczeństwa blokują commit i push.

Obowiązkowe polecenie przed commitem: `python3 scripts/check_project.py`. Obejmuje Ruff, testy backendu i frontendu, build oraz kontrolę zmian Git. Brak narzędzia lub niezerowy wynik blokuje commit. Stała zgoda na uruchamianie tej kontroli i Ruff jest zapisana w AGENTS.md.

## Obowiązkowa kolejność zwykłego zadania

1. Przeczytaj: README.md, REPO.md, STATUS.md, CHANGELOG.md, AGENTS.md i na końcu HANDOFF.md, jeśli istnieją.
2. Zacznij od aktualnego lokalnego develop. Przed rozpoczęciem pracy sprawdź jego zgodność z origin/develop. Jeśli zdalny develop nie istnieje albo stan jest rozbieżny, zgłoś to Mariuszowi; nie wybieraj samodzielnie innej podstawy.
3. Utwórz nową gałąź zadania z develop. Nie zaczynaj zadania z master ani ze starej gałęzi zadania.
4. Wykonaj wyłącznie zlecone zadanie na tej gałęzi.
5. Uruchom pełny wymagany zestaw testów i kontroli. Po zielonym wyniku wykonaj zatwierdzony commit na gałęzi zadania.
6. Scal tę gałąź lokalnie do develop. Nie twórz dodatkowej gałęzi tylko po to, żeby pośrednio scalić gałąź wskazaną przez Mariusza. Konflikty rozwiąż bez utraty cudzej pracy.
7. Zweryfikuj wynik scalenia na develop. Wszystkie wymagane kontrole muszą być zielone dla stanu przeznaczonego do wysłania; jeżeli scalenie zmieniło testowany stan, powtórz wymagane kontrole.
8. Zatrzymaj się i czekaj na wyraźną zgodę Mariusza na push. Zgoda na zadanie, commit lub lokalny merge nie jest zgodą na push.
9. Po uzyskaniu zgody wykonaj wyłącznie git push origin develop. Nie pushuj gałęzi zadania ani master.
10. Dopiero po udanym pushu develop i potwierdzeniu, że obejmuje zmiany gałęzi zadania, usuń tę gałąź lokalnie bez wymuszania. Nie usuwaj jej przed pushem ani po nieudanym pushu. Nie czekaj z tym do wdrożenia.

Zdalnych gałęzi nie usuwaj bez osobnej zgody. Lokalnego master nie używaj do pracy nad zadaniem; master przyjmuje zmiany wyłącznie przez PR na GitHub z zielonymi wymaganymi kontrolami. PR, jego scalenie i wdrożenie wymagają osobnej zgody.

## Sprzeczne polecenia i wyjątki

1. Gdy polecenie jest sprzeczne z tym flow, nie wykonuj sprzecznego kroku za pierwszym razem. Powiedz wprost: „Mariusz, to jest niezgodne z Git Flow”, wskaż konkretną zasadę i omów konsekwencje.
2. Polemizuj, jeśli widzisz ryzyko lub błąd; nie przytakuj automatycznie. Poczekaj na dobry powód i świadome, jednoznaczne zatwierdzenie konkretnego wyjątku przez Mariusza.
3. Wyjątek dotyczy tylko wskazanej czynności i zadania. Nie zmienia domyślnego flow na przyszłość. Uzasadnienie i zakres wyjątku zapisz w HANDOFF.md.
4. Tylko Mariusz może nadać status fire. Jawne oznaczenie zadania jako fire lub świadoma zgoda Mariusza pozwala pracować i commitować bezpośrednio na develop, bez gałęzi zadania. Agent nie nadaje sobie tego statusu.
5. Sam status fire nie znosi obowiązku zielonych testów, ochrony sekretów ani osobnej zgody na push. Odstępstwa od kontroli jakości wymagają odrębnej, wyraźnej decyzji Mariusza z uzasadnieniem.

## W trakcie zadania

1. Wykonuj tylko zakres zlecony przez Mariusza.
2. Nie dodawaj zależności, nie aktualizuj pakietów i nie refaktoryzuj pobocznych elementów bez zgody.
3. Nie odczytuj ani nie modyfikuj sekretów oraz nie analizuj dotenvx i skryptów środowiska — obowiązuje AGENTS.md.
4. Testy i kontrole jakości uruchamiaj poleceniami opisanymi w README.md i REPO.md, zgodnie z zasadami AGENTS.md.
5. Sekrety, klucze API, tokeny, rzeczywiste pliki środowiska i prywatne dane nie mogą trafić do commitu ani na GitHub. Przed commitem i pushem sprawdź dokładny zakres publikowanych zmian bez ujawniania wartości sekretów. Nie używaj zbiorczego dodawania plików bez ich weryfikacji.

## Commit i ochrona pracy

1. Nie commituj przy błędach testów lub kontroli jakości.
2. Commit w zleconym zadaniu wykonuj samodzielnie po zielonych testach, chyba że Mariusz wyraźnie go wstrzyma. Nie pytaj o każdy commit ponownie.
3. Nie zmieniaj git config user.name ani git config user.email.
4. Nie przywracaj plików bezpieczeństwa przez git restore, git checkout --, git reset --hard ani podobne mechanizmy. Nie kasuj cudzych zmian, żeby uzyskać czyste drzewo robocze.

5. Podpisuj commit własną tożsamością i trailerem Co-Authored-By z nazwą używanego agenta/modelu oraz jego adresem noreply. Nie podszywaj się pod właściciela ani inny model.

## Seria punktów jednego audytu

Na wyraźne polecenie Mariusza bieżący audyt wykonujemy do końca na docs/audyt-2026-10-17. Każdy punkt osobno kończy się pełnymi testami, commitem i lokalnym scaleniem do develop, a następnie agent wraca na tę samą gałąź audytu do kolejnego punktu. Gałąź pozostaje do końca audytu; push nadal dotyczy tylko develop i czeka na osobne polecenie. To zatwierdzona organizacja etapów jednego zadania, nie zgoda na używanie starej gałęzi do nowego, niezwiązanego zadania.

## Dokumentacja po zadaniu

Jeżeli istnieją i zmiana tego wymaga, aktualizuj kolejno:

1. HANDOFF.md — aktualny stan zadania, wynik kontroli, zgody i ewentualny wyjątek od flow.
2. CHANGELOG.md — trwała historia, append-only.
3. STATUS.md — aktualny stan i następny priorytet.
