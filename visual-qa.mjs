import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

const chromePath = process.env.CHROME_PATH;
if (!chromePath) throw new Error('CHROME_PATH is required for visual QA.');

const outDir = path.resolve('_qa');
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: chromePath,
  headless: true,
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
});

const viewports = [
  { name: 'mobile-390', width: 390, height: 844 },
  { name: 'tablet-820', width: 820, height: 1100 },
  { name: 'desktop-1440', width: 1440, height: 1000 },
];

function fail(messages, viewport) {
  if (!messages.length) return;
  throw new Error(`${viewport}:\n- ${messages.join('\n- ')}`);
}

for (const viewport of viewports) {
  const page = await browser.newPage({
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: 1,
  });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('http://127.0.0.1:4173/', { waitUntil: 'networkidle' });
  await page.evaluate(async () => {
    if (document.fonts?.ready) await document.fonts.ready;
  });

  const audit = await page.evaluate(({ width }) => {
    const errors = [];

    const parseColor = (value) => {
      const match = String(value).match(/rgba?\((\d+(?:\.\d+)?)[, ]+(\d+(?:\.\d+)?)[, ]+(\d+(?:\.\d+)?)/i);
      return match ? [Number(match[1]), Number(match[2]), Number(match[3])] : null;
    };
    const hex = (value) => {
      const clean = value.replace('#', '');
      return [0, 2, 4].map((i) => parseInt(clean.slice(i, i + 2), 16));
    };
    const luminance = (rgb) => {
      const linear = rgb.map((component) => {
        const c = component / 255;
        return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
      });
      return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722;
    };
    const contrast = (a, b) => {
      const l1 = luminance(a);
      const l2 = luminance(b);
      return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    };
    const requireContrast = (selector, backgrounds, minimum = 4.5) => {
      const nodes = [...document.querySelectorAll(selector)];
      if (!nodes.length) {
        errors.push(`missing contrast target ${selector}`);
        return;
      }
      for (const node of nodes) {
        const style = getComputedStyle(node);
        const fg = parseColor(style.color);
        if (!fg) {
          errors.push(`unreadable computed color for ${selector}: ${style.color}`);
          continue;
        }
        const ratios = backgrounds.map((bg) => contrast(fg, hex(bg)));
        const worst = Math.min(...ratios);
        if (worst < minimum) errors.push(`${selector} contrast ${worst.toFixed(2)} < ${minimum}`);
        const rect = node.getBoundingClientRect();
        if (rect.width < 1 || rect.height < 1) errors.push(`${selector} has zero geometry`);
        if (Number(style.opacity) < 0.75) errors.push(`${selector} opacity ${style.opacity} is too low`);
      }
    };

    if (document.documentElement.scrollWidth > window.innerWidth + 2) {
      errors.push(`horizontal overflow ${document.documentElement.scrollWidth}px > ${window.innerWidth}px`);
    }

    const required = ['#start', '#haltung', '#ausbildung', '#anlage', '#pferde', '#aktuelles', '#preise', '#fragen', '#kontakt'];
    for (const selector of required) if (!document.querySelector(selector)) errors.push(`missing ${selector}`);
    if (!document.querySelector('nav a[href="#fragen"]')) errors.push('primary navigation has no Fragen destination');

    const lesson = document.querySelector('.cinematic img');
    if (!lesson || !lesson.currentSrc.includes('reistunde1')) errors.push('large Unterricht image is not the curated reistunde1 asset');

    for (const link of document.querySelectorAll('.hero-links>a')) {
      const rect = link.getBoundingClientRect();
      if (rect.height < 44) errors.push(`hero CTA touch target ${rect.height.toFixed(1)}px < 44px`);
    }
    for (const summary of document.querySelectorAll('.faq-item summary')) {
      const rect = summary.getBoundingClientRect();
      if (rect.height < 44) errors.push(`FAQ target ${rect.height.toFixed(1)}px < 44px`);
    }

    requireContrast('.stable-copy>p:not(.kicker)', ['#17382d', '#10291f']);
    requireContrast('.stable-specs dd', ['#17382d', '#10291f']);
    requireContrast('.terrain>p:not(.kicker)', ['#17382d', '#10291f']);
    requireContrast('.pricing-intro>p:not(.kicker)', ['#15372b', '#102b21']);
    requireContrast('.price-highlight span', ['#15372b', '#102b21']);

    const heroTitle = document.querySelector('.hero-copy h1')?.getBoundingClientRect();
    if (!heroTitle || heroTitle.width < Math.min(240, width * 0.55)) errors.push('hero title collapsed unexpectedly');

    if (width <= 820) {
      for (const image of document.querySelectorAll('.horse-ledger figure')) {
        const rect = image.getBoundingClientRect();
        if (rect.width > 140) errors.push(`archival horse image rendered too large on mobile: ${rect.width.toFixed(1)}px`);
      }
    }

    return { errors, pageHeight: document.documentElement.scrollHeight };
  }, { width: viewport.width });

  fail(audit.errors, viewport.name);
  await page.screenshot({
    path: path.join(outDir, `${viewport.name}.png`),
    fullPage: true,
    animations: 'disabled',
  });
  console.log(`Visual QA ${viewport.name}: passed (${audit.pageHeight}px page height).`);
  await page.close();
}

await browser.close();
console.log('Browser visual regression, responsive layout and contrast checks passed.');
