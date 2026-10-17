"""Check semantic navigation destinations, not just whether a URL exists."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.current = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.current = {'attrs': dict(attrs), 'text': ''}

    def handle_data(self, data):
        if self.current is not None:
            self.current['text'] += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            self.links.append(self.current)
            self.current = None


class NavigationTest(unittest.TestCase):
    def test_current_news_links_resolve_to_news_archive(self):
        sources = [(p, p.relative_to(ROOT)) for p in ROOT.glob('*.html')]
        for directory in ('aktuelles', 'urbar', 'standpunkte', 'energie'):
            sources.extend((p, p.relative_to(ROOT)) for p in (ROOT / directory).rglob('*.html'))
        for package in (ROOT / '_scheduled').iterdir():
            files = package / 'files'
            sources.extend((p, p.relative_to(files)) for p in files.rglob('*.html'))
        checked = 0
        for source, public_path in sources:
            for link in Links(source.read_text()).links:
                if link['text'].strip() not in ('Aktuelles', 'Aktuelles vor Ort'):
                    continue
                with self.subTest(page=str(public_path), href=link['attrs'].get('href')):
                    target = urljoin('https://marcopusceddu.de/' + public_path.as_posix(), link['attrs'].get('href', ''))
                    self.assertEqual(urlsplit(target).path, '/aktuelles/')
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == '__main__':
    unittest.main()
