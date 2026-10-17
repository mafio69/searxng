import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mcp'))
import server


class SearchStatusTests(unittest.IsolatedAsyncioTestCase):
    async def search(self, primary, fallback):
        def options(value):
            return {'side_effect': value} if isinstance(value, Exception) else {'return_value': value}
        with patch.object(server, '_searxng', **options(primary)), patch.object(server, '_perplexity', **options(fallback)):
            return json.loads(await server.web_search('synthetic fixture'))

    async def test_successfully_empty_with_disabled_fallback(self):
        result = await self.search([], server.ProviderUnavailable('perplexity_no_key'))
        self.assertEqual(result, {'status': 'empty', 'source': None, 'results': [], 'errors': []})

    async def test_provider_failure_is_never_empty(self):
        for primary, fallback in [
            (httpx.ReadTimeout('fixture'), []),
            ([], httpx.ReadTimeout('fixture')),
            ([], server.ProviderUnavailable('perplexity_limit')),
            (RuntimeError('fixture'), server.ProviderUnavailable('perplexity_no_key')),
        ]:
            with self.subTest(primary=type(primary), fallback=type(fallback)):
                result = await self.search(primary, fallback)
                self.assertEqual(result['status'], 'error')
                self.assertIsNone(result['source'])
                self.assertEqual(result['results'], [])
                self.assertTrue(result['errors'])

    async def test_successful_fallback_has_no_errors(self):
        results = [{'title': 'Example', 'url': 'https://example.org/', 'snippet': 'Fixture'}]
        response = await self.search(RuntimeError('fixture'), results)
        self.assertEqual(response, {'status': 'ok', 'source': 'perplexity-fast', 'results': results, 'errors': []})
