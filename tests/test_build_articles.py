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
        shutil.copytree(SITE, self.root, ignore=shutil.ignore_patterns("__pycache__"))

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def test_complete_archive_six_previews_and_idempotency(self):
        before = self.snapshot()
        count, _ = build(self.root)
        self.assertEqual(count, 12)
        archive = Document((self.root / "aktuelles/index.html").read_text()).root
        self.assertEqual(len(archive.find("article", "news-card")), 12)
        home = Document((self.root / "index.html").read_text()).root
        self.assertEqual(len(home.find("article", "latest-preview-card")), 6)
        self.assertEqual(len(home.find("article", "news-card-featured")), 1)
        _, changed = build(self.root, check=True)
        self.assertFalse(changed)
        after = self.snapshot()
        for path in before:
            if path not in map(Path, ["index.html", "aktuelles/index.html", "sitemap.xml"]):
                self.assertEqual(before[path], after[path], str(path))

    def test_new_article_updates_all_lists_without_manual_entries(self):
        original = self.root / "aktuelles/organisationshoheit-gute-ideen.html"
        new = self.root / "aktuelles/aaa-pruefbeitrag.html"
        new.write_text(original.read_text().replace(original.name, new.name).replace("Gute Ideen verdienen eine Antwort", "Ein weiterer Prüfbeitrag"))
        count, _ = build(self.root)
        self.assertEqual(count, 13)
        for path in ["index.html", "aktuelles/index.html", "sitemap.xml"]:
            self.assertIn(new.name, (self.root / path).read_text())
        new.unlink()
        count, _ = build(self.root)
        self.assertEqual(count, 12)
        for path in ["index.html", "aktuelles/index.html", "sitemap.xml"]:
            self.assertNotIn(new.name, (self.root / path).read_text())

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


if __name__ == "__main__":
    unittest.main()
