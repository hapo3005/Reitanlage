from pathlib import Path

# Reuse the reviewed homepage copy map without executing the journal pass in
# carmen-voice.py. This keeps the homepage transformation strict and fails the
# build if its source copy changes unexpectedly.
source = Path('carmen-voice.py').read_text(encoding='utf-8')
prefix = source.split('\njournal_replacements =', 1)[0]
namespace = {}
exec(prefix, namespace)
namespace['replace_many'](Path('_site/index.html'), namespace['index_replacements'])

# Keep the opening intentionally minimal: identity, message and actions only.
exec(Path('hero-personality.py').read_text(encoding='utf-8'), {})

css_path = Path('_site/site.css')
css = css_path.read_text(encoding='utf-8')

# Desktop homepage authority.
css_marker = '/* ===== homepage-final-20260827.css ===== */'
assert css_marker not in css
css += '\n\n' + css_marker + '\n' + Path('homepage-final-20260827.css').read_text(encoding='utf-8').rstrip() + '\n'

desktop_marker = '/* ===== desktop-composition-final-20260827.css ===== */'
assert desktop_marker not in css
css += '\n\n' + desktop_marker + '\n' + Path('desktop-composition-final-20260827.css').read_text(encoding='utf-8').rstrip() + '\n'

# Canonical mobile closing authority. It deliberately comes AFTER every
# homepage visual layer so pricing, contact, footer and the closing header state
# cannot be redefined by older CSS later in the cascade.
mobile_closing_marker = '/* ===== mobile-closing-final-20260828.css ===== */'
assert mobile_closing_marker not in css
css += '\n\n' + mobile_closing_marker + '\n' + Path('mobile-closing-final-20260828.css').read_text(encoding='utf-8').rstrip() + '\n'

# Minimal hero authority. Loaded last so older hero rules cannot restore copy
# or oversized secondary controls on small screens.
hero_reduction_marker = '/* ===== hero-reduction-final-20260828.css ===== */'
assert hero_reduction_marker not in css
css += '\n\n' + hero_reduction_marker + '\n' + Path('hero-reduction-final-20260828.css').read_text(encoding='utf-8').rstrip() + '\n'
css_path.write_text(css, encoding='utf-8')

# Deterministic contact-active state near the bottom of the page.
js_path = Path('_site/site.js')
js_marker = '/* ===== homepage-final-20260827.js ===== */'
js = js_path.read_text(encoding='utf-8')
assert js_marker not in js
js += '\n\n' + js_marker + '\n' + Path('homepage-final-20260827.js').read_text(encoding='utf-8').rstrip() + '\n'

# Mobile closing behavior is appended last for the homepage: once pricing is
# reached, the floating header leaves the viewport and no longer obscures the
# final price/contact composition.
mobile_closing_js_marker = '/* ===== mobile-closing-final-20260828.js ===== */'
assert mobile_closing_js_marker not in js
js += '\n\n' + mobile_closing_js_marker + '\n' + Path('mobile-closing-final-20260828.js').read_text(encoding='utf-8').rstrip() + '\n'
js_path.write_text(js, encoding='utf-8')

index = Path('_site/index.html').read_text(encoding='utf-8')
final_css = css_path.read_text(encoding='utf-8')
final_js = js_path.read_text(encoding='utf-8')
assert 'Was Carmen im Unterricht' not in index
assert 'Schreiben Sie Carmen gern' not in index
assert 'Reiten beginnt für mich mit <em>Vertrauen.</em>' in index
assert 'Was mir beim Reiten <em>wichtig ist.</em>' in index
assert 'melden Sie sich <em>gern bei mir.</em>' in index
assert 'class="hero-signature"' not in index
assert 'class="hero-intro"' not in index
assert 'class="credential"' not in index
assert 'Schön, dass Sie da sind.' not in index
assert 'Reitunterricht für Kinder, Jugendliche und Erwachsene – vom Einstieg bis zur Turniervorbereitung.' not in index
assert 'Trainer C Leistungssport · Dressur bis M · Springen bis L' not in index
assert css_marker in final_css
assert desktop_marker in final_css
assert mobile_closing_marker in final_css
assert hero_reduction_marker in final_css
assert final_css.rfind(mobile_closing_marker) > final_css.rfind(desktop_marker)
assert final_css.rfind(hero_reduction_marker) > final_css.rfind(mobile_closing_marker)
assert 'body:not(.journal-page) .hero-links>a:nth-child(2)' in final_css
assert js_marker in final_js
assert mobile_closing_js_marker in final_js
assert final_js.rfind(mobile_closing_js_marker) > final_js.rfind(js_marker)
assert 'body.closing-zone:not(.nav-open) .header' in final_css
assert 'body:not(.journal-page) .contact.contact-editorial::after' in final_css
assert "body.classList.toggle('closing-zone', closing)" in final_js
assert ('height:560px!important' in final_css) or ('desktop-contact-v3' in final_css)
assert 'grid-template-columns:176px minmax(0,1fr)!important' in final_css
assert 'height:auto!important' in final_css
assert 'document.documentElement.scrollHeight-4' in final_js
print('Applied strict Carmen voice, minimal hero and canonical desktop/mobile homepage composition passes.')