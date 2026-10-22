#!/usr/bin/env python3
"""Generate article lists and sitemap from published HTML; Python standard library only."""

import argparse
import json
from dataclasses import dataclass, field
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from build_links import outputs as link_outputs

BASE = "https://marcopusceddu.de/"
TOPICS = {
    "politik-finanzen": "Politik & Finanzen",
    "bauen-umwelt": "Bauen & Umwelt",
    "erneuerbare-energien": "Erneuerbare Energien",
    "digitalisierung": "Digitalisierung",
    "ehrenamt": "Ehrenamt",
    "persoenlich": "Persönlich",
}
MONTHS = ("", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def text(self):
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)

    def find(self, tag, css_class=None):
        matches = []
        for child in self.children:
            if isinstance(child, Node):
                if child.tag == tag and (not css_class or css_class in child.attrs.get("class", "").split()):
                    matches.append(child)
                matches.extend(child.find(tag, css_class))
        return matches


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def one(nodes, label):
    if len(nodes) != 1:
        raise ValueError(f"{label}: erwartet 1 Element, gefunden {len(nodes)}")
    return nodes[0]


def heading_html(node):
    # Retain the existing short no-wrap spans, but never copy arbitrary markup.
    parts = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(escape(child))
        elif child.tag == "span" and child.attrs.get("class") == "title-lock":
            parts.append('<span class="title-lock">' + escape(child.text()) + '</span>')
        else:
            parts.append(escape(child.text()))
    return "".join(parts)


def read_article(path, today=None, directory="aktuelles"):
    today = today or date.today()
    doc = Document(path.read_text(encoding="utf-8")).root
    header = one(doc.find("header", "article-header"), f"{path.name}: Artikelkopf")
    heading = one(header.find("h1"), f"{path.name}: Überschrift")
    news = one(header.find("p", "news-meta"), f"{path.name}: Datum/Rubrik")
    stamp = one(news.find("time"), f"{path.name}: Datum")
    category = one(news.find("span"), f"{path.name}: Rubrik").text().strip()
    published = date.fromisoformat(stamp.attrs.get("datetime", ""))
    metadata = {}
    for node in doc.find("meta"):
        key = node.attrs.get("property") or node.attrs.get("name")
        if key:
            if key in metadata:
                raise ValueError(f"{path.name}: doppelte Metadaten {key}")
            metadata[key] = node.attrs.get("content", "")
    canonical = one([n for n in doc.find("link") if n.attrs.get("rel") == "canonical"], f"{path.name}: Canonical").attrs.get("href")
    url = BASE + directory + "/" + path.name
    if canonical != url or metadata.get("og:url") != url:
        raise ValueError(f"{path.name}: Canonical und og:url müssen {url} entsprechen")
    title = heading.text().strip()
    if metadata.get("og:title") != title:
        raise ValueError(f"{path.name}: og:title und sichtbare Überschrift weichen ab")
    if metadata.get("article:published_time") != published.isoformat():
        raise ValueError(f"{path.name}: sichtbares Datum und article:published_time weichen ab")
    if published > today:
        raise ValueError(f"{path.name}: zukünftiges Veröffentlichungsdatum; Entwürfe außerhalb der Website aufbewahren")
    modified = metadata.get("article:modified_time")
    if modified and not published <= date.fromisoformat(modified) <= today:
        raise ValueError(f"{path.name}: ungültiges Änderungsdatum")
    summary = metadata.get("article:summary") or metadata.get("og:description", "")
    if not all([title, category, summary, metadata.get("article:author"), metadata.get("og:image")]):
        raise ValueError(f"{path.name}: Titel, Rubrik, Kurztext, Autor oder Vorschaubild fehlen")
    places = {place.strip().casefold() for place in metadata.get("article:places", "").split(",") if place.strip()}
    topics = {topic.strip() for topic in metadata.get("article:topics", "").split(",") if topic.strip()}
    if not topics or topics - TOPICS.keys():
        raise ValueError(f"{path.name}: article:topics muss mindestens ein gültiges Thema enthalten; erlaubt: {', '.join(TOPICS)}")
    listing = metadata.get("article:listing", "current")
    if listing not in {"current", "background"}:
        raise ValueError(f"{path.name}: article:listing muss current oder background sein")
    return dict(directory=directory, collection=metadata.get("article:collection", ""), listing=listing, filename=path.name, title=title, heading=heading_html(heading), category=category, places=places, topics=topics,
                summary=summary, published=published, modified=modified, url=url)


