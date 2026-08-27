from pathlib import Path

# Reuse the reviewed homepage copy map without executing the journal pass in
# carmen-voice.py. This keeps the homepage transformation strict and fails the
# build if its source copy changes unexpectedly.
source = Path('carmen-voice.py').read_text(encoding='utf-8')
prefix = source.split('\njournal_replacements =', 1)[0]
namespace = {}
exec(prefix, namespace)
namespace['replace_many'](Path('_site/index.html'), namespace['index_replacements'])

index = Path('_site/index.html').read_text(encoding='utf-8')
assert 'Was Carmen im Unterricht' not in index
assert 'Schreiben Sie Carmen gern' not in index
assert 'Reiten beginnt für mich mit <em>Vertrauen.</em>' in index
assert 'Was mir beim Reiten <em>wichtig ist.</em>' in index
assert 'melden Sie sich <em>gern bei mir.</em>' in index
print('Applied strict Carmen voice editorial pass to homepage.')
