import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp"))

from starlette.testclient import TestClient
import server
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from smoke_test import SmokeTest
from web_app import create_app


class WebAppTests(unittest.TestCase):
    def setUp(self):
        isolated_mcp = patch("web_app.mcp", type(server.mcp)("search", host="0.0.0.0"))
        isolated_mcp.start()
        self.addCleanup(isolated_mcp.stop)
        self.service = AsyncMock(return_value=json.dumps({
            "source": "searxng", "results": [{"title": "Example", "url": "https://example.org", "snippet": "Text"}],
        }))
        self.client = TestClient(create_app(self.service, allowed_hosts=["testserver"]))

    def test_adapter_uses_shared_service_and_trims_query(self):
        response = self.client.post("/api/search", json={"query": "  test  ", "max_results": 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "searxng")
        self.service.assert_called_once_with("test", 5)

    def test_matching_untrusted_host_and_origin_are_rejected(self):
        response = self.client.post("/api/search", json={"query": "test"}, headers={
            "Host": "attacker.example:8890", "Origin": "http://attacker.example:8890",
            "Sec-Fetch-Site": "same-origin"})
        self.assertEqual(response.status_code, 400)
        self.service.assert_not_called()

    def test_extra_trusted_host_requires_explicit_configuration(self):
        with patch.dict("os.environ", {"SEARCH_ALLOWED_HOSTS": "127.0.0.1, mcp-search, 192.168.1.172"}):
            client = TestClient(create_app(self.service))
        self.assertEqual(client.post("/api/search", json={"query": "test"},
                                     headers={"Host": "192.168.1.172:8890"}).status_code, 200)
        self.assertEqual(client.post("/api/search", json={"query": "test"},
                                     headers={"Host": "attacker.example"}).status_code, 400)

    def test_default_hosts_preserve_docker_client_access(self):
        with patch.dict("os.environ", {}, clear=True):
            client = TestClient(create_app(self.service))
        for host in ("mcp-search:8000", "localhost:8890", "127.0.0.1:8890"):
            with self.subTest(host=host):
                response = client.post("/api/search", json={"query": "test"},
                                       headers={"Host": host, "Origin": "http://" + host})
                self.assertEqual(response.status_code, 200)

    def test_validation_prevents_provider_calls(self):
        for body in [[], {}, {"query": " "}, {"query": "x" * 501}, {"query": "test", "max_results": True},
                     {"query": "test", "max_results": 11}, {"query": "test", "max_results": "5"}]:
            with self.subTest(body=type(body)):
                self.assertEqual(self.client.post("/api/search", json=body).status_code, 400)
        self.service.assert_not_called()

    def test_rejects_large_body_invalid_json_and_cross_origin(self):
        self.assertEqual(self.client.post("/api/search", content="x" * 4097, headers={"content-type": "application/json"}).status_code, 413)
        self.assertEqual(self.client.post("/api/search", content="{", headers={"content-type": "application/json"}).status_code, 400)
        self.assertEqual(self.client.post("/api/search", data={"query": "test"}).status_code, 415)
        self.assertEqual(self.client.post("/api/search", json={"query": "test"}, headers={"Origin": "https://elsewhere.example"}).status_code, 403)
        self.service.assert_not_called()

    def test_provider_details_are_not_exposed(self):
        self.service.return_value = json.dumps({"source": None, "results": [], "errors": ["private operational detail"]})
        response = self.client.post("/api/search", json={"query": "test"})
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"error": "Search unavailable"})
        self.service.side_effect = RuntimeError("private operational detail")
        response = self.client.post("/api/search", json={"query": "test"})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("private operational detail", response.text)

    def test_malformed_service_result_returns_generic_gateway_error(self):
        for result in [None, [], {}, {"source": "unknown", "results": []},
                       {"source": "searxng", "results": None},
                       {"source": "searxng", "results": [None]},
                       {"source": "searxng", "results": [{"title": {"internal": "detail"}}]}]:
            with self.subTest(result=result):
                self.service.return_value = json.dumps(result)
                response = self.client.post("/api/search", json={"query": "test"})
                self.assertEqual(response.status_code, 502)
                self.assertEqual(response.json(), {"error": "Search unavailable"})

    def test_missing_static_files_return_actionable_errors(self):
        root = Path(__file__).resolve().parents[1] / ".local" / "tmp"
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            client = TestClient(create_app(self.service, directory, allowed_hosts=["testserver"]))
            response = client.get("/")
            self.assertEqual(response.status_code, 503)
            self.assertIn("README.md", response.json()["error"])
            self.assertEqual(client.get("/favicon.svg").status_code, 404)
        self.service.assert_not_called()

    def test_sec_fetch_cross_site_is_rejected_without_origin_header(self):
        response = self.client.post("/api/search", json={"query": "test"},
                                    headers={"Sec-Fetch-Site": "cross-site"})
        self.assertEqual(response.status_code, 403)
        self.service.assert_not_called()

    def test_serves_frontend_and_keeps_mcp_with_lifespan(self):
        # Explicitly keep temporary fixtures in repository-local .local.
        root = Path(__file__).resolve().parents[1] / ".local" / "tmp"
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            static = Path(directory)
            (static / "assets").mkdir()
            (static / "index.html").write_text("<title>Search UI</title>")
            (static / "assets" / "app.js").write_text("console.log('test')")
            with TestClient(create_app(self.service, static, allowed_hosts=["testserver"])) as client:
                index_response = client.get("/")
                self.assertIn("Search UI", index_response.text)
                self.assertEqual(index_response.headers.get("X-Content-Type-Options"), "nosniff")
                self.assertEqual(index_response.headers.get("Referrer-Policy"), "no-referrer")
                self.assertEqual(client.get("/assets/app.js").status_code, 200)
                response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                    "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"},
                }}, headers={"Accept": "application/json, text/event-stream"})
                self.assertEqual(response.status_code, 200)
                self.assertIn("serverInfo", response.text)