def card(article, level, css_class, prefix="", filterable=False):
    a = article
    d = a["published"]
    label = f"{d.day}. {MONTHS[d.month]} {d.year}"
    if a.get("directory", "aktuelles") != "aktuelles":
        prefix = prefix.replace("aktuelles/", a["directory"] + "/") if prefix else "../" + a["directory"] + "/"
    href = escape(prefix + a["filename"], quote=True)
    topics_attr = ' data-topics="' + ' '.join(sorted(a['topics'])) + '"' if filterable else ''
    return f'''<article class="{css_class}"{topics_attr}>
  <p class="news-meta"><time datetime="{d.isoformat()}">{label}</time><span>{escape(a['category'])}</span></p>
  <h{level}><a href="{href}">{a['heading']}</a></h{level}>
  <p>{escape(a['summary'])}</p>
  <a class="card-link" href="{href}" aria-label="{escape('Beitrag lesen: ' + a['title'], quote=True)}">Beitrag lesen <span aria-hidden="true">↗</span></a>
</article>'''


def topic_buttons(articles):
    counts = {key: sum(key in a["topics"] for a in articles) for key in TOPICS}
    choices = [("alle", "Alle", len(articles))]
    choices.extend((key, label, counts[key]) for key, label in TOPICS.items() if counts[key])
    return "\n".join(
        f'<button type="button" class="article-filter-button" data-topic="{key}" '
        f'aria-pressed="{"true" if key == "alle" else "false"}" aria-controls="article-list">'
        f'{escape(label)} <span class="article-filter-count" aria-hidden="true">{count}</span></button>'
        for key, label, count in choices
    )


def replace_region(source, name, content, indent):
    start, end = f"<!-- BEGIN GENERATED:{name} -->", f"<!-- END GENERATED:{name} -->"
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Fehlende oder doppelte Markierungen: {name}")
    rendered = "\n".join(indent + line if line else "" for line in content.splitlines())
    return re.sub(re.escape(start) + r".*?" + re.escape(end),
                  lambda _: start + "\n" + rendered + "\n" + indent + end, source, flags=re.S)


