import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import assemble
class ScheduledReleaseTests(unittest.TestCase):
    def build_at(self, timestamp):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / 'site'
        assemble(ROOT, output, datetime.fromisoformat(timestamp))
        return output
    def test_absent_one_second_before_release(self):
        output = self.build_at('2026-10-07T11:59:59+02:00')
        self.assertFalse((output / 'aktuelles/kas-finanzierung.html').exists())
        self.assertFalse((output / 'assets/images/kas-finanzierung.jpg').exists())
        for name in ['index.html', 'aktuelles/index.html', 'sitemap.xml']:
            self.assertNotIn('kas-finanzierung.html', (output/name).read_text())
        for name in ['_scheduled', 'scripts', 'tests', '.git', '.github']:
            self.assertFalse((output/name).exists())
    def test_present_at_release_and_later(self):
        for timestamp in ['2026-10-07T12:00:00+02:00', '2026-12-01T12:00:00+01:00']:
            output = self.build_at(timestamp)
            self.assertTrue((output/'aktuelles/kas-finanzierung.html').is_file())
            self.assertTrue((output/'assets/images/kas-finanzierung.jpg').is_file())
            for name in ['index.html', 'aktuelles/index.html', 'sitemap.xml']:
                self.assertIn('kas-finanzierung.html', (output/name).read_text())
            for name in ['impressum.html', 'datenschutz.html', 'CNAME']:
                self.assertEqual((ROOT/name).read_bytes(), (output/name).read_bytes())
    def test_europa_absent_before_release_preserves_kas(self):
        output = self.build_at('2026-10-26T11:59:59+01:00')
        self.assertTrue((output/'aktuelles/kas-finanzierung.html').is_file())
        self.assertFalse((output/'aktuelles/europa-zusammenarbeit.html').exists())
        self.assertFalse((output/'assets/images/europa-zusammenarbeit.jpg').exists())
        for name in ['index.html', 'aktuelles/index.html', 'sitemap.xml']:
            self.assertNotIn('europa-zusammenarbeit.html', (output/name).read_text())
    def test_europa_published_at_noon_cet_and_later(self):
        for timestamp in ['2026-10-26T11:00:00+00:00', '2026-12-01T12:00:00+01:00']:
            output = self.build_at(timestamp)
            for slug in ['kas-finanzierung', 'europa-zusammenarbeit']:
                self.assertTrue((output/f'aktuelles/{slug}.html').is_file())
                self.assertTrue((output/f'assets/images/{slug}.jpg').is_file())
                for name in ['index.html', 'aktuelles/index.html', 'sitemap.xml']:
                    self.assertIn(slug+'.html', (output/name).read_text())
    def test_offset_and_timezone_required(self):
        output = self.build_at('2026-10-07T10:00:00+00:00')
        self.assertTrue((output/'aktuelles/kas-finanzierung.html').is_file())
        with self.assertRaises(ValueError):
            self.build_at('2026-10-07T12:00:00')
if __name__ == '__main__':
    unittest.main()
