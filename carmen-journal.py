from pathlib import Path

path = Path('_site/aktuelles.html')
text = path.read_text(encoding='utf-8')

required = (
    'Was bei uns auf dem Hof <em>passiert.</em>',
    'Hier nehme ich Sie ein bisschen ausführlicher mit in unseren Hofalltag',
    'Einblicke in unseren <em>Alltag.</em>',
    'Ein paar Rückblicke aus den <em>vergangenen Jahren.</em>',
    'Je nach Vereinbarung begleite ich Schüler, Einsteller und Privatreiter',
    'Termine und Verfügbarkeiten stimmen wir am besten direkt <em>ab.</em>',
)
for phrase in required:
    assert phrase in text, phrase

forbidden = (
    'Momente, die man nicht in eine <em>Preisliste</em> bekommt.',
    'Was bereits <em>passiert ist.</em>',
    'Carmen begleitet Schüler, Einsteller und Privatreiter',
    'Termine und Verfügbarkeiten am besten direkt <em>abstimmen.</em>',
)
for phrase in forbidden:
    assert phrase not in text, phrase

print('Verified canonical Carmen voice copy for Hofjournal.')
