"""Check a running deployment without dependencies or paid provider calls."""
import argparse
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from html.parser import HTMLParser


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []
        self.root = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.root |= attrs.get('id') == 'root'
        path = attrs.get('src') if tag == 'script' else attrs.get('href') if tag == 'link' else None
        if path and path.startswith('/assets/'):
            self.paths.append(path)


class SmokeTest:
    def __init__(self, base_url, mcp_auth=""):
        self.base = base_url.rstrip('/') + '/'
        self.session = {}
        self.auth = {"Authorization": "Bearer " + mcp_auth} if mcp_auth else {}

    def request(self, path, payload=None, expected=200, headers=None):
        request = Request(urljoin(self.base, path.lstrip('/')),
                          data=json.dumps(payload).encode() if payload is not None else None,
                          headers={'Content-Type': 'application/json', **(headers or {})})
        try:
            response = urlopen(request, timeout=40)
        except HTTPError as error:
            response = error
        with response:
            body = response.read()
            if response.status != expected:
                raise AssertionError(f'{path}: expected HTTP {expected}, got {response.status}')
            return body, response.headers

    def rpc(self, method, params, identifier):
        payload = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if identifier is not None:
            payload['id'] = identifier
        body, headers = self.request('/mcp', payload, 202 if identifier is None else 200,
                                     {'Accept': 'application/json, text/event-stream', **self.session, **self.auth})
        if headers.get('Mcp-Session-Id'):
            self.session['Mcp-Session-Id'] = headers['Mcp-Session-Id']
        if identifier is None:
            return None
        if 'text/event-stream' in headers.get('Content-Type', ''):
            messages = [json.loads(line[5:].strip()) for line in body.decode().splitlines()
                        if line.startswith('data:')]
            reply = next((item for item in messages if item.get('id') == identifier), None)
        else:
            reply = json.loads(body)
        if not isinstance(reply, dict) or reply.get('id') != identifier or 'error' in reply:
            raise AssertionError(f'MCP {method}: invalid response')
        return reply['result']

    def run(self, query=None):
        html, headers = self.request('/')
        assert 'text/html' in headers.get('Content-Type', ''), 'Frontend is not HTML'
        assets = Assets()
        assets.feed(html.decode())
        assert assets.root and assets.paths, 'Missing React root or built assets'
        for path in assets.paths:
            body, _ = self.request(path)
            assert body, f'Empty asset: {path}'
        icon, _ = self.request('/favicon.svg')
        assert b'<svg' in icon, 'Invalid favicon'
        print('OK frontend, assets, favicon')
        self.request('/api/search', {'query': ' '}, expected=400)
        self.request('/api/search', {'query': 'test'}, expected=403,
                     headers={'Origin': 'https://smoke.invalid'})
        print('OK API validation and cross-origin rejection')
        initialized = self.rpc('initialize', {'protocolVersion': '2025-03-26', 'capabilities': {},
                               'clientInfo': {'name': 'search-smoke', 'version': '1'}}, 1)
        assert initialized.get('serverInfo'), 'Missing MCP serverInfo'
        self.session['MCP-Protocol-Version'] = initialized['protocolVersion']
        self.rpc('notifications/initialized', {}, None)
        tools = self.rpc('tools/list', {}, 2)
        tool = next((t for t in tools.get('tools', []) if t['name'] == 'web_search'), None)
        assert tool and 'query' in tool['inputSchema'].get('required', []), 'Missing web_search contract'
        print('OK MCP initialization and tools/list')
        if query:
            body, _ = self.request('/api/search', {'query': query, 'max_results': 1})
            result = json.loads(body)
            assert result.get('source') in ('searxng', 'perplexity-fast') and result.get('results'), 'Search returned no results'
            assert all(isinstance(item.get('url'), str) and urlsplit(item['url']).scheme in ('http', 'https')
                       for item in result['results']), 'Invalid result URL'
            print('OK live search via ' + result['source'])
        else:
            print('SKIP live search (use --query; may use paid Perplexity fallback)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8890')
    parser.add_argument('--query', help='Opt in to real search; may incur Perplexity costs')
    args = parser.parse_args()
    try:
        SmokeTest(args.url, os.getenv("MCP_AUTH_TOKEN", "")).run(args.query)
    except (AssertionError, URLError, ValueError, KeyError, StopIteration, TimeoutError) as error:
        print(f'FAIL {type(error).__name__}: deployment check failed; verify URL, containers and Docker network ai')
        return 1
    print('PASS smoke test')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
