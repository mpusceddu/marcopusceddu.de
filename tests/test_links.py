"""Check link-page publication, editorial focus and scheduled article visibility."""
from datetime import date, datetime
import json
import shutil
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import assemble
from build_articles import read_article
from build_links import outputs, select_featured


class LinkPageTest(unittest.TestCase):
    def test_focus_is_independent_and_expiry_is_inclusive(self):
        newest, pinned = {'path': 'new.html'}, {'path': 'old.html'}
        config = {'path': 'old.html', 'expires': '2026-10-19'}
        self.assertEqual(select_featured([newest, pinned], config, date(2026, 10, 19)), pinned)
        self.assertEqual(select_featured([newest, pinned], config, date(2026, 10, 20)), newest)
        with self.assertRaises(ValueError):
            select_featured([newest], {'path': 'missing.html'}, date(2026, 10, 19))

    def test_link_page_follows_release_boundary_and_excludes_source_files(self):
        slug = 'guter-ganztag-qualifizierte-menschen.html'
        for timestamp, visible in [('2026-10-20T17:59:59+02:00', False), ('2026-10-20T18:00:00+02:00', True)]:
            with self.subTest(timestamp=timestamp), tempfile.TemporaryDirectory() as folder:
                destination = Path(folder) / 'public'
                source = Path(folder) / 'source'
                shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '__pycache__'))
                # Reconstruct the regular article inventory at the tested historical date.
                for article in (source / 'aktuelles').glob('*.html'):
                    if article.name != 'index.html' and read_article(article)['published'] > date(2026, 10, 20):
                        article.unlink()
                assemble(source, destination, datetime.fromisoformat(timestamp))
                html = (destination / 'links/index.html').read_text()
                recent = html.split('<!-- BEGIN GENERATED:links-recent -->')[1].split('<!-- END GENERATED:links-recent -->')[0]
                self.assertEqual(slug in recent, visible)
                self.assertIn('href="/standpunkte/fliegendes-auto.html"', html)
                self.assertIn('https://vinofy.de/', html)
                self.assertIn('https://github.com/mpusceddu', html)
                self.assertNotIn('noindex', html)
                self.assertIn('https://marcopusceddu.de/links/', (destination / 'sitemap.xml').read_text())
                self.assertFalse((destination / 'scripts').exists())
                self.assertFalse((destination / 'tests').exists())
                self.assertEqual(outputs(destination, date(2026, 10, 20))[destination / 'links/index.html'], html)

    def test_future_focus_is_not_shown_in_historical_build(self):
        rendered = next(iter(outputs(ROOT, date(2026, 10, 18)).values()))
        self.assertNotIn('href="/standpunkte/fliegendes-auto.html"', rendered)


if __name__ == '__main__':
    unittest.main()
