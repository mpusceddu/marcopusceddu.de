# marcopusceddu.de

[![Website](https://img.shields.io/badge/Website-marcopusceddu.de-071f33?style=flat-square)](https://marcopusceddu.de/)

Persönliche Website von **Marco Pusceddu**: Familienmensch, Unternehmer und Kommunalpolitiker aus Urbar.

[![Vorschau der Website](assets/images/og-20260928.jpg)](https://marcopusceddu.de/)

## Live-Version

[**marcopusceddu.de öffnen**](https://marcopusceddu.de/)

## Inhalt

Die Website stellt meinen beruflichen Hintergrund und mein kommunalpolitisches Engagement in **Urbar** und der **Verbandsgemeinde Vallendar** vor. Unter **Aktuelles** erscheinen Berichte, Einblicke und persönliche Positionen. Die Seite bietet außerdem direkte Kontaktmöglichkeiten sowie Impressum und Datenschutzerklärung.

## Öffentliches Digitalprojekt

### [Dorfflohmarkt Urbar 2026](https://github.com/mpusceddu/dorfflohmarkt-urbar)

Interaktive, mobil nutzbare Karte für die teilnehmenden Stände des Dorfflohmarkts. Das Projekt verbindet konkrete Bürgerinformation mit einer schlanken technischen Umsetzung auf Basis von JavaScript, Leaflet, OpenStreetMap und GitHub Pages.

[**Interaktive Karte öffnen**](https://mpusceddu.github.io/dorfflohmarkt-urbar/)

## Technische Umsetzung

- statische Website ohne komplexes Framework
- semantisches HTML5
- eigenes responsives CSS
- lokale Schriftdateien mit beiliegenden Lizenztexten
- mobile Navigation mit sichtbaren, bei Bedarf umbrechenden Links ohne JavaScript
- optimierte Darstellung für Smartphones und Desktop-Rechner
- Skip-Link und beschriftete Navigation für bessere Zugänglichkeit
- Open-Graph- und Social-Media-Metadaten
- MP-Favicon als SVG, PNG und ICO sowie eigenes Apple-Touch-Icon
- eigene Fehlerseite
- Veröffentlichung über GitHub Pages mit eigener Domain

## Projektstruktur

```text
.
├── index.html          # Startseite
├── impressum.html      # Impressum
├── datenschutz.html    # Datenschutzerklärung
├── 404.html            # Fehlerseite
├── aktuelles/
│   ├── index.html      # Beitragsarchiv
│   └── *.html          # Einzelne Beiträge
├── assets/
│   ├── css/            # Gestaltung
│   ├── fonts/          # Lokale Schriften und Lizenzen
│   ├── js/             # Optionaler Themenfilter im Archiv
│   └── images/         # Bildmaterial
├── CNAME               # eigene Domain für GitHub Pages
├── robots.txt
└── sitemap.xml
```

## Lokal ansehen

Die Website bleibt statisch und kann direkt angesehen werden. Der optionale Pflegeschritt für Artikelübersichten benötigt nur Python 3 ab Version 3.9, keine zusätzlichen Pakete. Im Projektordner genügt für die Vorschau:

```bash
python3 -m http.server 8000
```

Danach im Browser öffnen:

```text
http://localhost:8000
```

## Grundsatz

Die Seite ist bewusst schlank gehalten: kurze Ladewege, klare Inhalte und keine unnötige technische Komplexität.

Das kanonische runde Porträt für persönliche Kacheln und Profil-Icons liegt unter `assets/images/avatar-marco-rund.jpg`. Für solche Einsätze dieses Bild verwenden und keine abweichenden Porträtausschnitte anlegen. Funktionale Symbole wie E-Mail oder soziale Netzwerke bleiben davon unberührt, sofern kein persönlicher Absender dargestellt wird.

## Schrift und Startseitenporträt

Die Website verwendet die lokal gespeicherte Source Sans 3 für Fließtext und Überschriften. Moderate Schriftgewichte und offene Zeilenabstände halten die Darstellung ruhig. Das Startseitenporträt `assets/images/marco-pusceddu-portrait-ki-v2.jpg` zeigt Marco im dunkelblauen Poloshirt. Das KI-bearbeitete Porträt wurde von Marco am 01.10.2026 als Bildfassung bestätigt; Hintergrund und Pose sind generativ bearbeitet. Die Bilddatei hat 1122 × 1402 Pixel und wird im Alternativtext als KI-bearbeitet bezeichnet. Auf schmalen Ansichten bleibt das Bild im Hochformat, damit Gesicht und verschränkte Arme sichtbar sind. Das runde Profilbild und vorhandene Social-Media-Vorschaubilder bleiben eigenständige Motive.

## Änderungen prüfen

- Die vorhandenen Artikeladressen und Quellen beibehalten. Rechtliche Texte gesondert prüfen.
- Bei CSS-Änderungen den Versionsparameter an allen HTML-Seiten gemeinsam aktualisieren; derzeit 20 Seiten, aktuell `styles.css?v=24`.
- Startseite, Beitragsarchiv, einen langen Artikel und den Bildartikel auf Smartphone, Tablet und Desktop prüfen. Zusätzlich schmale Ansichten, die Umbrüche bei 900 und 1100 Pixeln sowie Textvergrößerung berücksichtigen.
- Navigation, Tastaturfokus, Sprungmarken, Bilder und interne Links kontrollieren. Der mobile Kopfbereich scrollt mit der Seite, damit mehrzeilige Navigation keine Inhalte verdeckt.
- Die Fehlerseite lokal unter `/404.html` prüfen. Der einfache lokale Python-Server ersetzt nicht den GitHub-Pages-Test einer tatsächlich fehlenden Unterseite.
- Nach der Veröffentlichung auch eine verschachtelte, nicht vorhandene Adresse auf der echten Domain aufrufen: Gestaltung und Link zur Startseite müssen funktionieren.
- Den erfolgreichen Pages-Lauf und anschließend den veröffentlichten Stand auf der eigenen Domain kontrollieren. Offene Browserprüfungen ausdrücklich als offen festhalten.

## Beiträge auf der Startseite pflegen

- Artikel ausschließlich in ihrer bestehenden Datei unter `aktuelles/*.html` pflegen. Entwürfe außerhalb der veröffentlichten Website aufbewahren: GitHub Pages liefert jede HTML-Datei im Repository aus, auch wenn sie nicht verlinkt ist.
- Nach einer freigegebenen Änderung `python3 scripts/build_articles.py` ausführen. Das Skript erzeugt die markierten Bereiche in Startseite und Archiv sowie die Artikeladressen der Sitemap. Die erzeugten Dateien gemeinsam mit dem Artikel committen. GitHub Pages veröffentlicht weiterhin die eingecheckten statischen Dateien; es gibt keinen Hintergrundprozess mit Schreibzugriff.
- Quelle sind der sichtbare Artikelkopf (Titel, Datum, Rubrik), `og:description` als Kurztext, Canonical-Adresse und Artikelmetadaten. Optional überschreibt `<meta name="article:summary" content="Kurzer Überblick">` den Kurztext für die Übersichten. Das Skript ändert keine Artikeltexte oder rechtlichen Seiten.
- Den neuesten aktuellen Beitrag zeigt das Skript hervorgehoben. Unter „Weitere Beiträge“ erscheinen die sechs nächsten vorhandenen Beiträge in absteigender Reihenfolge des Veröffentlichungsdatums, ohne Dopplung. Aktualisierungen ändern diese Reihenfolge nicht. Bei gleichem Datum entscheidet der Dateiname.
- Hintergrundbeiträge erhalten `<meta name="article:listing" content="background">`. Sie erscheinen nach den aktuellen Beiträgen, innerhalb beider Gruppen nach Veröffentlichungsdatum absteigend. Ohne dieses Feld gilt `current`. Das tatsächliche Veröffentlichungsdatum bleibt erhalten; die sichtbare Rubrik kennzeichnet den Hintergrundcharakter. So verdrängt ein neuer Hintergrundtext keine aktuelle Meldung. Diese Reihenfolge gilt auch im Urbar-Bereich.
- Bestehende Adressen und Veröffentlichungsdaten beibehalten. Eine wesentliche Aktualisierung mit `article:modified_time` und sichtbarem Änderungsdatum kennzeichnen. Historische Sitemap-Änderungsdaten bleiben erhalten; das Datum eines erneuten Builds wird nicht als inhaltliche Änderung ausgegeben.
- Vor dem Veröffentlichen `python3 scripts/build_articles.py --check` und `python3 -m unittest discover -s tests` ausführen. Fehlende Metadaten, falsche Canonical-Adressen, abweichende Titel/Datumswerte und zukünftige Veröffentlichungsdaten brechen die Erzeugung ab, bevor Ausgabedateien geändert werden.
- Das Raster zeigt über 1100 Pixeln drei, zwischen 561 und 1100 Pixeln zwei und bis 560 Pixel eine Spalte. Mit sechs Einträgen bleiben die letzten Reihen vollständig.

## Themenfilter unter Aktuelles

Das Archiv bietet „Alle“, „Politik & Finanzen“, „Bauen & Umwelt“, „Erneuerbare Energien“, „Digitalisierung“, „Ehrenamt“ und „Persönlich“. Ein Artikel kann zu mehreren Themen gehören; Orte und sichtbare Rubriken bleiben davon unabhängig. Die Zuordnung erfolgt im Artikelkopf über beispielsweise `<meta name="article:topics" content="politik-finanzen, digitalisierung">`.

Erlaubte Kennungen sind `politik-finanzen`, `bauen-umwelt`, `erneuerbare-energien`, `digitalisierung`, `ehrenamt` und `persoenlich`. Jeder Artikel benötigt mindestens eine gültige Kennung. Der bestehende Artikelgenerator prüft sie und erzeugt Filter, Beitragszahlen und Kartenzuordnungen gemeinsam. Themen ohne Artikel werden nicht angezeigt. Neue Themen in `TOPICS` in `scripts/build_articles.py` ergänzen, erst wenn passende veröffentlichte Beiträge vorliegen.

Das kleine lokale Skript `assets/js/article-filter.js` blendet passende Karten direkt ein. Die Auswahl lässt sich als Link weitergeben, etwa `/aktuelles/#thema=digitalisierung`, und bleibt beim Zurückgehen erhalten. Ein unbekanntes Thema zeigt alle Beiträge. Ohne JavaScript oder bei einem nicht geladenen Skript bleiben alle Artikel sichtbar und die Bedienelemente verborgen. Keine Cookies, kein Speicherzugriff, keine externen Abhängigkeiten.

Die Gestaltung liegt ausschließlich in `assets/css/article-filter.css`. Bei Änderungen an Filter-CSS oder -JavaScript den jeweiligen Versionsparameter in `aktuelles/index.html` erhöhen. Tastaturbedienung, Fokus, Beitragszahl, Zurück/Weiter, direkte Themenlinks und die Ansicht ohne JavaScript auf schmalen und breiten Bildschirmen mitprüfen.

## Favicon und Lesezeichen

Das Favicon verwendet eine für kleine Größen angepasste Fassung des vorhandenen MP-Zeichens: cremeweißes M und helltürkises P auf Dunkelblau. `favicon.svg` ist die skalierbare Hauptfassung mit expliziten Abmessungen. `favicon-32x32.png` und `favicon-96x96.png` sind die Rasterfassungen, `favicon.ico` enthält 16, 32 und 48 Pixel. `apple-touch-icon.png` hat 180 × 180 Pixel und einen deckenden Hintergrund; die Rundung übernimmt das Gerät. `safari-pinned-tab.svg` stellt für angeheftete Safari-Tabs das MP-Zeichen als schwarze Vektormaske auf transparentem Grund bereit; Safari übernimmt die Einfärbung.

Alle 20 HTML-Seiten binden diese Dateien mit Pfaden ab der Domainwurzel ein. Das gilt auch für verschachtelte Artikel und die Fehlerseite. Bei Änderungen alle Fassungen gemeinsam ersetzen, in kleinen Größen vor hellem und dunklem Hintergrund prüfen und die Einbindung in neuen Artikeln übernehmen. Die Favicon-Adressen stabil halten, damit Suchmaschinen sie zuverlässig abrufen können. Aktuell gilt einmalig `?v=2`, damit Browser die anfänglichen, fehlenden oder veralteten Symbole erneut abrufen. Diesen Wert nicht bei gewöhnlichen Artikeländerungen erhöhen.

## Persönlicher Urbar-Bereich

`urbar/index.html` bündelt persönliche Beiträge und die Arbeit im Ortsgemeinderat. Der Bereich ist von der Startseite und der Hauptnavigation erreichbar. Das Layout ergänzt die vorhandene Gestaltung über `assets/css/urbar.css`; rechtliche Texte bleiben unverändert. Der gemeinsame Footer kann auf schmalen Geräten umbrechen.

Seit dem 03.10.2026 sind auf Marcos Wunsch die Karten „Dorfflohmarkt Urbar“ und „Vereinsleben an einem Ort“ vorerst ausgeblendet. Der zugehörige Abschnitt „Digitale Projekte“ und sein Sprunglink sind vollständig aus dem ausgelieferten HTML entfernt. Der bisherige Inhalt bleibt in der Git-Historie erhalten und darf erst nach einem neuen Auftrag wieder eingebaut werden. Die eigenständigen Projektwebsites sind davon unberührt.

Ein veröffentlichter Artikel erscheint automatisch auch dort, wenn sein Kopf `<meta name="article:places" content="urbar">` enthält. Mehrere Orte können durch Kommas getrennt werden. Die Zuordnung erfolgt bewusst durch die Redaktion, nicht über eine Stichwortsuche im Text. Anschließend denselben Pflegeschritt `python3 scripts/build_articles.py` ausführen und alle erzeugten Änderungen gemeinsam committen. Auf der Urbar-Seite erscheinen alle zugeordneten Beiträge: aktuelle Beiträge zuerst, danach Hintergrundbeiträge; innerhalb beider Gruppen neueste zuerst; die Artikel selbst bleiben unter ihrer bisherigen Adresse.

Projektangaben vor Änderungen auf den verlinkten Projektseiten prüfen. Aktueller Stand am 29.09.2026: Dorfflohmarkt mit Ausblick auf 2027 ohne veröffentlichten Termin; Vereinsring als öffentliche Vorschau. Die Domain `unser-urbar-für-alle.de` ist als zusätzliche Adresse vorgesehen, die auf `https://marcopusceddu.de/urbar/` weiterleitet. Canonical-Adresse bleibt die persönliche Hauptdomain.

## Verweise zur CDU-Seite

Die persönlichen Einblicke bleiben auf marcopusceddu.de. Im Engagementbereich führen Links zur CDU-Fraktion in Urbar, zur Fraktion im Verbandsgemeinderat sowie zur Übersicht der Themen und Anträge. Der Beitrag zur kommunalpolitischen Verantwortung verlinkt den Gemeindeverband mit der Teamseite.

Die neue CDU-Seite liegt derzeit unter der öffentlichen Entwicklungsadresse `https://mpusceddu.github.io/cdu-vallendar/`. Wenn die endgültige Domain eingerichtet ist, die vier Verweise gemeinsam ersetzen und die Sprungmarken `#team` und `#fraktion` erneut prüfen.

## Kontakt

- Website: [marcopusceddu.de](https://marcopusceddu.de/)
- GitHub: [github.com/mpusceddu](https://github.com/mpusceddu)
- E-Mail: [marco.pusceddu@cdu-urbar.de](mailto:marco.pusceddu@cdu-urbar.de)
- Instagram: [@mapusceddu](https://www.instagram.com/mapusceddu/)

## Beitragsbild zur Haushaltsdisziplin

`assets/images/freiwillige-leistungen-haushaltsdisziplin.jpg` ist eine eigene typografische Beitragsgrafik mit dem vorhandenen MP-Zeichen und Source Sans 3 in Dunkelblau und Türkis. Die Aussage stammt aus dem Artikel. Die Datei ist 1200 × 630 Pixel groß und dient zugleich als Artikelbild und Open-Graph-/Twitter-Vorschau. Sie wird lokal ohne Drittanbieter geladen und enthält keine Darstellung einer tatsächlichen Sitzung.
