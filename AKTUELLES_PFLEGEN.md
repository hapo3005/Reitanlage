# Aktuelles pflegen

Die Meldungen auf der Startseite kommen weiterhin aus `aktuelles.json`. Für normale Änderungen müssen weder HTML noch CSS noch JavaScript angefasst werden.

## Empfohlener Weg: Aktuelles-Editor

Im Ordner `tools` liegt die Datei `aktuelles-editor.html`.

1. `tools/aktuelles-editor.html` herunterladen und im Browser öffnen.
2. `aktuelles.json` über **JSON-Datei öffnen** laden.
3. Texte, Bildpfade, Reihenfolge und CTA-Texte bequem im Formular ändern.
4. Das Aktualisierungsdatum setzen.
5. **aktuelles.json herunterladen** wählen.
6. Die vorhandene `aktuelles.json` im Repository durch die erzeugte Datei ersetzen und committen.

Der normale Deploy optimiert die Bilder automatisch und veröffentlicht die neue Fassung. Im Editor müssen deshalb weiterhin nur die normalen Quelldateien im Ordner `images` angegeben werden, zum Beispiel `images/ferienkurs.png`.

## Wichtig für die Reihenfolge

Die oberste Meldung in `items` wird als große Hauptmeldung dargestellt. Alle weiteren Meldungen erscheinen als Nebenmeldungen. Im Editor lässt sich die Reihenfolge mit **Nach oben** und **Nach unten** ändern.

## Bilder

Neue Bilder zuerst in den Ordner `images` hochladen. Danach den exakten Dateinamen im Editor eintragen.

- Fotos: `imageFit` auf `cover`
- Flyer oder Motive, die vollständig sichtbar bleiben sollen: `imageFit` auf `contain`
- Für Flyer kann `imageZoom` aktiviert werden
- `imagePosition` und `imagePositionMobile` steuern den Bildausschnitt, zum Beispiel `50% 35%`

Die Produktionspipeline erstellt daraus automatisch optimierte WebP-Dateien. Die erzeugten WebP-Namen gehören nicht in die gepflegte `aktuelles.json`.

## Direkte Bearbeitung von JSON

Falls der Editor nicht genutzt werden soll, kann `aktuelles.json` weiterhin direkt in GitHub bearbeitet werden. Die wichtigsten Felder sind:

- `category`: Rubrik
- `meta`: kurze Zusatzinfo
- `title`: Überschrift
- `text`: Meldungstext
- `image`: Quelldatei aus `images`
- `alt`: Bildbeschreibung
- `link`: Ziel, meist `#kontakt`
- `linkText`: sichtbarer CTA-Text
- `imageFit`: `cover` oder `contain`
- `imageZoom`: `true` oder `false`

Die Datei muss gültiges JSON bleiben. Der Deploy bricht bei technischen Fehlern ab, bevor eine fehlerhafte Produktionsseite veröffentlicht wird.
