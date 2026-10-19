import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'mcp'))
sys.path.insert(0, str(ROOT / 'scripts'))
import server
from smoke_test import SmokeTest
from web_app import create_app

FIXTURES = json.loads((ROOT / 'docs/contract/web_search.example.json').read_text())


class McpContractTests(unittest.TestCase):
    def check_contract(self, case):
        isolated = type(server.mcp)('search', host='0.0.0.0')
        isolated.add_tool(server.web_search)
        with patch('web_app.mcp', isolated):
            app = create_app(allowed_hosts=['testserver'], mcp_auth='')
        primary = {'return_value': FIXTURES['ok']['results'] if case == 'ok' else []}
        fallback = {'return_value': []}
        if case == 'error':
            primary = {'side_effect': httpx.ReadTimeout('synthetic private detail')}
            fallback = {'side_effect': server.ProviderUnavailable('perplexity_no_key')}
        with TestClient(app) as client, patch.object(server, '_searxng', **primary), patch.object(server, '_perplexity', **fallback):
            smoke = SmokeTest('http://testserver')

            def request(path, payload=None, expected=200, headers=None):
                response = client.post(path, json=payload, headers=headers)
                self.assertEqual(response.status_code, expected)
                return response.content, response.headers

            smoke.request = request
            initialized = smoke.rpc('initialize', {'protocolVersion': '2025-11-25', 'capabilities': {},
                                  'clientInfo': {'name': 'contract-fixture', 'version': '1'}}, 1)
            smoke.session['MCP-Protocol-Version'] = initialized['protocolVersion']
            smoke.rpc('notifications/initialized', {}, None)
            tools = smoke.rpc('tools/list', {}, 2)
            self.assertTrue(any(tool['name'] == 'web_search' for tool in tools['tools']))
            result = smoke.rpc('tools/call', {'name': 'web_search', 'arguments': {'query': 'synthetic fixture'}}, 3)
            self.assertFalse(result.get('isError', False))
            texts = [item['text'] for item in result['content'] if item['type'] == 'text']
            self.assertEqual(len(texts), 1)
            self.assertEqual(json.loads(texts[0]), FIXTURES[case])

    def test_results_contract(self):
        self.check_contract('ok')

    def test_empty_contract(self):
        self.check_contract('empty')

    def test_failure_contract(self):
        self.check_contract('error')