class SmokeTests(unittest.TestCase):
    def setUp(self):
        isolated = type(server.mcp)("search", host="0.0.0.0")
        isolated.add_tool(server.web_search)
        replacement = patch("web_app.mcp", isolated)
        replacement.start()
        self.addCleanup(replacement.stop)

    def test_full_smoke_flow_without_provider_calls(self):
        service = AsyncMock(side_effect=AssertionError("Smoke must not call providers"))
        root = Path(__file__).resolve().parents[1] / ".local" / "tmp"
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            static = Path(directory)
            (static / "assets").mkdir()
            (static / "index.html").write_text('<div id="root"></div><script src="/assets/app.js"></script>')
            (static / "assets" / "app.js").write_text("// frontend")
            (static / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            with TestClient(create_app(service, static, allowed_hosts=["testserver"])) as client:
                smoke = SmokeTest("http://testserver")

                def request(path, payload=None, expected=200, headers=None):
                    response = client.request("POST" if payload is not None else "GET", path,
                                              json=payload, headers=headers)
                    self.assertEqual(response.status_code, expected, path)
                    return response.content, response.headers

                smoke.request = request
                smoke.run()
                service.assert_not_called()
                with patch.object(server, "_searxng", return_value=[{"title": "Test", "url": "https://example.org", "snippet": "Text"}]), patch.object(server, "_perplexity") as paid:
                    result = smoke.rpc("tools/call", {"name": "web_search", "arguments": {
                        "query": "test", "max_results": 1}}, 3)
                    self.assertFalse(result.get("isError", False))
                    texts = [item["text"] for item in result["content"] if item["type"] == "text"]
                    self.assertEqual(json.loads(texts[0])["source"], "searxng")
                    paid.assert_not_called()

    def test_authorization_header_is_not_forwarded_across_redirects(self):
        from urllib.request import HTTPRedirectHandler

        captured = []
        fake_response = Mock()
        fake_response.__enter__ = Mock(return_value=fake_response)
        fake_response.__exit__ = Mock(return_value=False)
        fake_response.status = 200
        fake_response.read.return_value = b"{}"
        fake_response.headers = {}

        def fake_urlopen(req, timeout=40):
            captured.append(req)
            return fake_response

        smoke = SmokeTest("https://search.example.test", mcp_auth="synthetic-fixture")
        with patch("smoke_test.urlopen", side_effect=fake_urlopen):
            smoke.request("/mcp", {"jsonrpc": "2.0"}, headers=smoke.auth)
        self.assertEqual(len(captured), 1)
        req = captured[0]
        self.assertNotIn("Authorization", req.headers)
        self.assertEqual(req.unredirected_hdrs.get("Authorization"), "Bearer synthetic-fixture")
        redirected = HTTPRedirectHandler().redirect_request(
            req, None, 302, "Found", {}, "http://other.example.test/mcp"
        )
        self.assertIsNone(redirected.get_header("Authorization"))


class SearchFallbackTests(unittest.IsolatedAsyncioTestCase):
    @patch.object(server, "_perplexity")
    @patch.object(server, "_searxng")
    async def test_success_never_calls_paid_fallback(self, searxng, perplexity):
        searxng.return_value = [{"url": "https://example.org"}]
        result = json.loads(await server.web_search("test", 100))
        self.assertEqual(result["source"], "searxng")
        searxng.assert_called_once_with("test", 10)
        perplexity.assert_not_called()

    @patch.object(server, "_perplexity", return_value=[])
    @patch.object(server, "_searxng", return_value=[])
    async def test_empty_primary_uses_fallback(self, searxng, perplexity):
        self.assertEqual(json.loads(await server.web_search("test")), {
            "status": "empty", "source": None, "results": [], "errors": []})
        perplexity.assert_called_once_with("test", 5)

    @patch.object(server, "_perplexity", side_effect=RuntimeError("fallback unavailable"))
    @patch.object(server, "_searxng", side_effect=RuntimeError("primary unavailable"))
    async def test_both_failures_are_reported(self, searxng, perplexity):
        result = json.loads(await server.web_search("test"))
        self.assertIsNone(result["source"])
        self.assertEqual(result["results"], [])
        self.assertEqual(len(result["errors"]), 2)


class ProviderTests(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self):
        await server.close_http_client()

    @patch.object(server.httpx.AsyncClient, "get", new_callable=AsyncMock)
    async def test_searxng_limits_results_and_truncates_content(self, get):
        get.return_value = Mock()
        get.return_value.json.return_value = {"results": [
            {"title": "A", "url": "https://example.org", "content": "x" * 500},
            {"title": "B", "content": None},
        ]}
        result = await server._searxng("query", 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["snippet"]), 400)
        get.return_value.raise_for_status.assert_called_once()
        self.assertEqual(get.call_args.kwargs["params"]["format"], "json")

    @patch.object(server.httpx.AsyncClient, "post", new_callable=AsyncMock)
    async def test_missing_key_prevents_paid_request(self, post):
        with patch.object(server, "PPLX_KEY", ""):
            with self.assertRaisesRegex(RuntimeError, "perplexity_no_key"):
                await server._perplexity("query", 1)
        post.assert_not_called()

    @patch.object(server.httpx.AsyncClient, "post", new_callable=AsyncMock)
    async def test_daily_limit_prevents_paid_request(self, post):
        state = {"day": server.datetime.date.today().isoformat(), "count": 2}
        with patch.object(server, "PPLX_KEY", "test-placeholder"), patch.object(server, "PPLX_DAILY_LIMIT", 2), patch.object(server, "_pplx", state):
            with self.assertRaisesRegex(RuntimeError, "limit"):
                await server._perplexity("query", 1)
        post.assert_not_called()

    @patch.object(server.httpx.AsyncClient, "post", new_callable=AsyncMock)
    async def test_new_day_resets_limit_and_failed_http_keeps_its_reservation(self, post):
        state = {"day": "2000-01-01", "count": 100}
        post.return_value = Mock()
        post.return_value.json.return_value = {"results": [{"snippet": "x" * 500}]}
        with patch.object(server, "PPLX_KEY", "test-placeholder"), patch.object(server, "_pplx", state):
            self.assertEqual(len((await server._perplexity("query", 1))[0]["snippet"]), 400)
            self.assertEqual(state["count"], 1)
            post.return_value.raise_for_status.side_effect = RuntimeError("HTTP failure")
            with self.assertRaises(RuntimeError):
                await server._perplexity("query", 1)
            self.assertEqual(state["count"], 2)

    @patch.object(server, "_perplexity", return_value=[{"url": "https://example.org"}])
    @patch.object(server, "_searxng", side_effect=RuntimeError("primary unavailable"))
    async def test_primary_exception_uses_fallback_with_minimum_limit(self, searxng, perplexity):
        result = json.loads(await server.web_search("query", 0))
        self.assertEqual(result["source"], "perplexity-fast")
        perplexity.assert_called_once_with("query", 1)


if __name__ == "__main__":
    unittest.main()
