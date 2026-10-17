"""Regression checks for public deployment config; never read real env files."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConfigurationTests(unittest.TestCase):
    def test_public_settings_never_contain_a_secret_value(self):
        settings = (ROOT / 'searxng-settings.example.yml').read_text()
        key_lines = [line.strip() for line in settings.splitlines() if line.strip().startswith('secret_key:')]
        self.assertEqual(key_lines, ['secret_key: ""'])

    def test_compose_requires_environment_key_and_only_mounts_public_template(self):
        compose = (ROOT / 'docker-compose.yml').read_text()
        self.assertIn('SEARXNG_SECRET: ' + chr(36) + '{SEARXNG_SECRET:?', compose)
        self.assertIn('./searxng-settings.example.yml:/etc/searxng/settings.yml:ro', compose)
        self.assertNotIn('./searxng-settings.yml:', compose)
        self.assertIn('/searxng-settings.yml', (ROOT / '.gitignore').read_text().splitlines())
