# PhpStorm HTTP Client — testy DevBrain

Ten dokument opisuje testy `.http` uruchamiane **wewnątrz PhpStorma**. Nie
zastępuje testów PHPUnit ani nie zawiera tokenów, ciasteczek ani certyfikatów.

## Co oznaczają kolory w oknie Services

Wykonanie requestu i wynik testu to dwa niezależne fakty:

- zielone `Request` / `Response` oznacza, że klient wysłał żądanie i odebrał
  odpowiedź HTTP — także `401`, `404`, `422` lub `302`;
- wynik w gałęzi `Tests` pochodzi z kodu `client.test(...)` uruchamianego po
  odebraniu odpowiedzi;
- `client.assert(...)` ma rzucić błąd, gdy kontrakt nie jest spełniony. Nie
  wyłączamy asercji ani nie zmieniamy oczekiwanego statusu tylko po to, aby
  wynik był zielony.

Zatem ekran „request zielony, test czerwony” jest prawidłową sygnalizacją
problemu w aplikacji, środowisku albo kontrakcie testu. Szczegóły są w zakładce
`Tests`, a diagnostyka handlera w `Response Handler`.

Oficjalnie `client.test()` wykonuje testy po response handlerze, a
`client.assert()` kończy test błędem, gdy warunek jest fałszywy:
[HTTP Client reference](https://www.jetbrains.com/help/idea/http-client-reference.html).

## Pliki i środowiska

- `backend/http/testy_token.http` jest **lokalnym** testem integracyjnym
  prywatnej listy #1222. Sprawdza autoryzację i wykonuje dwa zapisy testowe.
  Nie uruchamiamy go na produkcji.
- `backend/http/plan-szyfrowania-notatek.http` jest **produkcyjnym,
  jednorazowym seederem** zadań na zwykłej liście #65. Każdy jego `POST` tworzy
  nowe zadanie, więc nie wolno używać `Run All` ani traktować go jako regresji.
  Najpierw uruchamiamy wyłącznie pierwszy `GET` listy #65.
- `backend/http/http-client.private.env.json` jest plikiem lokalnym,
  gitignored. Zawiera wartości prywatne i nie trafia do commitu. Przykładowa
  struktura bez sekretów jest w `backend/http/example.http-client.private.env.json`.

W PhpStormie wybór z listy `Run with` jest częścią kontraktu testu. Prywatne
zmienne nadpisują zmienne publiczne; klient wyszukuje pliki środowiskowe od
katalogu `.http` w górę drzewa projektu. To oznacza, że błędnie wybrane `local`
może poprawnie wysłać request do `localhost`, ale nie znajdzie produkcyjnej
listy #65 i zwróci `404`.

Źródło: [HTTP Client variables](https://www.jetbrains.com/help/pycharm/http-client-variables.html)
(mechanizm wspólny dla IDE JetBrains).

## Zasada uruchamiania

1. Wybierz właściwe środowisko w `Run with`.
2. Uruchom pojedynczy request preflight (`GET` listy) i przeczytaj status oraz
   body odpowiedzi.
3. Dopiero po zielonym preflight uruchamiaj request modyfikujący.
4. Oceniaj wynik w `Tests`, nie tylko zielony znacznik przy `Request`.
5. Odpowiedzi zapisane przez IDE pod `.idea/httpRequests/` są historią
   diagnostyczną, a nie dowodem pozytywnego wyniku testu.

PhpStorm zapisuje odpowiedzi i wyświetla wyniki response handlerów w Services:
[HTTP Client w edytorze](https://www.jetbrains.com/help/idea/http-client-in-product-code-editor.html).

## Minimalny kontrakt requestu TODO

Każdy test API powinien weryfikować co najmniej:

```http
> {%
client.test("Utworzono zadanie na oczekiwanej liście", function () {
  const body = response.body;
  client.assert(response.status === 201, "Oczekiwano 201, otrzymano " + response.status);
  client.assert(body.task?.listId === Number("{{listId}}"), "Zadanie trafiło na inną listę");
  client.assert(Number.isInteger(body.task?.id), "Brak identyfikatora utworzonego zadania");
});
%}
```

Status `201` potwierdza utworzenie zasobu; `listId` i `id` chronią przed
fałszywie pozytywnym zapisem do niewłaściwej listy. Testy odmowy (`401`, `403`,
`404`) mają pozostać asercjami bezpieczeństwa, a nie być usuwane.

## Rozpoznane przyczyny wcześniejszych czerwonych wyników

1. Seeder planu miał zaszytą listę #66, podczas gdy lokalny HTTP Client był
   uruchamiany przeciw `localhost`. Lokalna baza nie zawiera produkcyjnej listy,
   więc poprawną odpowiedzią był `404`. Skrypt wskazuje teraz listę #65 i wprost
   informuje, że wymaga środowiska `prod`.
2. Plik seedera był uruchamiany jak pełna paczka testów. To błąd użycia: zawiera
   mutujące `POST`, które należy wykonywać pojedynczo po preflight.
3. Produkcyjny host jest dodatkowo chroniony przez Cloudflare Access. Zwykły
   bearer token DevBrain autoryzuje dopiero aplikację; nie zastępuje poświadczeń
   wymaganych przez bramę przed aplikacją. Odpowiedź `302` do logowania Access
   oznacza problem dostępu do środowiska, nie błąd asercji i nie powód do
   wyłączania walidacji.

## Diagnostyka bez obchodzenia zabezpieczeń

- `401` z JSON API: token aplikacyjny jest brakujący, nieważny, wygasły albo
  nie ma uprawnień. Użyj właściwego środowiska; nie wklejaj tokenu do `.http`.
- `404` lokalnie dla listy produkcyjnej: wybierz `prod` albo użyj lokalnego ID
  przeznaczonego do testów.
- `302` lub HTML bramy Access: zatrzymaj test. Wymaga skonfigurowanego,
  zatwierdzonego dostępu do Cloudflare Access dla klienta HTTP; nie omijaj go
  wyłączaniem ochrony ani kopiowaniem ciasteczek.
- Błąd certyfikatu `localhost`: napraw lokalny zaufany certyfikat. Nie ustawiaj
  globalnie `verifyHostCertificate: false`; JetBrains traktuje tę opcję jako
  wyjątek per prywatne środowisko.

## Automatyzacja później, nie zamiast diagnostyki

HTTP Client CLI może uruchamiać te same response handlery i zapisać raport
JUnit XML (`--report`). Nie należy jednak od razu przenosić testów lokalnego
TLS/OAuth do CLI: aktualna dokumentacja wskazuje ograniczenia CLI dla SSL i
OAuth. Najpierw stabilizujemy kontrakt w PhpStormie i oddzielamy read-only
regresję od seederów zapisujących dane.

Źródło: [HTTP Client CLI](https://www.jetbrains.com/help/idea/http-client-cli.html).

## Produkcyjne testy przez Cloudflare Access

Zwykły bearer DevBrain jest poświadczeniem aplikacji. Nie uwierzytelnia
klienta przed Cloudflare Access, dlatego produkcyjny seeder używa dodatkowo
nagłówków `CF-Access-Client-Id` i `CF-Access-Client-Secret`.

Operator tworzy w Cloudflare ograniczony Service Token oraz politykę typu
Service Auth wyłącznie dla aplikacji lub ścieżki API DevBrain. Identyfikator i
wartość tokenu wpisuje tylko do gitignored
`backend/http/http-client.private.env.json`, jako `cfAccessClientId` i
`cfAccessClientSecret`. Nie wpisuje ich do pliku przykładowego, kodu, raportu
testów ani czatu.

Po ustawieniu tych dwóch wartości najpierw uruchom pojedynczy `GET` preflight
listy #65. Dopiero status `200` z JSON API pozwala uruchomić pojedynczy `POST`
seedera. `302` lub `200 text/html` oznacza nadal bramę Access — test ma pozostać
czerwony i nie tworzyć zadań.

### Runbook: dostęp Service Auth dla HTTP Clienta

Ten runbook dodaje **osobny** dostęp maszynowy do API TODO. Nie zmienia
logowania użytkowników do panelu DevBrain, nie otwiera całej domeny i nie
zmienia historycznej aplikacji `devbrain-mcp-oauth-bypass`. Ta ostatnia ma
politykę `Block` dla starych endpointów MCP/OAuth i powinna pozostać bez zmian.

#### 1. Utwórz dedykowany Service Token

W Cloudflare Zero Trust przejdź kolejno do:

1. `Access controls` → `Service credentials` → `Service Tokens`.
2. Kliknij utworzenie nowego Service Tokena.
3. Nadaj nazwę `devbrain-http-client-todo`.
4. Ustaw termin ważności — dla lokalnego klienta HTTP zalecane jest 30 dni.
5. Zapisz jednorazowo pokazane `Client ID` i `Client Secret` tylko w
   lokalnym, gitignored `backend/http/http-client.private.env.json`, wewnątrz
   obiektu `prod`:

   ```json
   "cfAccessClientId": "WARTOSC_PRYWATNA",
   "cfAccessClientSecret": "WARTOSC_PRYWATNA"
   ```

Nie używaj tokena serwerowego, np. `hyperdrive-devbrain-*`, w lokalnym kliencie
HTTP. Nie unieważniaj go bez potwierdzenia jego użytkowników, ponieważ może
obsługiwać działającą integrację serwerową.

#### 2. Utwórz wąską aplikację Access

W Cloudflare Zero Trust przejdź kolejno do:

1. `Access controls` → `Applications`.
2. `+ Create new application`.
3. Górna zakładka: `Self-hosted and private`.
4. W drugim rzędzie typów kliknij `Service auth` — nie `Private destinations`,
   `Workers` ani `Public DNS`.
5. Kliknij `Continue with Self-hosted and private`.
6. Nazwij aplikację `devbrain-todo-api-service-auth`.
7. W `Destinations` → `Public hostnames` wpisz:

   | Pole | Wartość |
   | --- | --- |
   | `Subdomain` | `devbrain` |
   | `Domain` | `virral.tech` |
   | `Path` | `api/todo/*` |

   Pole `Path` pokazuje ukośnik poza polem, dlatego wpisujemy
   `api/todo/*`, bez początkowego `/`.

Nowy interfejs może po wprowadzeniu nazwy przewinąć formularz bez przycisku
`Next`; jest to oczekiwane zachowanie.

#### 3. Utwórz politykę dla jednego tokena

W formularzu `Create new policy` ustaw dokładnie:

| Pole | Wartość |
| --- | --- |
| `Policy Name` | `devbrain-todo-http-client` |
| `Action` | `Service Auth` |
| `Include` → `Selector is...` | `Service Token` |
| `Include` → `Value is...` | `devbrain-http-client-todo` |
| `Policy session duration` | `Same as application session duration` |

Nie wybieraj `Any Access Service Token`: dopuściłby każdy token usługowy z
konta. Nie dodawaj `Emails`, `Email one-time PIN`, `Google`, `Everyone`,
`Require` ani `Exclude`. Te selektory dotyczą interaktywnego logowania
człowieka, którego PhpStorm HTTP Client nie wykonuje.

`Action` musi być `Service Auth`, a nie `Allow`. Przy `Allow` Cloudflare nadal
oczekuje logowania przez dostawcę tożsamości i klient HTTP otrzymuje stronę
logowania zamiast odpowiedzi API. Nie używaj również `Bypass`: wyłączałby
egzekwowanie Access, podczas gdy Service Auth uwierzytelnia konkretny token.

Pozostaw `Override global multi-factor authentication settings (MFA)` i
`Just-in-time access` jako `Off`. Kliknij `Save policy`, a następnie zapisz
aplikację w końcowym kroku formularza.

#### 4. Weryfikacja oraz interpretacja wyniku

1. W PhpStorm otwórz `backend/http/plan-szyfrowania-notatek.http`.
2. Wybierz `Run with: prod`.
3. Uruchom wyłącznie pierwszy request `GET` (preflight listy #65).

Wynik oczekiwany to `200` oraz JSON API zawierający listę #65. Dopiero wtedy
można wykonać pojedynczy, zatwierdzony `POST` seedera.

| Wynik | Znaczenie | Działanie |
| --- | --- | --- |
| `200` i JSON API | Cloudflare Service Auth oraz token DevBrain działają | można przejść do zatwierdzonego zapisu |
| `200 text/html` lub strona logowania Cloudflare | request trafia w interaktywne logowanie lub nie spełnia polityki | sprawdź ścieżkę aplikacji, `Action: Service Auth` i wybrany konkretny token |
| `401` JSON z DevBrain | Cloudflare przepuścił ruch, ale token aplikacji DevBrain jest nieprawidłowy | operator generuje lub przekazuje właściwy token DevBrain |
| `unsubstituted variable` | PhpStorm nie wczytał środowiska `prod` | sprawdź `Run with: prod` i strukturę prywatnego pliku środowiska |

#### 5. Wycofanie

Jeśli dostęp trzeba zatrzymać, usuń nową aplikację
`devbrain-todo-api-service-auth` albo odłącz od niej politykę
`devbrain-todo-http-client`. Ruch wróci do zwykłej ochrony Access; nie
przywracaj polityki `Bypass` i nie zmieniaj aplikacji
`devbrain-mcp-oauth-bypass`.

Źródła: [Service tokens](https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/),
[Access policies](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/) oraz
[Authenticate coding agents](https://developers.cloudflare.com/cloudflare-one/access-controls/authenticate-agents/).

## Przystępne materiały do dalszej nauki

- [The Best of IntelliJ IDEA’s HTTP Client](https://blog.jetbrains.com/idea/2023/10/the-best-of-intellij-idea-s-http-client/) — zwięzły przegląd plików `.http`, środowisk i skryptów przed oraz po żądaniu.
- [HTTP Client CLI: Run requests and tests on CI](https://blog.jetbrains.com/idea/2022/12/http-client-cli-run-requests-and-tests-on-ci/) — praktyczny opis uruchamiania testów i raportowania ich wyniku w CI.
- [HTTP request in editor specification](https://github.com/JetBrains/http-request-in-editor-spec/blob/master/spec.md) — specyfikacja składni, dobra gdy zachowanie `client.test`, zmiennych lub separatorów `###` jest niejasne.
- [Practical Guide to JetBrains HTTP Client](https://karve.dev/blog/jetbrains-http-client-files/) — przystępne wprowadzenie praktyczne; to źródło pomocnicze, więc szczegóły składni i ograniczenia zawsze potwierdzamy w dokumentacji JetBrains.

Oficjalne referencje JetBrains są źródłem rozstrzygającym dla wersji PhpStorm używanej w projekcie.
