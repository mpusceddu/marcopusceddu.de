#!/usr/bin/env python3
"""Render /links/ from public article files; no browser JavaScript or external requests."""
import argparse
from datetime import date
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlparse

BASE = "https://marcopusceddu.de/"
MONTHS = ("", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember")

class Metadata(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.values = {}
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.values[attrs.get("property") or attrs.get("name")] = attrs.get("content", "")

def articles(root, today):
    result = []
    for folder in ("aktuelles", "standpunkte", "energie"):
        for path in sorted((root / folder).rglob("*.html")):
            values = Metadata(path.read_text(encoding="utf-8")).values
            if not values.get("article:published_time"):
                continue
            published = date.fromisoformat(values["article:published_time"])
            if published > today or "noindex" in values.get("robots", ""):
                continue
            rel = path.relative_to(root).as_posix()
            if values.get("og:url") != BASE + rel:
                raise ValueError(f"Unerwartete Artikeladresse: {rel}")
            image = urlparse(values["og:image"])
            if image.scheme != "https" or image.netloc != "marcopusceddu.de" or not (root / image.path.lstrip("/")).is_file():
                raise ValueError(f"Vorschaubild fehlt: {rel}")
            result.append(dict(path=rel, title=values["og:title"], summary=values.get("article:summary") or values["og:description"], image=image.path, published=published))
    return sorted(result, key=lambda a: (-a["published"].toordinal(), a["path"]))

def label(stamp):
    return f"{stamp.day}. {MONTHS[stamp.month]} {stamp.year}"

def select_featured(items, config, today):
    expires = date.fromisoformat(config["expires"]) if config.get("expires") else None
    if config.get("path") and (expires is None or today <= expires):
        matches = [a for a in items if a["path"] == config["path"]]
        if not matches:
            raise ValueError("Der hervorgehobene Beitrag muss bereits veröffentlicht sein.")
        return matches[0]
    return items[0]

def region(source, name, content):
    start, end = f"<!-- BEGIN GENERATED:{name} -->", f"<!-- END GENERATED:{name} -->"
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Markierungen fehlen oder sind doppelt: {name}")
    return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: start + "\n" + content + "\n        " + end, source, flags=re.S)

def outputs(root, today=None):
    page = root / "links/index.html"
    if not page.exists():
        return {}
    today = today or date.today()
    items = articles(root, today)
    if not items:
        raise ValueError("Keine veröffentlichten Beiträge für /links/ gefunden.")
    config = json.loads((root / "links/featured.json").read_text(encoding="utf-8"))
    if config.get("path"):
        pinned = (root / config["path"]).resolve()
        if root.resolve() not in pinned.parents or not pinned.is_file():
            raise ValueError("Der hervorgehobene Beitrag muss bereits veröffentlicht sein.")
        published = Metadata(pinned.read_text(encoding="utf-8")).values.get("article:published_time")
        if not published:
            raise ValueError("Der hervorgehobene Beitrag benötigt ein Veröffentlichungsdatum.")
        # A future-dated focus must never leak into an earlier build.
        if date.fromisoformat(published) > today:
            config = {}
    a = select_featured(items, config, today)
    e = lambda value: escape(str(value), quote=True)
    featured = f'''<a class="feature-card" href="/{e(a['path'])}">
          <img src="{e(a['image'])}" alt="" width="1600" height="800" decoding="async">
          <div class="feature-body"><p class="feature-meta"><time datetime="{a['published']}">{label(a['published'])}</time> · Mein aktueller Beitrag</p>
          <h3>{e(a['title'])}</h3><p>{e(a['summary'])}</p><span class="feature-cta">Beitrag lesen <span aria-hidden="true">↗</span></span></div>
        </a>'''
    recent = []
    for a in items[:3]:
        recent.append(f'''<a class="recent-link" href="/{e(a['path'])}"><img src="{e(a['image'])}" alt="" width="88" height="72" loading="lazy" decoding="async"><div><time class="recent-meta" datetime="{a['published']}">{label(a['published'])}</time><h3>{e(a['title'])}</h3></div><span class="arrow" aria-hidden="true">↗</span></a>''')
    source = page.read_text(encoding="utf-8")
    source = region(source, "links-featured", featured)
    source = region(source, "links-recent", "\n          ".join(recent))
    return {page: source}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = outputs(args.root.resolve())
    changed = [p for p, source in generated.items() if p.read_text(encoding="utf-8") != source]
    if args.check and changed:
        raise SystemExit("/links/ ist veraltet")
    if not args.check:
        for path in changed:
            path.write_text(generated[path], encoding="utf-8")
    print(f"/links/: {len(changed)} Dateien aktualisiert.")
