"""Keep every public and scheduled article on the shared reading layout."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlsplit, urljoin

ROOT = Path(__file__).resolve().parents[1]


class ArticleMarkup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.stylesheets = []
        self.classes = set()
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.classes.update(attrs.get('class', '').split())
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.stylesheets.append(urlsplit(attrs['href']).path)


class ArticleLayoutTest(unittest.TestCase):
    def test_all_article_sources_use_shared_reading_layout(self):
        checked = 0
        for directory in ('aktuelles', 'standpunkte', 'energie', '_scheduled'):
            for path in (ROOT / directory).rglob('*.html'):
                if path.name == 'index.html':
                    continue
                markup = ArticleMarkup(path.read_text())
                with self.subTest(page=str(path.relative_to(ROOT))):
                    relative = path.relative_to(ROOT).as_posix()
                    if '/files/' in relative:
                        relative = relative.split('/files/', 1)[1]
                    sheets = [urlsplit(urljoin('https://marcopusceddu.de/' + relative, s)).path for s in markup.stylesheets]
                    base = '/assets/css/styles.css'
                    article = '/assets/css/articles.css'
                    self.assertEqual(sheets.count(article), 1)
                    self.assertLess(sheets.index(base), sheets.index(article))
                    self.assertNotIn('/assets/css/knowledge.css', sheets)
                    self.assertTrue({'article-page', 'article-header', 'article-deck', 'article-body'} <= markup.classes)
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == '__main__':
    unittest.main()
