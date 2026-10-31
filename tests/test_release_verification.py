import hashlib
import sys
import tempfile
import json
import unittest
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_release_live import check, has_link
from release_clock import todays_due

class LiveVerificationTests(unittest.TestCase):
    def test_http_200_error_page_is_not_success(self):
        manifest = {'hashes': {'energie/a.html': hashlib.sha256(b'actual article').hexdigest()}, 'links': {}}
        self.assertTrue(check(manifest, lambda path: b'404 error page'))
        self.assertEqual([], check(manifest, lambda path: b'actual article'))

    def test_image_and_archive_missing_are_detected(self):
        manifest = {'hashes': {'assets/a.jpg': hashlib.sha256(b'image').hexdigest()}, 'links': {'links/index.html': ['energie/a.html']}}
        errors = check(manifest, lambda path: b'<html></html>')
        self.assertEqual(2, len(errors))

    def test_relative_absolute_and_sitemap_links(self):
        self.assertTrue(has_link(b'<a href="../energie/a.html">A</a>', 'links/index.html', 'energie/a.html'))
        self.assertFalse(has_link(b'energie/a.html', 'links/index.html', 'energie/a.html'))
        self.assertTrue(has_link(b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://marcopusceddu.de/energie/a.html</loc></url></urlset>', 'sitemap.xml', 'energie/a.html'))

    def test_clock_respects_local_day_and_dst(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for i, stamp in enumerate(['2026-11-06T18:00:00+01:00','2027-04-09T18:00:00+02:00']):
                directory = root / '_scheduled' / str(i)
                directory.mkdir(parents=True)
                (directory/'release.json').write_text(json.dumps({'publish_at':stamp}))
            self.assertEqual('2026-11-06T18:00:00+01:00', todays_due(root, datetime.fromisoformat('2026-11-06T15:13:00+00:00'))[0].isoformat())
            self.assertEqual('2027-04-09T18:00:00+02:00', todays_due(root, datetime.fromisoformat('2027-04-09T15:13:00+00:00'))[0].isoformat())
            self.assertEqual([], todays_due(root, datetime.fromisoformat('2026-11-07T15:13:00+00:00')))
