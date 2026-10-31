from datetime import datetime
from pathlib import Path
import sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_site import assemble

class ReleasePlanTests(unittest.TestCase):
    def build(self, stamp):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        site=Path(tmp.name)/'site'
        assemble(ROOT,site,datetime.fromisoformat(stamp))
        return site

    def test_municipal_article_exact_boundary(self):
        article='aktuelles/warum-den-kommunen-das-geld-fehlt.html'
        image='assets/images/kommunale-finanzen-symbolbild-v1.jpg'
        for stamp,visible in [('2026-11-04T17:59:59+01:00',False),('2026-11-04T18:00:00+01:00',True)]:
            site=self.build(stamp)
            self.assertEqual(visible,(site/article).exists())
            self.assertEqual(visible,(site/image).exists())
            for listing in ['aktuelles/index.html','standpunkte/index.html','sitemap.xml','links/index.html']:
                self.assertEqual(visible,'warum-den-kommunen-das-geld-fehlt.html' in (site/listing).read_text())
            if visible:
                self.assertNotIn('noindex',(site/article).read_text())
                self.assertNotIn('127.0.0.1',(site/article).read_text())
            for legal in ['impressum.html','datenschutz.html']:
                self.assertEqual((ROOT/legal).read_bytes(),(site/legal).read_bytes())

    def test_energy_six_moved_without_publishing_reserved_topics(self):
        for stamp,visible in [('2027-01-08T18:00:00+01:00',False),('2027-03-05T17:59:59+01:00',False),('2027-03-05T18:00:00+01:00',True)]:
            site=self.build(stamp)
            self.assertEqual(visible,(site/'energie/negative-strompreise.html').exists())
            self.assertEqual(visible,(site/'assets/images/negative-strompreise.jpg').exists())
            for listing in ['energie/index.html','aktuelles/index.html','sitemap.xml','links/index.html']:
                self.assertEqual(visible,'negative-strompreise.html' in (site/listing).read_text())
            self.assertFalse((site/'README.md').exists())
            self.assertFalse((site/'_scheduled').exists())
