# Aktuelles pflegen

Die News auf der Startseite werden ausschließlich aus `aktuelles.json` geladen. Für eine normale Meldung müssen `index.html`, `style.css` und `script.js` nicht verändert werden.

## Bestehende Meldung ändern

1. `aktuelles.json` auf GitHub öffnen.
2. Auf **Edit** klicken.
3. Bei der gewünschten Meldung nur die Texte zwischen den Anführungszeichen ändern.
4. Das Feld `updated` oben auf das aktuelle Datum im Format `JJJJ-MM-TT` setzen.
5. Änderung speichern/committen. GitHub Pages veröffentlicht die neue Fassung automatisch.

## Felder einer Meldung

- `category`: kurze Rubrik, z. B. `Ferienkurse`
- `meta`: kurze Zusatzinfo, z. B. `Termine auf Anfrage`
- `title`: Überschrift
- `text`: kurzer Meldungstext
- `image`: Bild aus dem Ordner `images`, z. B. `images/flyerferienreitkurs.png`
- `alt`: kurze Bildbeschreibung
- `link`: Ziel des Links, für Kontakt meistens `#kontakt`
- `linkText`: sichtbarer Linktext

## Reihenfolge

Die erste Meldung in `items` wird auf der Website groß als Hauptmeldung gezeigt. Alle weiteren Meldungen erscheinen daneben bzw. darunter. Für eine neue Hauptmeldung den neuen Block daher ganz nach oben setzen.

## Neue Meldung als Vorlage

```json
{
  "category": "Kurse",
  "meta": "Neuer Termin",
  "title": "Titel der Meldung",
  "text": "Kurzer Text mit den wichtigsten Informationen.",
  "image": "images/dateiname.png",
  "alt": "Beschreibung des Bildes",
  "link": "#kontakt",
  "linkText": "Mehr erfahren"
}
```

Zwischen zwei Meldungsblöcken muss ein Komma stehen. Die letzte Meldung in der Liste hat danach kein Komma.

## Bilder

Neue Bilder zuerst in den Ordner `images` hochladen und anschließend den exakten Dateinamen im Feld `image` verwenden. Am besten funktionieren Querformate für die Hauptmeldung; andere Formate werden automatisch passend zugeschnitten.
