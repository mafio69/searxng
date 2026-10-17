import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mcp'))
import server


class ProviderErrorTests(unittest.IsolatedAsyncioTestCase):
    async def test_provider_details_never_reach_tool_response(self):
        for error, code in [(httpx.ReadTimeout('private fixture detail'), 'timeout'),
                            (httpx.ConnectError('private fixture detail'), 'http_error'),
                            (ValueError('private fixture detail'), 'error')]:
            with self.subTest(code=code), patch.object(server, '_searxng', side_effect=error), patch.object(server, '_perplexity', side_effect=error):
                response = await server.web_search('synthetic fixture')
                self.assertNotIn('private fixture detail', response)
                self.assertEqual(json.loads(response)['errors'], ['searxng_' + code, 'perplexity_' + code])
