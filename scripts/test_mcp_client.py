"""Live MCP Client test script for szukaj.dom / local container."""
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

def get_auth_token():
    token = os.getenv("MCP_AUTH_TOKEN", "").strip()
    if token:
        return token
    private_file = ROOT / "http" / "http-client.private.env.json"
    if private_file.exists():
        try:
            data = json.loads(private_file.read_text(encoding="utf-8"))
            token = data.get("local", {}).get("authToken", "").strip()
            if token.startswith("Bearer "):
                token = token[7:].strip()
            return token
        except Exception:
            pass
    return ""

def mcp_rpc(base_url, token, session_id, method, params, req_id):
    url = f"{base_url.rstrip('/')}/mcp"
    payload = {"jsonrpc": "2.0", "method": method, "params": params}
    if req_id is not None:
        payload["id"] = req_id

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urlopen(req, timeout=30) as resp:
        new_session = resp.headers.get("Mcp-Session-Id") or session_id
        body = resp.read().decode("utf-8")
        if req_id is None:
            return None, new_session
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
                if data.get("id") == req_id:
                    return data.get("result"), new_session
        try:
            data = json.loads(body)
            if data.get("id") == req_id:
                return data.get("result"), new_session
        except Exception:
            pass
        return None, new_session

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "SearXNG meta search"
    base_url = os.getenv("MCP_BASE_URL", "http://127.0.0.1:8000")
    token = get_auth_token()

    print(f"Connecting to MCP server: {base_url}/mcp")
    # 1. Initialize
    init_res, session_id = mcp_rpc(
        base_url, token, None, "initialize",
        {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "mcp-cli-tester", "version": "1.0.0"}},
        1
    )
    if not init_res or not session_id:
        print("FAIL: Failed to initialize MCP session.")
        return 1

    server_info = init_res.get("serverInfo", {})
    print(f"OK: MCP Session established: {session_id}")
    print(f"OK: Server name: {server_info.get('name')}, version: {server_info.get('version')}")

    # 2. Initialized notification
    mcp_rpc(base_url, token, session_id, "notifications/initialized", {}, None)

    # 3. Call web_search tool
    print(f"\nCalling MCP Tool 'web_search' with query: '{query}'...")
    call_res, _ = mcp_rpc(
        base_url, token, session_id, "tools/call",
        {"name": "web_search", "arguments": {"query": query, "max_results": 5}},
        2
    )

    if not call_res:
        print("FAIL: No result returned from web_search.")
        return 1

    content = call_res.get("content", [])
    text_block = next((c.get("text") for c in content if c.get("type") == "text"), None)
    if not text_block:
        print("FAIL: No text block in tool call result.")
        return 1

    parsed = json.loads(text_block)
    results = parsed.get("results", [])
    print(f"Status: {parsed.get('status')}")
    print(f"Source: {parsed.get('source')}")
    print(f"Results count: {len(results)}\n")
    print("=" * 80)
    for idx, item in enumerate(results, start=1):
        print(f"[{idx}] {item.get('title')}")
        print(f"    URL:     {item.get('url')}")
        print(f"    Snippet: {item.get('snippet')}\n")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(main())
