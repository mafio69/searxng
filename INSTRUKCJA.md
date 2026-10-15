# Instrukcja: SearXNG + MCP Search

## Co to jest

Dwa kontenery na sieci `ai`:

| Kontener | Co robi | Port |
|---|---|---|
| `searxng` | Prywatna metawyszukiwarka (bez reklam, bez śledzenia) | tylko wewnątrz Docker (8080) |
| `mcp-search` | Serwer MCP udostępniający AI narzędzie `web_search` | `127.0.0.1:8890` |

`mcp-search` szuka najpierw przez SearXNG. Jeśli SearXNG zawiedzie — przez API Perplexity (wymaga `PPLX_API_KEY` w `.env`, dzienny limit domyślnie 50 zapytań).

## Codzienne użycie

```bash
# start (kontenery startują same po reboocie VPS — restart: unless-stopped)
/usr/bin/docker compose -f /home/mariusz/app/searxng/docker-compose.yml -p searxng up -d

# stop
/usr/bin/docker compose -f /home/mariusz/app/searxng/docker-compose.yml -p searxng down

# logi (czy działa)
docker logs mcp-search --tail 20
docker logs searxng --tail 20
```

## Podpięcie do klienta MCP

Serwer działa jako streamable HTTP pod adresem: **`http://127.0.0.1:8890/mcp`**

### opencode (opencode.json)

```json
{
  "mcp": {
    "search": {
      "type": "http",
      "url": "http://127.0.0.1:8890/mcp"
    }
  }
}
```

### Claude Desktop (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "search": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://127.0.0.1:8890/mcp"]
    }
  }
}
```

Po dodaniu wpisu zrestartuj klienta. AI dostanie narzędzie `web_search`.

## Jak z tego korzysta AI (narzędzie)

```
web_search(query, max_results=5)
```

- `query` — czego szukać, np. `"termin składania JPK_V7"`
- `max_results` — 1–10 wyników
- zwraca JSON: `{"source": "searxng"|"perplexity-fast", "results": [{"title", "url", "snippet"}]}`

Przykład: poproś agenta *"poszukaj przez web_search deadlinu PIT-5L za 2025"*.

## Podpięcie z INNEGO projektu (kontenery Docker)

Port `8890` jest wystawiony tylko na hosta. Z innych kontenerów użyj sieci `ai`:

1. W docker-compose.yml **drugiego projektu** dodaj:

```yaml
services:
  twoja-aplikacja:
    networks:
      - ai

networks:
  ai:
    external: true
```

2. Adres MCP z wnętrza kontenerów: **`http://mcp-search:8000/mcp`** (port wewnętrzny 8000, nie 8890).

### Wywołanie z backendu Node/TS

```ts
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const client = new Client({ name: "chat-app", version: "1.0" });
await client.connect(new StreamableHTTPClientTransport(
  new URL("http://mcp-search:8000/mcp")
));

const res = await client.callTool({
  name: "web_search",
  arguments: { query: "termin składania JPK_V7", max_results: 5 },
});
```

W pętli agenta: zadeklaruj GLM tool `web_search` (parametry `query`, `max_results`), a przy jego wywołaniu przez model przekaż argumenty do `client.callTool` jak wyżej i zwróć wynik do modelu.

## Szybki test bez klienta

```bash
# MCP odpowiada? (powinno zwrócić 200)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8890/mcp \
  -X POST -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# SearXNG wyszukuje? (powinno zwrócić JSON z results)
docker exec mcp-search python -c "import httpx; print(len(httpx.get('http://searxng:8080/search', params={'q':'test','format':'json'}, timeout=15).json()['results']), 'wyników')"
```

## Po zmianie kodu (server.py / requirements.txt)

```bash
/usr/bin/docker compose -f /home/mariusz/app/searxng/docker-compose.yml -p searxng up -d --build --force-recreate
```

## Pliki w projekcie

- `docker-compose.yml` — definicja obu usług
- `searxng-settings.yml` — ustawienia SearXNG (włączony format JSON, wyłączony rate-limiter)
- `mcp/server.py` — kod serwera MCP (narzędzie `web_search`)
- `mcp/requirements.txt` — zależności (`mcp` przypięty do `<2` — nie podnosić, kod używa API v1)
- `.env` — sekrety (`PPLX_API_KEY`); nigdy nie commitować
