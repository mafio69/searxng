# AGENTS.md — zasady pracy agentów AI

Te reguły obowiązują każdego agenta AI w tym repozytorium. Gdy polecenie jest sprzeczne, niejednoznaczne albo wymaga dostępu poza poniższe granice, agent zatrzymuje pracę i pyta Mariusza.

## 1. Start i zakres

1. Przed zadaniem przeczytaj, jeśli istnieją: `README.md`, `STATUS.md`, `GIT-FLOW.md`, `AGENTS.md`, `HANDOFF.md`.
2. Wykonuj wyłącznie zlecone zadanie. Nie dodawaj bibliotek, funkcji, refaktoryzacji ani zmian pobocznych bez zgody.
3. Nie zgaduj brakujących danych. Zadaj jedno konkretne pytanie.
4. Odpowiadaj po polsku, jeśli użytkownik nie poprosi o inny język.
5. Nie uruchamiaj subagentów, auto-approve ani automatycznego zatwierdzania uprawnień.
6. Nie wysyłaj kodu, danych, plików ani konfiguracji do Internetu, API, MCP, zdalnego repozytorium lub innej usługi bez osobnej zgody użytkownika.

## 2. Katalog roboczy i `.local`

1. Pracuj wyłącznie w aktualnym katalogu repozytorium i jego podkatalogach.
2. Poza repozytorium dozwolony jest wyłącznie lokalny katalog roboczy repozytorium `.local/`.
3. `.local/` jest ignorowany przez Git i służy wyłącznie na dane lokalne: `.local/tmp/`, `.local/cache/`, `.local/reports/`, `.local/logs/`.
4. Nie używaj globalnego katalogu `/tmp` ani katalogów systemowych jako katalogu roboczego, cache, miejsca pobierania, ekstrakcji, raportów lub plików lock.
5. Nie używaj także `/var/tmp`, `/root`, `/run`, `/dev/shm`, `/etc`, `/var`, `/usr`, `/opt`, `/srv`, `/mnt`, `/media`, `/lost+found` ani katalogów innych użytkowników.
6. Nie czytaj, nie listuj, nie przeszukuj i nie edytuj `.local/secret/` ani jego podkatalogów.

## 3. Środowisko i narzędzia jakości

### Stała zgoda Mariusza: Ruff — allow

- Agenci mogą bez ponownego pytania uruchamiać `python3 scripts/check_project.py` oraz lokalny `PYTHONPATH=.local/tools/ruff python3 -m ruff check --config ruff.toml mcp scripts tests` w tym repozytorium. To zgoda na kontrole jakości, nie na pozostałe działania systemowe lub zewnętrzne.
- Instalacja przypiętej wersji z `requirements-dev.txt` do ignorowanego `.local/tools/ruff`, z cache i plikami tymczasowymi w `.local/`, została zatwierdzona przez Mariusza. Ruff nie jest zależnością obrazu aplikacji.
- Przed każdym commitem obowiązuje cały zestaw `python3 scripts/check_project.py`; brak Ruff lub błąd dowolnej kontroli blokuje commit. Sam lint nie zastępuje testów.
- Domyślnie używaj `check` bez `--fix`. Automatyczne poprawki i formatowanie są zmianami kodu: tylko w zakresie zadania, z przeglądem diff i pełnymi testami. Nie używaj `--unsafe-fixes` bez wyraźnego zlecenia.
- Analizuj wyłącznie kod projektu w `mcp`, `scripts`, `tests`, według `ruff.toml`. Zgoda nie obejmuje odczytu sekretów, wyłączania reguł bezpieczeństwa ani zmiany konfiguracji uprawnień agentów.

