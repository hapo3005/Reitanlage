from pathlib import Path

path = Path('_site/index.html')
html = path.read_text(encoding='utf-8')

replacements = [
    (
        '<p class="kicker">Carmen Eichhorn-Nels · Reitanlage bei Wittlich</p>',
        '<p class="kicker">Reitanlage Eichhorn-Nels · Minderlittgen</p>'
    ),
    (
        '<h1>Reiten beginnt für mich mit <em>Vertrauen.</em></h1><p class="hero-intro">Schön, dass Sie da sind. Auf meiner Reitanlage in Minderlittgen begleite ich Kinder, Jugendliche und Erwachsene – vom ersten Reiten über den Wiedereinstieg bis zur Turniervorbereitung. Sie können mit einem meiner Lehrpferde oder mit dem eigenen Pferd zu mir kommen. Auch Beritt und Pferdepension gehören zu meinem Angebot.</p>',
        '<h1>Reiten beginnt für mich mit <em>Vertrauen.</em></h1><p class="hero-signature" aria-label="Carmen Eichhorn-Nels"><span aria-hidden="true"></span>Carmen Eichhorn-Nels</p><p class="hero-intro">Auf meiner Reitanlage in Minderlittgen begleite ich Kinder, Jugendliche und Erwachsene – vom ersten Reiten bis zur Turniervorbereitung. Unterricht ist mit einem meiner Lehrpferde oder mit dem eigenen Pferd möglich. Auch Beritt und Pferdepension gehören dazu.</p>'
    ),
    (
        '<p class="credential">Carmen Eichhorn-Nels · Trainer C Leistungssport · Dressur bis M · Springen bis L</p>',
        '<p class="credential">Trainer C Leistungssport · Dressur bis M · Springen bis L</p>'
    ),
]

missing = []
for old, new in replacements:
    if old not in html:
        missing.append(old[:120])
    else:
        html = html.replace(old, new, 1)

if missing:
    raise RuntimeError('Hero source changed unexpectedly:\n- ' + '\n- '.join(missing))

assert html.count('class="hero-signature"') == 1
assert 'Schön, dass Sie da sind.' not in html
assert 'Reitanlage Eichhorn-Nels · Minderlittgen' in html
path.write_text(html, encoding='utf-8')
print('Applied Carmen editorial signature and concise hero copy.')
