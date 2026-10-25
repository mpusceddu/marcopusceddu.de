"""Protect scheduled articles, nested navigation, and the public series teaser."""
from datetime import datetime,timedelta,date
from pathlib import Path
import json,sys,tempfile,unittest,shutil
from urllib.parse import urlsplit,urljoin,unquote
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_site import assemble
from build_articles import Document,build,read_article

class ZusammenhaltTests(unittest.TestCase):
 def test_individual_release_boundaries_and_overview(self):
  manifests=sorted((ROOT/'_scheduled').glob('zusammenhalt-*/release.json'))
  self.assertEqual(len(manifests),11)
  workflow=(ROOT/'.github/workflows/pages.yml').read_text()
  for m in manifests:
   release=json.loads(m.read_text());due=datetime.fromisoformat(release['publish_at']);article=release['article']
   self.assertEqual((due.hour,due.weekday()),(18,4))
   self.assertIn(due.date().isoformat(),workflow)
   for stamp,visible in [(due-timedelta(seconds=1),False),(due,True)]:
    with self.subTest(article=article,stamp=stamp),tempfile.TemporaryDirectory() as tmp:
     out=Path(tmp)/'site';assemble(ROOT,out,stamp)
     self.assertEqual((out/article).is_file(),visible)
     self.assertEqual((out/('assets/images/'+Path(article).stem+'.jpg')).is_file(),visible)
     for page in ['standpunkte/was-uns-zusammenhaelt/index.html','aktuelles/index.html','sitemap.xml','links/index.html']:
      self.assertEqual(Path(article).name in (out/page).read_text(),visible,page)
     self.assertFalse((out/'standpunkte/gdpr-legal-cookie.html').exists())
     self.assertFalse((out/'_scheduled').exists())
     build(out,today=stamp.date())

 def test_teaser_and_all_final_internal_destinations(self):
  for stamp in [datetime.fromisoformat('2026-10-22T17:00:00+02:00'),datetime.fromisoformat('2027-04-23T18:00:00+02:00')]:
   with self.subTest(stamp=stamp),tempfile.TemporaryDirectory() as tmp:
    source=Path(tmp)/'source';shutil.copytree(ROOT,source,ignore=shutil.ignore_patterns('.git','__pycache__'))
    for path in (source/'energie').glob('*.html'):
     if 'name="article:collection" content="energie"' in path.read_text() and read_article(path,today=date.max,directory='energie')['published']>stamp.date():path.unlink()
    out=Path(tmp)/'site';assemble(source,out,stamp)
    landing=(out/'standpunkte/was-uns-zusammenhaelt/index.html').read_text()
    self.assertIn('Mario Draghis',landing)
    self.assertIn('was-uns-zusammenhaelt-teaser.jpg',(out/'standpunkte/index.html').read_text())
    self.assertIn('/standpunkte/was-uns-zusammenhaelt/',(out/'index.html').read_text())
    self.assertEqual(len(Document(landing).root.find('li','series-episode')),11)
    for path in (out/'standpunkte/was-uns-zusammenhaelt').glob('*.html'):
     doc=Document(path.read_text()).root
     for node in doc.find('a')+doc.find('img')+doc.find('link'):
      target=node.attrs.get('href') or node.attrs.get('src')
      if not target:continue
      url=urlsplit(urljoin('https://marcopusceddu.de/'+path.relative_to(out).as_posix(),target))
      if url.netloc!='marcopusceddu.de':continue
      dest=out/unquote(url.path).lstrip('/')
      if dest.is_dir():dest=dest/'index.html'
      self.assertTrue(dest.is_file(),f'{path.name}: {target}')
      if url.fragment and dest.suffix=='.html':
       self.assertIn('id="'+url.fragment+'"',dest.read_text(),f'{path.name}: {target}')

if __name__=='__main__':unittest.main()