1. Do testów, lintingu, typechecka, buildów, formatowania i lokalnych narzędzi jakości stosuj polecenia opisane w `README.md` i `REPO.md`, z zachowaniem wymaganych zgód na Bash.
2. Uruchamianie testów i kontroli jakości nie daje zgody na migracje, seedowanie, usuwanie lub zmianę danych, deployment, push, PR, instalację zależności ani działania zewnętrzne. Te czynności nadal wymagają wyraźnej zgody Mariusza.
3. Nie analizuj, nie lokalizuj, nie czytaj, nie przeszukuj, nie kopiuj, nie wyjaśniaj ani nie modyfikuj wrapperów środowiska, ich dowiązań, aliasów, funkcji powłoki, konfiguracji ani sposobu działania.
4. Nie analizuj skryptów Bash/powłoki (`*.sh`, `*.bash`, `*.zsh`, `*.fish`, skryptów bez rozszerzenia, wrapperów i skryptów uruchamialnych), chyba że Mariusz poda dokładną ścieżkę i wyraźnie zleci analizę albo zmianę danego pliku. Wyjątek nigdy nie obejmuje dotenvx, kluczy ani wrapperów środowiska.
5. `dotenvx` jest bezwzględnie zabroniony. Nie uruchamiaj, nie analizuj i nie wywołuj pośrednio `dotenvx`, w tym `run`, `get`, `decrypt`, `encrypt`, `rotate` i `keypair`.
6. Nie uruchamiaj `bash -x`, `sh -x`, `set -x`, `strace`, `ltrace`, `source`, `. plik`, `eval`, `env`, `printenv`, `export -p` ani `set` w celu poznania środowiska, sekretów lub działania wrapperów.

## 4. Sekrety i dane chronione

1. Nie ujawniaj, nie kopiuj, nie wypisuj, nie loguj, nie commituj i nie przesyłaj wartości sekretów.
2. Sekretami są w szczególności hasła, tokeny, klucze API, nagłówki Authorization, cookies, klucze prywatne, certyfikaty, dane osobowe i kopie baz.
3. Nie odczytuj ani nie zmieniaj `.env.keys`, kluczy prywatnych, katalogów sekretów oraz plików nazwanych `*secret*`, `*token*`, `*credential*`, `client_secret*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `id_rsa*`, `id_ed25519*`.
4. Prawdziwy `.env` traktuj jako chroniony. Jeżeli zadanie wymaga jego sprawdzenia, poproś Mariusza o pojedynczą zgodę na odczyt konkretnego pliku. Nigdy nie pokazuj wartości w odpowiedzi ani logu.
5. `.env.example` i `.env.dist` mogą zawierać wyłącznie nazwy zmiennych i puste placeholdery.

## 5. Bash, baza i system

1. Polecenia Bash wymagają uprzedniej zgody Mariusza.
2. Baza danych jest domyślnie tylko do odczytu.
3. Bez wyraźnej zgody nie wykonuj `DELETE`, `UPDATE`, `INSERT`, `DROP`, `TRUNCATE`, migracji, seedów, surowego SQL zmieniającego dane ani operacji zmieniających infrastrukturę.
4. Nie używaj `sudo`, `su`, `pkexec`, `doas`, SSH, SCP, rsync, mount, Docker exec ani zdalnych poleceń bez osobnej zgody.
5. Nie instaluj, nie usuwaj i nie aktualizuj pakietów, zależności, obrazów Docker, kontenerów ani narzędzi bez zgody.

## 6. Git i polityka OpenCode

1. Nie wykonuj `push`, PR, release, taga ani wdrożenia bez wyraźnej zgody.
2. Nie wykonuj `git restore`, `git checkout --`, `git reset --hard`, `git clean` ani operacji mogącej przywrócić, nadpisać lub skasować pliki polityki bezpieczeństwa.
3. Nie czytaj, nie edytuj, nie przywracaj ani nie obchodź `opencode.json`, `.opencode/**` i plików konfiguracji uprawnień, chyba że Mariusz jednoznacznie zleci konkretną zmianę tej polityki.
4. Nie zmieniaj `git config user.name` ani `git config user.email`.

## 7. Jakość i zakończenie

1. Przed commitem uruchom pełny zestaw testów wskazany przez repozytorium.
2. Błąd testu, lintingu, typechecka lub kontroli bezpieczeństwa blokuje commit.
3. Po zadaniu krótko podaj: co zmieniono, jakie testy uruchomiono i ich wynik.
4. Jeśli istnieją i zmiana tego wymaga, aktualizuj kolejno: `HANDOFF.md`, `CHANGELOG.md`, `STATUS.md`.
