# Strom im Blick

Stand: 25.10.2026. Separate Arbeitskopie auf feature/strom-im-blick, Basis e0ed41f. Lokale Vorschau: http://127.0.0.1:8875/energie/strom-im-blick/. Veröffentlichung am 25.10.2026 ausdrücklich beauftragt.

## Inhalt und Gestaltung

Vier Diagramme mit Originaldaten von Fraunhofer ISE Energy-Charts: öffentliche Nettostromerzeugung, Erneuerbaren-Anteil an dieser Erzeugung, Day-Ahead-Börsenpreise DE-LU, physische Grenzflüsse. Heute, sieben Kalendertage und morgen (nur Preise). Die Kennzahlen beziehen sich explizit auf heute. Tabellen als zugängliche Alternative zu den Diagrammen.

Das Dropdown hat einen eigenen Pfeil mit 17 px rechtem Abstand und ausreichend Textpolster. Auswahl und Beschriftung haben getrennte Elemente. Smartphoneansicht bei 320 px visuell geprüft; 390/768/1440 px ohne horizontalen Überlauf. Kein physisches Mobilgerät getestet. Prozentachse beginnt bei 0 und reicht mindestens bis 100.

## Datenaktualisierung

`python3 scripts/update_energy_data.py` lädt drei Endpunkte einmal zentral. Der Preisabruf umfasst auch morgen. Validierung prüft Einheiten, Preis-Lizenz, eindeutige Zeitstempel und Datenlängen. Ältere oder ungültige Antworten überschreiben keine gültigen Daten. Fehler einzelner Endpunkte behalten deren letzten gültigen Stand. Retry-After bei HTTP 429 wird laufübergreifend berücksichtigt. Atomare Dateiersetzung verhindert unvollständige JSON-Antworten.

`python3 scripts/serve_energy_preview.py --directory /tmp/strom-im-blick-preview --port 8875` betreibt die lokale Vorschau. Nach 30 Minuten löst ein Zugriff auf den gemeinsamen Datensatz einen Aktualisierungsversuch im Hintergrund aus. Die geöffnete Seite lädt den eigenen Datensatz alle fünf Minuten nach. Ein echter serverseitig ausgelöster Abruf wurde erfolgreich geprüft. Es erfolgen keine direkten API-Anfragen aus den Browsern der Besucher.

Für späteren öffentlichen Betrieb ist `.github/workflows/energy-dashboard.yml` vorbereitet: alle 30 Minuten gemeinsamer Abruf, Cache des letzten gültigen Standes, Tests und Veröffentlichung über den bestehenden Build. Die vorhandene Veröffentlichungsroutine verwendet denselben Cache. Beide Abläufe teilen die bestehende GitHub-Pages-Sperre. Die neue Routine ist nicht aktiv, solange die Änderungen nicht in main veröffentlicht wurden. GitHub kann geplante Ausführungen verzögern; Datenstand und Störungen stehen sichtbar auf der Seite.

Zeitraumfilter verwenden deutsche Kalendertage, auch bei 23/25-Stunden-Tagen. Preisintervalle gelten für 15 Minuten; eine Datenlücke verlängert niemals den davorliegenden Preis. Erzeugung und physische Flüsse bleiben beim aktuellen Abruf deutlich verzögert; die Oberfläche weist darauf hin.

## Prüfung

37 Python-Tests und vier JavaScript-Tests bestanden. Geprüft sind insbesondere Ausfälle, fehlerhafte Einheiten/Lizenzen, Datenregression, Ratenbegrenzung, fehlende Werte, Zeitumstellung und Preislücken. Bestehende Veröffentlichungssperren für terminierte Beiträge bleiben durch den vorhandenen Build erhalten. Abschließende Browserprüfung ohne JavaScript-Fehler.

## Veröffentlichung

Produktionsfassung: Vorschaukennzeichnung/noindex entfernt, /links/ und Sitemap ergänzt. Zentrale Abrufe und Browser-Nachladen aktivieren sich mit Veröffentlichung auf main. Vorhandene terminierte Artikel nicht vorzeitig freigeben. Bestehende Redaktionsautomationen bleiben unverändert.

## Erweiterung: Erzeugungsmix, Merit Order und Stromrechnung

Die Anteile der einzelnen Erzeugungsgruppen entstehen aus der Integration vollständiger, verfügbarer Viertelstunden (GW × 0,25 h = GWh). Fehlende Intervalle werden weder zu null noch zu längeren Intervallen erweitert. Die getrennte Energy-Charts-Reihe zum Erneuerbaren-Anteil bleibt erhalten.

Das interaktive Merit-Order-Modell verwendet ausdrücklich frei gewählte Gebote (0/6/12/20 ct/kWh) und Mengen. Nachfrage und günstiges Angebot sind veränderbar. Das Modell behauptet keine aktuellen Kraftwerkskosten und identifiziert kein reales preissetzendes Kraftwerk. Grundlage: SMARD, Großhandelspreise und So funktioniert der Strommarkt.

Haushaltskosten: Monitoringbericht Energie 2025, Tabelle 38, gedruckte Seite 169/PDF-Seite 170, Preisstand 01.04.2025. Amtlicher Gesamtwert 40,05 ct/kWh; Beschaffung 11,39, Vertrieb/Marge 4,45, Nettonetz 11,02, Messstellenbetrieb 0,48, Konzession 1,60, KWKG 0,28, besondere Netznutzung 1,56, Offshore 0,82, Stromsteuer 2,05, Umsatzsteuer 6,39. Summe gerundeter Einzelwerte 40,04; Rundungsdifferenz 0,01 ausdrücklich erklärt. Keine Addition des heutigen Börsenpreises mit diesen historischen Komponenten. Quellenprüfung im Original-PDF und visuell an der vollständigen Tabelle.

Systemkosten werden knapp und ohne weitere fiktive ct/kWh-Aufschläge eingeordnet: Netzausbau und Redispatch über Netzkosten, EEG-Finanzierung seit 2023 im Bundeshaushalt. Quellen stehen an den Abschnitten.

37 Python- und neun JavaScript-Tests bestanden. Neue Tests prüfen Integration und Datenlücken, Merit-Order-Grenzfälle, Angebotsreihenfolge, Angebotsmangel und negative Gebote. Modell im Browser mit niedriger/hoher Nachfrage getestet; 320-px-Ansicht und Kostenblock bei 390 px visuell geprüft.
