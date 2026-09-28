# marcopusceddu.de

[![Website](https://img.shields.io/badge/Website-marcopusceddu.de-173f34?style=flat-square)](https://marcopusceddu.de/)

Persönliche Website von **Marco Pusceddu**: Familienmensch, Unternehmer und Kommunalpolitiker aus Urbar.

[![Vorschau der Website](assets/images/og.jpg)](https://marcopusceddu.de/)

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
│   └── images/         # Bildmaterial
├── CNAME               # eigene Domain für GitHub Pages
├── robots.txt
└── sitemap.xml
```

## Lokal ansehen

Das Projekt benötigt keinen Build-Prozess. Im Projektordner genügt beispielsweise:

```bash
python3 -m http.server 8000
```

Danach im Browser öffnen:

```text
http://localhost:8000
```

## Grundsatz

Die Seite ist bewusst schlank gehalten: kurze Ladewege, klare Inhalte und keine unnötige technische Komplexität.

## Änderungen prüfen

- Die vorhandenen Artikeladressen und Quellen beibehalten. Rechtliche Texte gesondert prüfen.
- Bei CSS-Änderungen den Versionsparameter an allen HTML-Seiten gemeinsam aktualisieren; derzeit 17 Seiten, im Gestaltungsentwurf `styles.css?v=21-preview`.
- Startseite, Beitragsarchiv, einen langen Artikel und den Bildartikel auf Smartphone, Tablet und Desktop prüfen. Zusätzlich schmale Ansichten, die Umbrüche bei 900 und 1100 Pixeln sowie Textvergrößerung berücksichtigen.
- Navigation, Tastaturfokus, Sprungmarken, Bilder und interne Links kontrollieren. Der mobile Kopfbereich scrollt mit der Seite, damit mehrzeilige Navigation keine Inhalte verdeckt.
- Die Fehlerseite lokal unter `/404.html` prüfen. Der einfache lokale Python-Server ersetzt nicht den GitHub-Pages-Test einer tatsächlich fehlenden Unterseite.
- Nach der Veröffentlichung auch eine verschachtelte, nicht vorhandene Adresse auf der echten Domain aufrufen: Gestaltung und Link zur Startseite müssen funktionieren.
- Den erfolgreichen Pages-Lauf und anschließend den veröffentlichten Stand auf der eigenen Domain kontrollieren. Offene Browserprüfungen ausdrücklich als offen festhalten.

## Beiträge auf der Startseite pflegen

- Den neuesten Beitrag im hervorgehobenen Bereich zeigen.
- Unter „Weitere Beiträge“ die sechs nächsten vorhandenen Beiträge in absteigender Reihenfolge des Datums zeigen. Titel, Datum und Kurztext aus dem Beitragsarchiv übernehmen; den hervorgehobenen Beitrag nicht doppelt aufführen.
- Das Raster zeigt über 1100 Pixeln drei, zwischen 561 und 1100 Pixeln zwei und bis 560 Pixel eine Spalte. Mit sechs Einträgen bleiben die letzten Reihen vollständig.

## Verweise zur CDU-Seite

Die persönlichen Einblicke bleiben auf marcopusceddu.de. Im Engagementbereich führen Links zur CDU-Fraktion in Urbar, zur Fraktion im Verbandsgemeinderat sowie zur Übersicht der Themen und Anträge. Der Beitrag zur kommunalpolitischen Verantwortung verlinkt den Gemeindeverband mit der Teamseite.

Die neue CDU-Seite liegt derzeit unter der öffentlichen Entwicklungsadresse `https://mpusceddu.github.io/cdu-vallendar/`. Wenn die endgültige Domain eingerichtet ist, die vier Verweise gemeinsam ersetzen und die Sprungmarken `#team` und `#fraktion` erneut prüfen.

## Kontakt

- Website: [marcopusceddu.de](https://marcopusceddu.de/)
- GitHub: [github.com/mpusceddu](https://github.com/mpusceddu)
- E-Mail: [marco.pusceddu@cdu-urbar.de](mailto:marco.pusceddu@cdu-urbar.de)
- Instagram: [@mapusceddu](https://www.instagram.com/mapusceddu/)
