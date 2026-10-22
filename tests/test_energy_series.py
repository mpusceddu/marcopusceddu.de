"""Verify that approved energy articles cannot leak before their individual release."""
from datetime import datetime,date,timedelta
from pathlib import Path
import json,shutil,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_site import assemble
from build_articles import build,read_article
class EnergySeriesTests(unittest.TestCase):
 def test_every_release_boundary_and_existing_content(self):
  manifests=sorted((ROOT/'_scheduled').glob('energie-*/release.json'))
  self.assertEqual(len(manifests),7)
  for m in manifests:
   release=json.loads(m.read_text());due=datetime.fromisoformat(release['publish_at']);article=release['article'];image='assets/images/'+Path(article).stem+'.jpg'
   for stamp,visible in [(due-timedelta(seconds=1),False),(due,True)]:
    with self.subTest(article=article,time=stamp), tempfile.TemporaryDirectory() as tmp:
     out=Path(tmp)/'site';assemble(ROOT,out,stamp)
     self.assertEqual((out/article).is_file(),visible)
     self.assertEqual((out/image).is_file(),visible)
     for page in ['energie/index.html','aktuelles/index.html','sitemap.xml','links/index.html']:
      self.assertEqual(Path(article).name in (out/page).read_text(),visible,page)
     self.assertTrue((out/'energie/strom-verdient-eine-sachliche-debatte.html').is_file())
     self.assertFalse((out/'standpunkte/gdpr-legal-cookie.html').exists())
     self.assertFalse((out/'_scheduled').exists())
     self.assertEqual((out/'datenschutz.html').read_bytes(),(ROOT/'datenschutz.html').read_bytes())
     if visible:
      self.assertEqual(read_article(out/article,today=stamp.date(),directory='energie')['url'],'https://marcopusceddu.de/'+article)
      # Rebuilding an already generated site must not duplicate its sitemap entries.
      build(out,today=stamp.date())
 def test_launch_times_cover_all_manifests(self):
  workflow=(ROOT/'.github/workflows/pages.yml').read_text()
  self.assertIn("43 16 * * 5",workflow)
  self.assertIn("13 17-23 * * 5",workflow)
  for m in (ROOT/'_scheduled').glob('energie-*/release.json'):
   due=datetime.fromisoformat(json.loads(m.read_text())['publish_at'])
   self.assertEqual((due.hour,due.utcoffset().total_seconds()),(18,3600))
   self.assertEqual(due.weekday(),4)
   self.assertIn(due.date().isoformat(),workflow)
if __name__=='__main__':unittest.main()
