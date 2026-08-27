# Go-live – Reitanlage Eichhorn-Nels

Die Seite ist technisch so vorbereitet, dass der spätere Umzug von GitHub Pages auf eine eigene Domain kein Redesign und keine manuelle Suche nach alten URLs erfordert.

## Was der Build erzeugt

Der produktive Build läuft über:

```bash
python -m pip install "Pillow>=11,<13"
SITE_URL="https://www.beispiel-domain.de/" python build-release.py
```

Danach liegt die vollständige öffentliche Website im Ordner `_site`.

Nur `_site` wird veröffentlicht. Interne Dateien wie Prüflisten, Editor, Build-Skripte und alte Entwicklungsdateien gehören nicht auf den Webserver.

## Für eine eigene Domain

Sobald die endgültige Domain feststeht:

- Domain beim gewünschten Anbieter registrieren bzw. vorhandene Domain verwenden
- statisches Webhosting mit HTTPS aktivieren
- beim Build `SITE_URL` auf die endgültige HTTPS-Adresse setzen
- Inhalt von `_site` in das Webroot des Hostings laden
- DNS auf das Hosting zeigen lassen
- HTTPS-Zertifikat aktivieren
- Weiterleitung von `http` auf `https` und von der nicht bevorzugten `www`-/Non-`www`-Variante auf die Hauptadresse einrichten

Der Build passt dann automatisch an:

- Canonical URL
- Open-Graph-URL
- Social Preview
- strukturierte Daten
- Canonicals von Impressum und Datenschutz
- `robots.txt`
- `sitemap.xml`
- Links der 404-Seite

## Vor der endgültigen Kundenfreigabe

Noch einmal mit Carmen bestätigen:

- Schreibweise der Straße: `Dadscheid` oder `Datscheid`
- öffentliche E-Mail-Adresse
- gewünschter Facebook-Kanal

Danach müssen diese Angaben in einem Zug in Kontaktbereich, strukturierten Daten, Impressum und Datenschutz synchronisiert werden.

## Abnahme nach dem Domain-Umzug

Nach dem ersten Deploy auf die echte Domain prüfen:

- Startseite lädt per HTTPS
- `impressum.html` und `datenschutz.html` erreichbar
- WhatsApp, Telefon, E-Mail, Route und Facebook funktionieren
- `robots.txt` nennt die neue Sitemap
- `sitemap.xml` enthält ausschließlich die neue Domain
- Social Preview zeigt das 1200 × 630 Bild
- Canonical verweist auf die neue Domain
- keine alte GitHub-Pages-URL im ausgelieferten HTML
- mobile Navigation, Bild-Lightbox, Aktuelles und Preise funktionieren

## Suchmaschinen

Erst nach finalem Domain-Umzug und bestätigten Kontaktdaten sollte die neue Domain als dauerhafte Unternehmenswebsite aktiv beworben und in Suchmaschinen-/Unternehmensprofilen hinterlegt werden. Die GitHub-Pages-Version bleibt bis dahin Entwicklungs- und Abnahmeumgebung.
