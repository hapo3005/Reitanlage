from __future__ import annotations

from pathlib import Path
import base64
import hashlib
import re

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / "_site"

CSP_META_RE = re.compile(
    r'<meta\s+http-equiv=["\']Content-Security-Policy["\'][^>]*>\s*',
    re.I,
)
REFERRER_META_RE = re.compile(
    r'<meta\s+name=["\']referrer["\'][^>]*>\s*',
    re.I,
)
INLINE_SCRIPT_RE = re.compile(
    r'<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>',
    re.I | re.S,
)
INLINE_STYLE_RE = re.compile(r'<style\b[^>]*>(.*?)</style>', re.I | re.S)
ANCHOR_RE = re.compile(r'<a\b[^>]*\bhref=["\'][^"\']+["\'][^>]*>', re.I)

APPLE_META_NAMES = (
    "apple-mobile-web-app-capable",
    "mobile-web-app-capable",
    "apple-mobile-web-app-status-bar-style",
    "apple-mobile-web-app-title",
    "format-detection",
)
APPLE_CSS_MARKER = "/* ===== apple-safari-20260911 ===== */"
APPLE_CSS = r"""
/* ===== apple-safari-20260911 ===== */
:root{color-scheme:light}
html{-webkit-text-size-adjust:100%}
body{-webkit-font-smoothing:antialiased}
a,button,summary{touch-action:manipulation;-webkit-tap-highlight-color:rgba(23,48,39,.14)}
.header.scrolled{-webkit-backdrop-filter:blur(10px)}
@supports (top:env(safe-area-inset-top)){
  .header{top:env(safe-area-inset-top)}
  .skip:focus{top:max(18px,env(safe-area-inset-top))}
  @media (orientation:landscape) and (max-width:932px){
    .header{left:env(safe-area-inset-left);right:env(safe-area-inset-right)}
    .hero-copy{padding-left:max(24px,env(safe-area-inset-left));padding-right:max(24px,env(safe-area-inset-right))}
    .facts{padding-left:max(30px,env(safe-area-inset-left));padding-right:max(30px,env(safe-area-inset-right))}
    .stable,.pricing,.contact{padding-left:max(32px,env(safe-area-inset-left));padding-right:max(32px,env(safe-area-inset-right))}
  }
}
@supports (-webkit-touch-callout:none){
  input,textarea,select{font-size:16px}
}
""".strip() + "\n"

APPLE_404_CSS = r"""
html{-webkit-text-size-adjust:100%;color-scheme:light}
body{-webkit-font-smoothing:antialiased}
a{touch-action:manipulation;-webkit-tap-highlight-color:rgba(23,48,39,.14)}
@supports (padding:env(safe-area-inset-top)){
  body{padding-top:max(24px,env(safe-area-inset-top));padding-right:max(24px,env(safe-area-inset-right));padding-bottom:max(24px,env(safe-area-inset-bottom));padding-left:max(24px,env(safe-area-inset-left))}
}
""".strip()


