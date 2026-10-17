"""Optional MCP-only bearer protection, including all stream/session methods."""
import hmac

from starlette.responses import JSONResponse


class McpAccessMiddleware:
    def __init__(self, app, auth_value=""):
        self.app = app
        self.expected = ("Bearer " + auth_value).encode("utf-8") if auth_value else None

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        protected = path == "/mcp" or path.startswith("/mcp/")
        if scope["type"] == "http" and protected and self.expected is not None:
            values = [value for name, value in scope.get("headers", []) if name.lower() == b"authorization"]
            valid = len(values) == 1 and hmac.compare_digest(values[0], self.expected)
            if not valid:
                response = JSONResponse(
                    {"error": "Unauthorized"}, status_code=401,
                    headers={"WWW-Authenticate": "Bearer", "Cache-Control": "no-store"},
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)
