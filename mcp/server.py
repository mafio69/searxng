import os, json, datetime, httpx
from threading import Lock

from mcp.server.fastmcp import FastMCP

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://searxng:8080")
SEARXNG_LANG = os.getenv("SEARXNG_LANG", "auto")
PPLX_KEY = os.getenv("PPLX_API_KEY", "")
PPLX_DAILY_LIMIT = int(os.getenv("PPLX_DAILY_LIMIT", "50"))
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8000"))

mcp = FastMCP("search", host=HOST, port=PORT)
_pplx = {"day": None, "count": 0}
_pplx_lock = Lock()


async def _searxng(q: str, n: int) -> list[dict]:
    async with httpx.AsyncClient(timeout=10, follow_redirects=False) as client:
        r = await client.get(
            f"{SEARXNG_URL}/search",
            params={"q": q, "format": "json", "language": SEARXNG_LANG},
        )
    r.raise_for_status()
    out = r.json().get("results", [])[:n]
    return [
        {"title": x.get("title"), "url": x.get("url"),
         "snippet": (x.get("content") or "")[:400]}
        for x in out
    ]


async def _perplexity(q: str, n: int) -> list[dict]:
    if not PPLX_KEY:
        raise RuntimeError("brak PPLX_API_KEY")
    today = datetime.date.today().isoformat()
    # Reserve before HTTP. Failures/cancellation may still have incurred costs.
    # The lock never covers network I/O or an await.
    with _pplx_lock:
        if _pplx["day"] != today:
            _pplx.update(day=today, count=0)
        if _pplx["count"] >= PPLX_DAILY_LIMIT:
            raise RuntimeError("dzienny limit Perplexity wyczerpany")
        _pplx["count"] += 1
    async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
        r = await client.post(
            "https://api.perplexity.ai/search",
            headers={"Authorization": f"Bearer {PPLX_KEY}"},
            json={"query": q, "max_results": n, "search_type": "fast"},
        )
    r.raise_for_status()
    return [
        {"title": x.get("title"), "url": x.get("url"),
         "snippet": (x.get("snippet") or "")[:400]}
        for x in r.json().get("results", [])[:n]
    ]


@mcp.tool()
async def web_search(query: str, max_results: int = 5) -> str:
    """Wyszukaj w internecie. Zwraca JSON: source, results[title,url,snippet]."""
    n = max(1, min(max_results, 10))
    errors = []
    try:
        res = await _searxng(query, n)
        if res:
            return json.dumps({"source": "searxng", "results": res}, ensure_ascii=False)
        errors.append("searxng: pusty wynik")
    except Exception as e:
        errors.append(f"searxng: {e}")
    try:
        res = await _perplexity(query, n)
        return json.dumps({"source": "perplexity-fast", "results": res}, ensure_ascii=False)
    except Exception as e:
        errors.append(f"perplexity: {e}")
    return json.dumps({"source": None, "results": [], "errors": errors}, ensure_ascii=False)


if __name__ == "__main__":
    import uvicorn
    from access import McpAccessMiddleware

    app = McpAccessMiddleware(mcp.streamable_http_app(), os.getenv("MCP_AUTH_TOKEN", ""))
    uvicorn.run(app, host=HOST, port=PORT, access_log=False)
