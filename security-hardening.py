from __future__ import annotations

from pathlib import Path
import base64
import hashlib
import re

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
  a.className='news-link';
  a.href=href;
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

    harden_runtime_js()
    html_files = sorted(OUT.glob("*.html"))
    if not html_files:
        raise RuntimeError("No generated HTML files found")
    for path in html_files:
        harden_html(path)

    print(
        f"Security hardening applied to {len(html_files)} HTML files and production JavaScript."
    )


if __name__ == "__main__":
    main()
