# HANDOFF.md — pałeczka między sesjami

> Jak prowadzić: plik opisuje stan zadania na granicy sesji. Zeruj go (nadpisuj całość) po zakończeniu zadania. Krótko, konkretnie, z komendami do wklejenia.

## Cel zadania (niedokończony)

Podłączyć narzędzie `web_search` (MCP: SearXNG + awaryjny Perplexity) do agentów w projekcie **wirral-ai** (czat na modelach z.ai/GLM). SearXNG = domyślna, darmowa wyszukiwarka; **Perplexity wchodzi tylko awaryjnie**, gdy SearXNG zwróci puste wyniki albo rzuci błąd (tak ma zostać — wymóg użytkownika).

## Co jest już zrobione (serwer wyszukiwarki — DZIAŁA)

Katalog: `/home/mariusz/app/searxng/` (ten projekt). Kontenery `searxng` i `mcp-search` wstają same (`restart: unless-stopped`), sieć zewnętrzna `ai`.

1. `docker-compose.yml` — naprawiony: 2 usługi (`searxng` z obrazu, `mcp-search` build `./mcp`), sieć `ai` zadeklarowana jako `external: true`.
2. `searxng-settings.yml` — włączony format JSON (SearXNG domyślnie go blokuje), `limiter: false`, wygenerowany `secret_key`.
3. `mcp/requirements.txt` — `mcp>=1.2,<2` (v2 zmieniła API: `FastMCP` → `MCPServer`; NIE podnosić).
4. Zweryfikowane: SearXNG zwraca wyniki JSON, MCP odpowiada HTTP 200.
5. `INSTRUKCJA.md` — pełna dokumentacja użycia (URLe, snippety, testy).

Adresy MCP:
- z hosta: `http://127.0.0.1:8890/mcp`
- z kontenerów w sieci `ai`: `http://mcp-search:8000/mcp`

Logika `web_search(query, max_results 1–10)` w `mcp/server.py`: SearXNG → puste/błąd → Perplexity (klucz `PPLX_API_KEY` w `.env`, limit dzienny `PPLX_DAILY_LIMIT` domyślnie 50).

## Co zostało do zrobienia (wirral-ai)

Kod: `/home/mariusz/PhpstormProjects/wirralAI` — **lokalna kopia jest STARA**. Najpierw:

```bash
cd /home/mariusz/PhpstormProjects/wirralAI
git checkout master && git pull
```

Kroki:
1. Przeczytać AGENTS.md / GIT-FLOW.md / README wirral-ai (jeśli są) i trzymać się ich konwencji.
2. Znaleźć pętlę agenta / integrację tooli (function calling do z.ai) — tam dodać tool `web_search`, który woła MCP (snippets: Node/TS w INSTRUKCJA.md; jeśli projekt jest w PHP — klient MCP albo bezpośrednie POST na endpoint MCP).
3. Jeśli wirral-ai działa w Dockerze na tym hoście → podpiąć jego kontenery do sieci `ai` w jego compose (`networks: { ai: { external: true } }`) i używać `http://mcp-search:8000/mcp`.
4. Po zmianach: testy projektu przed commitem, branch z `develop` wg GIT-FLOW (chyba że wirral-ai ma inny flow), po pushu STATUS.md + CHANGELOG.md.
5. Na koniec: zatwierdzić z użytkownikiem, gdzie dokładnie wirral-ai jest deployowany, i czy MCP jest tam osiągalny.

## BLOKADA (dlaczego przerwano)

Opencode w tej sesji ma `external_directory: "*": "deny"` — brak dostępu do `/home/mariusz/PhpstormProjects/**`. Rozwiązanie (jedno z):
- użytkownik dodaje w opencode.json allow **po** wpisie `"*": "deny"` i **pełny restart** opencode:

```json
"external_directory": {
  "*": "deny",
  "/home/mariusz/PhpstormProjects/**": "allow"
}
```

- albo start opencode z katalogu projektu: `cd /home/mariusz/PhpstormProjects/wirralAI && opencode` (ew. `--continue`).

## Zasady twarde (nie naruszać w wirral-ai)

- **Zasada #4**: nie czytać/wyświetlać `.env`, kluczy, credentiali — również w katalogu wirralAI.
- **Zasada #4b**: bash z umiarem, bez grzebania w git history, bez przeszukiwania dysku poza wskazanymi katalogami (użytkownik był tym zirytowany).
- Rozmowa po polsku, kod/komity po angielsku, UI przez i18n (pl+en).
- Nie proponować zmiany hostingu; nie commitować bez prośby.
