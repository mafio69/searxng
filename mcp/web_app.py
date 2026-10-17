"""Same-origin web UI and JSON adapter for the existing MCP search service."""

import json
import os
from pathlib import Path

import uvicorn
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from server import HOST, PORT, mcp, web_search


def create_app(search_service=web_search, static_dir=None, allowed_hosts=None):
    assets = Path(static_dir) if static_dir else Path(__file__).resolve().parent / "static"

    async def search_endpoint(request: Request):
        # Do not accept cross-origin form submissions or send provider errors to browsers.
        if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
            return JSONResponse({"error": "JSON required"}, status_code=415)
        origin = request.headers.get("origin")
        if origin and origin != f"{request.url.scheme}://{request.url.netloc}":
            return JSONResponse({"error": "Origin not allowed"}, status_code=403)
        if request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse({"error": "Origin not allowed"}, status_code=403)
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 4096:
                return JSONResponse({"error": "Request too large"}, status_code=413)
        try:
            payload = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        if not isinstance(payload, dict):
            return JSONResponse({"error": "Object required"}, status_code=400)
        query = payload.get("query")
        count = payload.get("max_results", 10)
        if (not isinstance(query, str) or not query.strip() or len(query) > 500
                or type(count) is not int or not 1 <= count <= 10):
            return JSONResponse({"error": "Invalid search arguments"}, status_code=400)
        try:
            result = json.loads(await search_service(query.strip(), count))
            if (not isinstance(result, dict)
                    or result.get("source") not in ("searxng", "perplexity-fast", None)
                    or not isinstance(result.get("results"), list)
                    or any(not isinstance(item, dict) or any(
                        item.get(field) is not None and not isinstance(item[field], str)
                        for field in ("title", "url", "snippet")) for item in result["results"])):
                raise ValueError("Invalid search result")
        except Exception:
            return JSONResponse({"error": "Search unavailable"}, status_code=502)
        # Raw exception strings from providers can contain operational details.
        return JSONResponse({"source": result.get("source"), "results": result.get("results", [])})

    async def index(request: Request):
        if not (assets / "index.html").is_file():
            return JSONResponse({"error": "Frontend not built. See README.md."}, status_code=503)
        return FileResponse(assets / "index.html", headers={"Cache-Control": "no-cache"})

    async def favicon(request: Request):
        if not (assets / "favicon.svg").is_file():
            return JSONResponse({"error": "Not found"}, status_code=404)
        return FileResponse(assets / "favicon.svg")

    # Reuse FastMCP's application, including its existing session-manager lifespan.
    app = mcp.streamable_http_app()
    trusted_hosts = allowed_hosts if allowed_hosts is not None else [
        host.strip() for host in os.getenv(
            "SEARCH_ALLOWED_HOSTS", "127.0.0.1,localhost,mcp-search"
        ).split(",") if host.strip()
    ]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts,
                       www_redirect=False)
    app.router.routes[0:0] = [
        Route("/", index),
        Route("/favicon.svg", favicon),
        Route("/api/search", search_endpoint, methods=["POST"]),
        Mount("/assets", app=StaticFiles(directory=assets / "assets", check_dir=False)),
    ]
    return app


if __name__ == "__main__":
    uvicorn.run(create_app(), host=HOST, port=PORT, access_log=False)
