import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mcp'))
import server
from web_app import create_app


class McpAccessTests(unittest.TestCase):
    def application(self, auth='fixture-only'):
        isolated = type(server.mcp)('search', host='0.0.0.0')
        with patch('web_app.mcp', isolated):
            return create_app(allowed_hosts=['testserver'], mcp_auth=auth)

    def test_all_mcp_methods_reject_missing_or_wrong_credentials(self):
        with TestClient(self.application()) as client:
            for method in ['GET', 'POST', 'DELETE']:
                for headers in [{}, {'Authorization': 'Bearer wrong'}, {'Authorization': 'Basic fixture-only'}]:
                    with self.subTest(method=method, headers_present=bool(headers)):
                        response = client.request(method, '/mcp', headers=headers)
                        self.assertEqual(response.status_code, 401)
                        self.assertNotIn('fixture-only', response.text)
                        self.assertEqual(response.headers['WWW-Authenticate'], 'Bearer')
            self.assertEqual(client.post('/mcp/extra').status_code, 401)

    def test_authorized_client_initializes_with_optional_auth_enabled(self):
        for scheme in ('Bearer', 'bearer', 'BeArEr'):
            with self.subTest(scheme=scheme), TestClient(self.application()) as client:
                response = client.post('/mcp', json={
                    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
                    'params': {'protocolVersion': '2025-03-26', 'capabilities': {}, 'clientInfo': {'name': 'fixture', 'version': '1'}},
                }, headers={'Authorization': f'{scheme} fixture-only', 'Accept': 'application/json, text/event-stream'})
                self.assertEqual(response.status_code, 200)
                self.assertIn('serverInfo', response.text)

    def test_token_comparison_remains_case_sensitive(self):
        with TestClient(self.application()) as client:
            response = client.post('/mcp', headers={'Authorization': 'bearer FIXTURE-ONLY'})
            self.assertEqual(response.status_code, 401)

    def test_auth_does_not_change_browser_api_or_static_routes(self):
        with TestClient(self.application()) as client:
            self.assertEqual(client.post('/api/search', json={'query': ' '}).status_code, 400)
            self.assertNotEqual(client.get('/').status_code, 401)

    def test_duplicate_credentials_are_rejected(self):
        with TestClient(self.application()) as client:
            for scheme in ('Bearer', 'bearer'):
                response = client.post('/mcp', headers=[('Authorization', f'{scheme} fixture-only'), ('Authorization', f'{scheme} fixture-only')])
                self.assertEqual(response.status_code, 401)

    def test_no_config_preserves_previous_behavior(self):
        with TestClient(self.application(auth='')) as client:
            self.assertNotEqual(client.post('/mcp').status_code, 401)
