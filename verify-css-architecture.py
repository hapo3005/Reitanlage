from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
CANONICAL = ROOT / 'styles' / 'site.css'
BUILT = ROOT / '_site' / 'site.css'
WORKFLOW = ROOT / '.github' / 'workflows' / 'deploy-current.yml'

MARKERS = (
    '/* ===== rebuild-base.css ===== */',
    '/* ===== architecture-v2.css — final production layer ===== */',
    '/* ===== journal.css ===== */',
    '/* ===== above-fold-direction.css ===== */',
    '/* ===== navigation-final-20260827.css ===== */',
    '/* ===== mobile-system-20260827.css ===== */',
    '/* ===== mobile-navigation-final-20260827.css ===== */',
    '/* ===== mobile-composition-20260827.css ===== */',
    '/* ===== final-10of10-20260827.css ===== */',
    '/* ===== mobile-qa-final-20260827.css ===== */',
    '/* ===== faq-premium-20260911 ===== */',
    '/* ===== homepage-authority-bundle ===== */',
    '/* ===== homepage-premium-final.css ===== */',
    '/* ===== journal-10of10-20260827.css ===== */',
    '/* ===== release-quality-20260912 ===== */',
    '/* ===== apple-safari-20260911 ===== */',
)

css = CANONICAL.read_text(encoding='utf-8').rstrip() + '\n'
assert len(css) > 60_000
for marker in MARKERS:
    assert css.count(marker) == 1, f'Expected one canonical marker: {marker}'

assert 'inset:auto' not in css.replace(' ', ''), 'Mobile navigation inset reset returned'

workflow = WORKFLOW.read_text(encoding='utf-8')
assert not re.search(r'>>\s*_site/site\.css', workflow), 'Workflow appends to site.css'
assert not re.search(r'\bcat\s+[^\n]+\.css\s*>>', workflow), 'Workflow rebuilds a CSS cascade'

for filename in ('build-journal.py', 'carmen-index.py', 'carmen-journal.py', 'release-quality.py'):
    source = (ROOT / filename).read_text(encoding='utf-8')
    assert not re.search(r'(?:css_path|CSS)\.write_text\(', source), f'{filename} mutates production CSS'

build_source = (ROOT / 'build-release.py').read_text(encoding='utf-8')
assert "CANONICAL_CSS = ROOT / 'styles' / 'site.css'" in build_source
assert 'CSS_PARTS' not in build_source

if BUILT.exists():
    assert BUILT.read_text(encoding='utf-8') == css, 'Built CSS differs from canonical CSS'

print('CSS architecture verified: one canonical source, no build-time append chain.')
