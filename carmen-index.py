from pathlib import Path

# Reuse the reviewed homepage copy map without executing the journal pass in
# carmen-voice.py. This keeps the homepage transformation strict and fails the
# build if its source copy changes unexpectedly.
source = Path('carmen-voice.py').read_text(encoding='utf-8')
prefix = source.split('\njournal_replacements =', 1)[0]
namespace = {}
exec(prefix, namespace)
namespace['replace_many'](Path('_site/index.html'), namespace['index_replacements'])

# The first-person voice is established above; now make Carmen visibly the
# author of the hero and trim the opening copy without touching later sections.
exec(Path('hero-personality.py').read_text(encoding='utf-8'), {})

# One final homepage presentation layer is appended after every historical CSS
# layer. Desktop contact fixes are scoped to min-width:821px; mobile remains
# governed by the already-reviewed mobile composition files.
css_path = Path('_site/site.css')
css_marker = '/* ===== homepage-final-20260827.css ===== */'
css = css_path.read_text(encoding='utf-8')
assert css_marker not in css
css += '\n\n' + css_marker + '\n' + Path('homepage-final-20260827.css').read_text(encoding='utf-8').rstrip() + '\n'

# Consolidated large-desktop geometry pass. This is intentionally appended
# after the homepage layer so legacy section rules cannot reintroduce the
# spacing/grid defects caught during the final visual audit.
desktop_marker = '/* ===== desktop-composition-final-20260827.css ===== */'
assert desktop_marker not in css
css += '\n\n' + desktop_marker + '\n' + Path('desktop-composition-final-20260827.css').read_text(encoding='utf-8').rstrip() + '\n'
css_path.write_text(css, encoding='utf-8')

# The legacy observer can leave the previous chapter active near the bottom of
# the page. A deterministic final pass keeps Contact active when Contact is the
# visible closing chapter.
js_path = Path('_site/site.js')
js_marker = '/* ===== homepage-final-20260827.js ===== */'
js = js_path.read_text(encoding='utf-8')
assert js_marker not in js
js += '\n\n' + js_marker + '\n' + Path('homepage-final-20260827.js').read_text(encoding='utf-8').rstrip() + '\n'
js_path.write_text(js, encoding='utf-8')

index = Path('_site/index.html').read_text(encoding='utf-8')
final_css = css_path.read_text(encoding='utf-8')
final_js = js_path.read_text(encoding='utf-8')
assert 'Was Carmen im Unterricht' not in index
assert 'Schreiben Sie Carmen gern' not in index
assert 'Reiten beginnt für mich mit <em>Vertrauen.</em>' in index
assert 'Was mir beim Reiten <em>wichtig ist.</em>' in index
assert 'melden Sie sich <em>gern bei mir.</em>' in index
assert index.count('class="hero-signature"') == 1
assert 'Schön, dass Sie da sind.' not in index
assert css_marker in final_css
assert desktop_marker in final_css
assert js_marker in final_js
assert ('height:560px!important' in final_css) or ('desktop-contact-v3' in final_css)
assert 'grid-template-columns:176px minmax(0,1fr)!important' in final_css
assert 'height:auto!important' in final_css
assert 'document.documentElement.scrollHeight-4' in final_js
print('Applied strict Carmen voice, hero personality and final homepage/desktop composition passes.')