def outputs(root, today=None):
    articles = [read_article(p, today=today) for p in sorted((root / "aktuelles").glob("*.html")) if p.name != "index.html"]
    for path in sorted((root / "energie").glob("*.html")):
        if 'name="article:collection" content="energie"' in path.read_text(encoding="utf-8"):
            articles.append(read_article(path, today=today, directory="energie"))
    series_directory = "standpunkte/was-uns-zusammenhaelt"
    for path in sorted((root / series_directory).glob("*.html")):
        if 'name="article:collection" content="zusammenhalt"' in path.read_text(encoding="utf-8"):
            articles.append(read_article(path, today=today, directory=series_directory))
    if not articles:
        raise ValueError("Keine veröffentlichten Artikel gefunden")
    # Editorial placement is independent of the real publication date.
    articles.sort(key=lambda a: (a["listing"] == "background", -a["published"].toordinal(), a["filename"]))
    home_path, archive_path = root / "index.html", root / "aktuelles/index.html"
    home = home_path.read_text(encoding="utf-8")
    home = replace_region(home, "featured", card(articles[0], 3, "news-card news-card-featured", "aktuelles/"), "      ")
    previews = "\n".join(card(a, 3, "latest-preview-card", "aktuelles/") for a in articles[1:3])
    home = replace_region(home, "previews", previews, "          ")
    archive = archive_path.read_text(encoding="utf-8")
    archive = replace_region(archive, "topic-filters", topic_buttons(articles), "          ")
    cards = "\n".join(card(a, 2, "news-card news-card-featured" if i == 0 else "news-card", filterable=True) for i, a in enumerate(articles))
    archive = replace_region(archive, "archive", cards, "        ")
    urbar_path = root / "urbar/index.html"
    urbar = urbar_path.read_text(encoding="utf-8")
    local_articles = [a for a in articles if "urbar" in a["places"]]
    local_cards = "\n".join(card(a, 3, "latest-preview-card", "../aktuelles/") for a in local_articles)
    urbar = replace_region(urbar, "urbar", local_cards, "        ")

    sitemap_path = root / "sitemap.xml"
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    old = ET.fromstring(sitemap_path.read_text(encoding="utf-8"))
    entries = [(u.findtext(ns + "loc"), u.findtext(ns + "lastmod")) for u in old.findall(ns + "url")]
    previous = dict(entries)
    # Keep non-article URLs and historic modification dates; never use build time.
    urls = [(url, modified) for url, modified in entries if url not in {a["url"] for a in articles} and not (url.startswith(BASE + "aktuelles/") and url.endswith(".html"))]
    for a in articles:
        candidates = [a["published"].isoformat(), a["modified"], previous.get(a["url"])]
        modified = max(date.fromisoformat(v) for v in candidates if v).isoformat()
        urls.append((a["url"], modified))
    if len({url for url, _ in urls}) != len(urls):
        raise ValueError("Doppelte URL in der Sitemap")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, modified in urls:
        xml.extend(["  <url>", "    <loc>" + escape(url) + "</loc>"])
        if modified:
            xml.append("    <lastmod>" + modified + "</lastmod>")
        xml.append("  </url>")
    xml.append("</urlset>")
    generated = {home_path: home, archive_path: archive, urbar_path: urbar, sitemap_path: "\n".join(xml) + "\n"}
    knowledge_path = root / "standpunkte/index.html"
    if knowledge_path.exists():
        knowledge = knowledge_path.read_text(encoding="utf-8")
        if "<!-- BEGIN GENERATED:standpunkte -->" in knowledge:
            selected = [a for a in articles if a["collection"] == "standpunkte"]
            cards = "\n".join(card(a, 3, "news-card knowledge-card", "/aktuelles/") for a in selected)
            section = ("<section class=\"knowledge-topic\" aria-labelledby=\"wirtschaft-title\">"
                       "<div class=\"knowledge-topic-heading\"><p class=\"eyebrow\">Wirtschaft &amp; Gesellschaft</p>"
                       "<h2 id=\"wirtschaft-title\">Freiheit und Verantwortung.</h2></div>" + cards + "</section>") if selected else ""
            generated[knowledge_path] = replace_region(knowledge, "standpunkte", section, "    ")
    energy_path = root / "energie/index.html"
    if energy_path.exists():
        energy = energy_path.read_text(encoding="utf-8")
        if "<!-- BEGIN GENERATED:energie -->" in energy:
            selected = sorted((a for a in articles if a["collection"] == "energie"), key=lambda a: a["published"])
            cards = "\n".join(card(a, 3, "news-card knowledge-card", "/energie/") for a in selected)
            section = ('<section class="knowledge-topic" aria-labelledby="folgen-title"><div class="knowledge-topic-heading"><h2 id="folgen-title">Weitere Folgen</h2></div>' + cards + '</section>') if selected else ''
            generated[energy_path] = replace_region(energy, "energie", section, "    ")
    series_path = root / series_directory / "index.html"
    if series_path.exists():
        planned = json.loads((series_path.parent / "reihe.json").read_text(encoding="utf-8"))
        released = {a["category"].rsplit(" ", 1)[-1]: a for a in articles if a["collection"] == "zusammenhalt"}
        items = []
        for episode in planned:
            a = released.get(str(episode["number"]))
            stamp = date.fromisoformat(episode["date"])
            label = f"{stamp.day}. {MONTHS[stamp.month]} {stamp.year}"
            title = escape(episode["title"])
            if a:
                title = '<a href="' + escape(a["url"], quote=True) + '">' + title + '</a>'
            status = "Veröffentlicht" if a else "Geplant"
            items.append(f'<li class="series-episode"><p class="news-meta">Folge {episode["number"]} · {status} · <time datetime="{stamp.isoformat()}">{label}</time> · 18 Uhr</p><h3>{title}</h3><p>{escape(episode["deck"])}</p></li>')
        series = replace_region(series_path.read_text(encoding="utf-8"), "zusammenhalt", '<ol>' + ''.join(items) + '</ol>', '    ')
        if not released:
            status = '<p>Die Reihe beginnt am <strong>6. November 2026 um 18 Uhr</strong>. Weitere Beiträge folgen in der Regel alle zwei Wochen. Über Weihnachten, Neujahr und Ostern gibt es eine Pause.</p>'
        elif len(released) == len(planned):
            status = '<p>Alle elf Folgen der Reihe sind veröffentlicht. Lesen Sie die Beiträge in der Reihenfolge oder wählen Sie das Thema, das Sie interessiert.</p>'
        else:
            status = f'<p>Bereits {len(released)} von elf Folgen sind veröffentlicht. Weitere Beiträge folgen an den unten angekündigten Terminen, jeweils um 18 Uhr.</p>'
        generated[series_path] = replace_region(series, "series-status", status, '    ')
    generated.update(link_outputs(root, today=today))
    return generated, len(articles)


def build(root, check=False, today=None):
    # Validate and render every output before writing any file.
    generated, count = outputs(root, today=today)
    changed = [p for p, content in generated.items() if p.read_text(encoding="utf-8") != content]
    if check and changed:
        raise ValueError("Veraltete Artikelübersichten: " + ", ".join(str(p.relative_to(root)) for p in changed))
    if not check:
        for path in changed:
            path.write_text(generated[path], encoding="utf-8")
    return count, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Nur prüfen; keine Dateien ändern")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        count, changed = build(args.root.resolve(), args.check)
    except (ValueError, OSError, ET.ParseError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    print(f"{count} Artikel geprüft; {len(changed)} Dateien aktualisiert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
