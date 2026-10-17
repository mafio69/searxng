import asyncio
import json
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mcp'))
import server


class ConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    async def test_two_delayed_searches_overlap_and_event_loop_stays_responsive(self):
        entered = 0
        both_entered = asyncio.Event()

        async def delayed(query, count):
            nonlocal entered
            entered += 1
            if entered == 2:
                both_entered.set()
            await asyncio.sleep(1)
            return [{'title': query, 'url': 'https://example.org', 'snippet': ''}]

        with patch.object(server, '_searxng', side_effect=delayed), patch.object(server, '_perplexity', new_callable=AsyncMock) as paid:
            started = time.perf_counter()
            tasks = [asyncio.create_task(server.web_search(q)) for q in ['one', 'two']]
            await asyncio.wait_for(both_entered.wait(), timeout=0.5)
            replies = await asyncio.gather(*tasks)
            self.assertLess(time.perf_counter() - started, 1.5)
            self.assertEqual([json.loads(r)['source'] for r in replies], ['searxng', 'searxng'])
            paid.assert_not_called()
