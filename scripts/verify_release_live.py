"""Verify deployed release bytes and listing links, not just an HTTP 200."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.request
from urllib.parse import urljoin
from html.parser import HTMLParser

BASE = "https://marcopusceddu.de/"
ROOT = Path(__file__).resolve().parents[1]
LISTINGS = ("index.html", "aktuelles/index.html", "energie/index.html", "standpunkte/index.html", "links/index.html", "sitemap.xml")

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.urls.add(attrs["href"])

def has_link(data, page, article):
    text = data.decode("utf-8")
    expected = urljoin(BASE, article)
    if page.endswith(".xml"):
        import xml.etree.ElementTree as ET
        return expected in [e.text for e in ET.fromstring(text).iter() if e.tag.endswith("}loc") or e.tag == "loc"]
    parser = Links()
    parser.feed(text)
    return expected in {urljoin(urljoin(BASE, page), link).split("#")[0] for link in parser.urls}

def manifest_for(root, site):
    hashes, links, articles = {}, {}, []
    for manifest in sorted((root / "_scheduled").glob("*/release.json")):
        release = json.loads(manifest.read_text())
        article = release["article"]
        # The built artifact is the source of truth for this exact deployment.
        if not (site / article).is_file():
            continue
        articles.append({"path": article, "publish_at": release["publish_at"]})
        for source in (manifest.parent / "files").rglob("*"):
            if source.is_file():
                path = str(source.relative_to(manifest.parent / "files"))
                hashes[path] = hashlib.sha256((site / path).read_bytes()).hexdigest()
        for page in LISTINGS:
            if (site / page).is_file() and has_link((site / page).read_bytes(), page, article):
                links.setdefault(page, []).append(article)
    return {"articles": articles, "hashes": hashes, "links": links}

def check(manifest, fetch):
    errors = []
    for path, expected in manifest["hashes"].items():
        try:
            if hashlib.sha256(fetch(path)).hexdigest() != expected:
                errors.append(path + ": content differs")
        except Exception as error:
            errors.append(path + ": " + str(error))
    for page, articles in manifest["links"].items():
        try:
            data = fetch(page)
            for article in articles:
                if not has_link(data, page, article):
                    errors.append(page + ": missing " + article)
        except Exception as error:
            errors.append(page + ": " + str(error))
    return errors

def fetch_live(path):
    request = urllib.request.Request(urljoin(BASE, path), headers={"User-Agent": "MarcoWebsiteReleaseCheck/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise ValueError("HTTP " + str(response.status))
        if not response.url.startswith(BASE):
            raise ValueError("Unexpected redirect")
        return response.read()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--attempts", type=int, default=5)
    args = parser.parse_args()
    if args.site:
        args.manifest.write_text(json.dumps(manifest_for(ROOT, args.site), indent=2))
    else:
        manifest = json.loads(args.manifest.read_text())
        for attempt in range(args.attempts):
            errors = check(manifest, fetch_live)
            if not errors:
                break
            print("Live check pending:", errors, flush=True)
            if attempt + 1 < args.attempts:
                time.sleep(20)
        if errors:
            raise SystemExit("Live verification failed; deployment is not confirmed")
        report = "Live verified at " + datetime.now(timezone.utc).isoformat() + "\n" + "\n".join("- " + BASE + a["path"] for a in manifest["articles"])
        print(report)
        import os
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
                f.write(report + "\n")
