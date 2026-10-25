# Strom im Blick und die Energiereihe

Aktueller Aufbau nach der Vereinfachung vom 25.10.2026:

- `/energie/strom-im-blick/`: aktuelle Daten zu Erzeugung, Erneuerbaren-Anteil, Börsenpreis und physischem Stromaustausch. Keine Simulation und keine historischen Haushaltskosten auf der Datenansicht.
- `/energie/merit-order/`: eigenständige Erklärung „Warum ist Strom teuer, obwohl Wind und Sonne liefern?“ mit frei veränderbarem Beispiel. Keine automatische Übernahme von Messwerten. Das tatsächlich preissetzende Gebot/Kraftwerk lässt sich aus den vorhandenen Erzeugungsdaten nicht bestimmen.
- `/energie/was-steckt-im-strompreis.html`: Hintergrundbeitrag zur Stromrechnung. Amtlicher Vergleich zum 01.04.2025 (Monitoringbericht Energie 2025, Tabelle 38, gedruckte Seite 169), keine aktuellen Tarifwerte.

Import und Export stehen im Dashboard vor der Erzeugungsansicht. Sichtbar sind Import, Export, Saldo, Zeitverlauf, erfasste Strommengen im ausgewählten Zeitraum sowie Richtung und Leistung nach Land/Verbindung. Quellwerte sind in GW; positive Werte bedeuten Import nach Deutschland, negative Export. Die Summe enthält die Länderreihen, nicht die zusätzliche API-Summenreihe. Mengen ergeben sich ausschließlich aus vollständigen Viertelstunden mit vollständigen Werten (GW × 0,25 h = GWh); fehlende Zeiträume werden nicht überbrückt. Physische Flüsse sind keine Handelsgeschäfte und belegen für sich keinen Versorgungsmangel.

Die Datenaktualisierung bleibt unverändert: drei gemeinsame API-Abrufe etwa alle 30 Minuten, validierter Cache des letzten gültigen Standes, atomare Speicherung, Retry-After-Beachtung und sichtbare Verzögerungs-/Fehlerhinweise. Besucher lesen den gemeinsamen Datensatz nach, ohne die Fraunhofer-API selbst anzufragen.

Die späteren geplanten Folgen zur Strompreisbildung und zum europäischen Stromhandel bleiben an ihren bestätigten Veröffentlichungsterminen. Der Haushaltskosten-Beitrag wird mit dem tatsächlichen Publikationsdatum 25.10.2026 als Hintergrund geführt. Historische Testkopien rekonstruieren dafür auch den damaligen Bestand der Energieartikel; die Produktionssperre gegen zukünftige Artikel bleibt erhalten.

Prüfung: 37 Python- und 11 JavaScript-Tests bestanden. Enthalten sind Veröffentlichungssperren, Preislücken/Zeitumstellung, getrennte Import-/Exportmengen, Datenlücken und Modellberechnung. Drei Seiten visuell auf Desktop und bei 390 px geprüft.
