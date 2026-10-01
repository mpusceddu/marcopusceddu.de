"""Check publishing invariants in disposable copies of the real website."""
from datetime import date, timedelta
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE / "scripts"))
from build_articles import build, Document


class ArticleBuildTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "site"
        shutil.copytree(SITE, self.root, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def test_complete_archive_six_previews_and_idempotency(self):
        before = self.snapshot()
        count, _ = build(self.root)
        self.assertEqual(count, 13)
        archive = Document((self.root / "aktuelles/index.html").read_text()).root
        self.assertEqual(len(archive.find("article", "news-card")), 13)
        home = Document((self.root / "index.html").read_text()).root
        self.assertEqual(len(home.find("article", "latest-preview-card")), 6)
        self.assertEqual(len(home.find("article", "news-card-featured")), 1)
        _, changed = build(self.root, check=True)
        self.assertFalse(changed)
        after = self.snapshot()
        for path in before:
            if path not in map(Path, ["index.html", "aktuelles/index.html", "urbar/index.html", "sitemap.xml"]):
                self.assertEqual(before[path], after[path], str(path))

    def test_urbar_lists_only_tagged_articles_and_removes_stale_entries(self):
        build(self.root)
        page = self.root / "urbar/index.html"
        document = Document(page.read_text()).root
        self.assertEqual(len(document.find("article", "latest-preview-card")), 4)
        self.assertNotIn('href="../aktuelles/haushalt-2026.html"', page.read_text())
        original = self.root / "aktuelles/organisationshoheit-gute-ideen.html"
        new = self.root / "aktuelles/aaa-urbar-test.html"
        source = original.read_text().replace(original.name, new.name)
        source = source.replace('<head>', '<head>\n<meta name="article:places" content=" Urbar, Vallendar ">')
        new.write_text(source)
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Veraltete Artikelübersichten"):
            build(self.root, check=True)
        self.assertEqual(before, self.snapshot())
        build(self.root)
        self.assertIn('href="../aktuelles/aaa-urbar-test.html"', page.read_text())
        self.assertLess(page.read_text().index(new.name), page.read_text().index('bauturbo-suedliche-ortsmitte.html'))
        new.unlink()
        build(self.root)
        self.assertNotIn(new.name, page.read_text())
        self.assertIn('https://marcopusceddu.de/urbar/', (self.root / 'sitemap.xml').read_text())

    def test_new_article_updates_all_lists_without_manual_entries(self):
        original = self.root / "aktuelles/organisationshoheit-gute-ideen.html"
        new = self.root / "aktuelles/aaa-pruefbeitrag.html"
        new.write_text(original.read_text().replace(original.name, new.name).replace("Gute Ideen verdienen eine Antwort", "Ein weiterer Prüfbeitrag"))
        count, _ = build(self.root)
        self.assertEqual(count, 14)
        for path in ["index.html", "aktuelles/index.html", "sitemap.xml"]:
            self.assertIn(new.name, (self.root / path).read_text())
        new.unlink()
        count, _ = build(self.root)
        self.assertEqual(count, 13)
        for path in ["index.html", "aktuelles/index.html", "sitemap.xml"]:
            self.assertNotIn(new.name, (self.root / path).read_text())

    def test_background_keeps_real_date_without_displacing_current_articles(self):
        home_before = (self.root / "index.html").read_text()
        build(self.root)
        self.assertEqual(home_before, (self.root / "index.html").read_text())
        archive = Document((self.root / "aktuelles/index.html").read_text()).root
        cards = archive.find("article", "news-card")
        self.assertEqual(cards[0].find("a")[0].attrs["href"], "organisationshoheit-gute-ideen.html")
        background = cards[-1]
        self.assertEqual(background.find("a")[0].attrs["href"], "erneuerbare-energien-urbar.html")
        self.assertEqual(background.find("time")[0].attrs["datetime"], "2026-10-01")
        self.assertIn("Hintergrund", background.text())
        self.assertEqual(background.attrs["data-topics"], "erneuerbare-energien")
        urbar = Document((self.root / "urbar/index.html").read_text()).root
        self.assertIn("erneuerbare-energien-urbar.html", urbar.find("article", "latest-preview-card")[-1].find("a")[0].attrs["href"])
        # An equally recent current article still becomes the lead automatically.
        original = self.root / "aktuelles/organisationshoheit-gute-ideen.html"
        new = self.root / "aktuelles/neue-meldung.html"
        new.write_text(original.read_text().replace(original.name, new.name).replace("2026-09-28", "2026-10-01"))
        build(self.root)
        home = Document((self.root / "index.html").read_text()).root
        self.assertEqual(home.find("article", "news-card-featured")[0].find("a")[0].attrs["href"], "aktuelles/neue-meldung.html")

    def test_invalid_listing_never_partially_writes(self):
        p = self.root / "aktuelles/erneuerbare-energien-urbar.html"
        p.write_text(p.read_text().replace('content="background"', 'content="backgroun"'))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "article:listing"):
            build(self.root)
        self.assertEqual(before, self.snapshot())

    def test_invalid_metadata_never_partially_rewrites_outputs(self):
        p = self.root / "aktuelles/willkommen.html"
        p.write_text(p.read_text().replace('rel="canonical"', 'rel="alternate"'))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Canonical"):
            build(self.root)
        self.assertEqual(before, self.snapshot())

    def test_check_reports_stale_output_without_writing(self):
        p = self.root / "aktuelles/willkommen.html"
        p.write_text(p.read_text().replace('content="Ein eigener Ort', 'content="Ein persönlicher Ort'))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Veraltete Artikelübersichten"):
            build(self.root, check=True)
        self.assertEqual(before, self.snapshot())

    def test_future_article_is_rejected(self):
        p = self.root / "aktuelles/organisationshoheit-gute-ideen.html"
        p.write_text(p.read_text().replace("2026-09-28", (date.today() + timedelta(days=1)).isoformat()))
        with self.assertRaisesRegex(ValueError, "zukünftiges Veröffentlichungsdatum"):
            build(self.root)

    def test_modification_dates_are_preserved(self):
        build(self.root)
        sitemap = (self.root / "sitemap.xml").read_text()
        self.assertIn("willkommen.html</loc>\n    <lastmod>2026-09-28</lastmod>", sitemap)
        self.assertIn("haushalt-2026.html</loc>\n    <lastmod>2026-08-26</lastmod>", sitemap)

    def test_topics_cover_archive_and_empty_topic_disappears(self):
        build(self.root)
        page = self.root / "aktuelles/index.html"
        archive = Document(page.read_text()).root
        cards = archive.find("article", "news-card")
        self.assertTrue(all(card.attrs.get("data-topics") for card in cards))
        by_file = {card.find("a")[0].attrs["href"]: card for card in cards}
        self.assertEqual(set(by_file["organisationshoheit-gute-ideen.html"].attrs["data-topics"].split()),
                         {"politik-finanzen", "digitalisierung"})
        self.assertIn('data-topic="ehrenamt"', page.read_text())
        (self.root / "aktuelles/jahresuebung-feuerwehr-vallendar-2026.html").unlink()
        build(self.root)
        self.assertNotIn('data-topic="ehrenamt"', page.read_text())
        archive = Document(page.read_text()).root
        all_button = next(b for b in archive.find("button") if b.attrs.get("data-topic") == "alle")
        self.assertEqual(all_button.find("span")[0].text(), "12")

    def test_missing_or_unknown_topic_never_partially_writes(self):
        p = self.root / "aktuelles/willkommen.html"
        original = p.read_text()
        for replacement in ["", '<meta name="article:topics" content="persoenlich, typo">']:
            with self.subTest(replacement=replacement):
                p.write_text(original.replace('<meta name="article:topics" content="persoenlich">', replacement))
                before = self.snapshot()
                with self.assertRaisesRegex(ValueError, "article:topics"):
                    build(self.root)
                self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main()
