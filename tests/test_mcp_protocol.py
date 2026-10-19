import json
import sys
import unittest
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mcp'))
import server
from web_app import create_app


class McpProtocolTests(unittest.TestCase):
    def test_installed_sdk_matches_exact_requirement(self):
        requirement = (Path(__file__).resolve().parents[1] / 'mcp/requirements.txt').read_text().splitlines()[0]
        self.assertEqual(requirement, 'mcp==' + version('mcp'))

    def test_initialize_negotiates_versions_accepted_by_wirralai(self):
        accepted = ['2024-11-05', '2025-03-26', '2025-06-18', '2025-11-25']
        for requested in accepted + ['2099-01-01']:
            with self.subTest(requested=requested):
                isolated = type(server.mcp)('search', host='0.0.0.0')
                with patch('web_app.mcp', isolated):
                    app = create_app(allowed_hosts=['testserver'], mcp_auth='')
                with TestClient(app) as client:
                    response = client.post('/mcp', json={
                        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
                        'params': {'protocolVersion': requested, 'capabilities': {},
                                   'clientInfo': {'name': 'contract-fixture', 'version': '1'}},
                    }, headers={'Accept': 'application/json, text/event-stream'})
                    self.assertEqual(response.status_code, 200)
                    payload = next(json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: '))
                    negotiated = payload['result']['protocolVersion']
                    self.assertEqual(negotiated, requested if requested in accepted else '2025-11-25')
