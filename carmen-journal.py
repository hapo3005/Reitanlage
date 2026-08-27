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

# This script runs after the global final desktop/mobile layers in the deploy
# workflow. Append the dedicated Hofjournal authority here so no older generic
# rule can re-introduce the oversized headings, stray rules or dead space.
css_path = Path('_site/site.css')
journal_css_path = Path('journal-10of10-20260827.css')
marker = '/* ===== journal-10of10-20260827.css ===== */'
css = css_path.read_text(encoding='utf-8')
assert marker not in css
css += '\n\n' + marker + '\n' + journal_css_path.read_text(encoding='utf-8').rstrip() + '\n'
css_path.write_text(css, encoding='utf-8')

final_css = css_path.read_text(encoding='utf-8')
assert final_css.count(marker) == 1
assert final_css.rfind(marker) > final_css.rfind('/* ===== final-10of10-20260827.css ===== */')
assert '.journal-page .journal-photoessay .journal-section-head h2' in final_css
assert 'grid-template-columns:repeat(12,minmax(0,1fr))!important' in final_css

print('Verified canonical Carmen voice and loaded final Hofjournal 10/10 system.')