def sha256_source(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


def merge_rel(tag: str, *tokens: str) -> str:
    rel_match = re.search(r'\brel=["\']([^"\']*)["\']', tag, re.I)
    existing = set(rel_match.group(1).split()) if rel_match else set()
    existing.update(tokens)
    rel_value = " ".join(sorted(existing))
    if rel_match:
        return tag[: rel_match.start()] + f'rel="{rel_value}"' + tag[rel_match.end() :]
    return tag[:-1] + f' rel="{rel_value}">'


def secure_anchor(match: re.Match[str]) -> str:
    tag = match.group(0)
    href_match = re.search(r'\bhref=["\']([^"\']+)["\']', tag, re.I)
    if not href_match:
        return tag
    href = href_match.group(1).strip().lower()
    if href.startswith(("https://", "http://")):
        tag = merge_rel(tag, "noopener", "noreferrer")
    if re.search(r'\btarget=["\']_blank["\']', tag, re.I):
        tag = merge_rel(tag, "noopener", "noreferrer")
    return tag


def build_apple_assets() -> None:
    icon = Image.new("RGB", (180, 180), "#173027")
    draw = ImageDraw.Draw(icon)
    cream = "#f4f0e7"

    # Geometric E/N mark matching the existing favicon language; no font
    # dependency keeps CI output deterministic across GitHub runners.
    draw.rectangle((40, 42, 50, 138), fill=cream)
    draw.rectangle((50, 42, 83, 52), fill=cream)
    draw.rectangle((50, 85, 78, 95), fill=cream)
    draw.rectangle((50, 128, 83, 138), fill=cream)
    draw.rectangle((100, 42, 110, 138), fill=cream)
    draw.rectangle((140, 42, 150, 138), fill=cream)
    draw.line((106, 47, 144, 133), fill=cream, width=10)
    icon.save(OUT / "apple-touch-icon.png", "PNG", optimize=True)

    mask_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<path d="M14 17h15v4H19v8h9v4h-9v10h10v4H14V17Zm22 0h4l10 21V17h4v30h-4L40 26v21h-4V17Z"/>
</svg>\n'''
    (OUT / "safari-pinned-tab.svg").write_text(mask_svg, encoding="utf-8")


def harden_stylesheets() -> None:
    for filename in ("site.css", "legal-page.css"):
        path = OUT / filename
        if not path.exists():
            continue
        css = path.read_text(encoding="utf-8")
        if APPLE_CSS_MARKER not in css:
            path.write_text(css.rstrip() + "\n\n" + APPLE_CSS, encoding="utf-8")


def add_apple_head(html: str) -> str:
    for name in APPLE_META_NAMES:
        html = re.sub(
            rf'<meta\s+name=["\']{re.escape(name)}["\'][^>]*>\s*',
            "",
            html,
            flags=re.I,
        )
    html = re.sub(
        r'<link\s+rel=["\']apple-touch-icon["\'][^>]*>\s*',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'<link\s+rel=["\']mask-icon["\'][^>]*>\s*',
        "",
        html,
        flags=re.I,
    )

    viewport = '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    if re.search(r'<meta\s+name=["\']viewport["\'][^>]*>', html, re.I):
        html = re.sub(
            r'<meta\s+name=["\']viewport["\'][^>]*>',
            viewport,
            html,
            count=1,
            flags=re.I,
        )
    else:
        html = html.replace("<head>", "<head>" + viewport, 1)

    apple = (
        '<meta name="format-detection" content="telephone=no">'
        '<meta name="mobile-web-app-capable" content="yes">'
        '<meta name="apple-mobile-web-app-capable" content="yes">'
        '<meta name="apple-mobile-web-app-status-bar-style" content="default">'
        '<meta name="apple-mobile-web-app-title" content="Eichhorn-Nels">'
        '<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">'
        '<link rel="mask-icon" href="safari-pinned-tab.svg" color="#173027">'
    )
    return html.replace(viewport, viewport + apple, 1)


def security_policy(html: str) -> str:
    script_hashes = sorted(
        {sha256_source(body) for body in INLINE_SCRIPT_RE.findall(html) if body.strip()}
    )
    style_hashes = sorted(
        {sha256_source(body) for body in INLINE_STYLE_RE.findall(html) if body.strip()}
    )

    script_sources = " ".join(["'self'", *script_hashes])
    style_sources = " ".join(["'self'", *style_hashes])

    return "; ".join(
        [
            "default-src 'self'",
            f"script-src {script_sources}",
            f"script-src-elem {script_sources}",
            "script-src-attr 'none'",
            f"style-src {style_sources}",
            f"style-src-elem {style_sources}",
            "style-src-attr 'unsafe-inline'",
            "img-src 'self' data:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "manifest-src 'self'",
            "media-src 'self'",
            "object-src 'none'",
            "frame-src 'none'",
            "worker-src 'none'",
            "base-uri 'none'",
            "form-action 'none'",
            "upgrade-insecure-requests",
        ]
    )


def harden_html(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    html = CSP_META_RE.sub("", html)
    html = REFERRER_META_RE.sub("", html)
    html = ANCHOR_RE.sub(secure_anchor, html)
    html = add_apple_head(html)

    if path.name == "404.html" and APPLE_404_CSS not in html:
        html = html.replace("</style>", APPLE_404_CSS + "</style>", 1)

    policy = security_policy(html)
    meta = (
        f'<meta http-equiv="Content-Security-Policy" content="{policy}">'
        '<meta name="referrer" content="no-referrer">'
    )

    if '<meta name="viewport"' in html:
        html = re.sub(
            r'(<meta\s+name=["\']viewport["\'][^>]*>)',
            r'\1' + meta,
            html,
            count=1,
            flags=re.I,
        )
    else:
        html = html.replace("<head>", "<head>" + meta, 1)

    if re.search(r'<(?:script|link)\b[^>]*(?:src|href)=["\']http://', html, re.I):
        raise RuntimeError(f"Insecure HTTP resource in {path.name}")
    if re.search(r'<script\b[^>]*\bsrc=["\']https?://', html, re.I):
        raise RuntimeError(f"External script source in {path.name}")
    if re.search(
        r'<link\b[^>]*\brel=["\']stylesheet["\'][^>]*\bhref=["\']https?://',
        html,
        re.I,
    ):
        raise RuntimeError(f"External stylesheet in {path.name}")
    if re.search(r'\bon[a-z]+\s*=', html, re.I):
        raise RuntimeError(f"Inline event handler in {path.name}")
    if re.search(r'(?:href|src)=["\']\s*javascript:', html, re.I):
        raise RuntimeError(f"javascript: URL in {path.name}")

    path.write_text(html, encoding="utf-8")


def harden_runtime_js() -> None:
    path = OUT / "site.js"
    js = path.read_text(encoding="utf-8")

    old_news_link = """function newsLink(item){
  if(!item.link||!item.linkText)return null;
  const a=document.createElement('a');
  a.className='news-link';
  a.href=item.link;
  a.textContent=item.linkText;
  return a;
}
"""
    new_news_link = """function safeNewsHref(value){
  const raw=String(value||'').trim();
  if(!raw)return null;
  if(raw.startsWith('#'))return /^#[A-Za-z][A-Za-z0-9_.:-]*$/.test(raw)?raw:null;
  try{
    const url=new URL(raw,window.location.href);
    if(url.origin===window.location.origin)return url.href;
    if(url.protocol==='https:'||url.protocol==='mailto:'||url.protocol==='tel:')return url.href;
  }catch(_err){return null;}
  return null;
}

function newsLink(item){
  const href=safeNewsHref(item.link);
  if(!href||!item.linkText)return null;
  const a=document.createElement('a');
  a.href=href;
  a.className='news-link';
  a.textContent=item.linkText;
  if(href.startsWith('https://')){
    const target=new URL(href);
    if(target.origin!==window.location.origin)a.rel='noopener noreferrer';
  }
  return a;
}

function setNewsMessage(host,message){
  const p=document.createElement('p');
  p.textContent=message;
  host.replaceChildren(p);
}
"""

    if old_news_link not in js:
        raise RuntimeError("Expected newsLink implementation was not found")
    js = js.replace(old_news_link, new_news_link, 1)

    replacements = {
        "host.innerHTML='<p>Aktuell sind keine Meldungen veröffentlicht. Für Termine und Verfügbarkeiten bitte direkt Kontakt aufnehmen.</p>';": "setNewsMessage(host,'Aktuell sind keine Meldungen veröffentlicht. Für Termine und Verfügbarkeiten bitte direkt Kontakt aufnehmen.');",
        "host.innerHTML='<p>Die aktuellen Meldungen konnten nicht geladen werden. Termine bitte direkt telefonisch oder per WhatsApp erfragen.</p>';": "setNewsMessage(host,'Die aktuellen Meldungen konnten nicht geladen werden. Termine bitte direkt telefonisch oder per WhatsApp erfragen.');",
    }
    for old, new in replacements.items():
        if old not in js:
            raise RuntimeError(f"Expected JavaScript sink not found: {old[:36]}")
        js = js.replace(old, new, 1)

    forbidden = ["innerHTML", "eval(", "new Function(", "document.write("]
    for token in forbidden:
        if token in js:
            raise RuntimeError(f"Forbidden JavaScript sink remains in production bundle: {token}")

    path.write_text(js, encoding="utf-8")


def main() -> None:
    if not OUT.exists():
        raise RuntimeError("_site does not exist; run the production build first")

    build_apple_assets()
    harden_stylesheets()
    harden_runtime_js()
    html_files = sorted(OUT.glob("*.html"))
    if not html_files:
        raise RuntimeError("No generated HTML files found")
    for path in html_files:
        harden_html(path)

    print(
        f"Security hardening plus Apple/Safari optimization applied to {len(html_files)} HTML files."
    )


if __name__ == "__main__":
    main()
