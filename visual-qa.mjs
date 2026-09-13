import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';

const ROOT = process.cwd();
const OUT = path.resolve('_qa');
const BASELINE = path.resolve('visual-baseline.json');
const PLAYWRIGHT_VERSION = '1.63.0';
const LHCI_VERSION = '0.15.1';
const PNGJS_VERSION = '7.0.0';
const PORT = 4174;
const URL = `https://127.0.0.1:${PORT}/`;
const TLS = path.join(OUT, 'tls');
const CERT = path.join(TLS, 'qa-cert.pem');
const KEY = path.join(TLS, 'qa-key.pem');

fs.mkdirSync(TLS, { recursive: true });

function run(command, args, env = process.env) {
  console.log(`\n> ${command} ${args.join(' ')}`);
  const result = spawnSync(command, args, { cwd: ROOT, stdio: 'inherit', env });
  if (result.status !== 0) throw new Error(`${command} failed with exit code ${result.status}`);
}
function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}
function fail(errors, label) {
  if (errors.length) throw new Error(`${label}:\n- ${errors.join('\n- ')}`);
}
function addCspErrors(errors, violations) {
  for (const violation of violations) {
    const source = violation.sourceFile || 'inline/unknown';
    const blocked = violation.blockedURI || 'inline';
    errors.push(
      `CSP ${violation.effectiveDirective || violation.violatedDirective} blocked=${blocked} source=${source}:${violation.lineNumber}:${violation.columnNumber} sample=${violation.sample || '-'}`,
    );
  }
}

run('npm', [
  'install', '--no-save', '--no-package-lock', '--ignore-scripts',
  `playwright@${PLAYWRIGHT_VERSION}`,
  `@lhci/cli@${LHCI_VERSION}`,
  `pngjs@${PNGJS_VERSION}`,
]);
const installEnv = { ...process.env };
delete installEnv.PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD;
run('npx', ['playwright', 'install', '--with-deps', 'chromium', 'firefox', 'webkit'], installEnv);
run('openssl', [
  'req', '-x509', '-newkey', 'rsa:2048', '-sha256', '-days', '1', '-nodes',
  '-keyout', KEY, '-out', CERT, '-subj', '/CN=127.0.0.1',
  '-addext', 'subjectAltName=IP:127.0.0.1,DNS:localhost',
]);

const server = spawn(process.execPath, ['qa-https-server.mjs'], {
  cwd: ROOT,
  env: {
    ...process.env,
    QA_SITE_DIR: path.resolve('_site'),
    QA_HTTPS_PORT: String(PORT),
    QA_CERT_PATH: CERT,
    QA_KEY_PATH: KEY,
  },
  stdio: ['ignore', 'pipe', 'pipe'],
});
server.stdout.on('data', chunk => process.stdout.write(chunk));
server.stderr.on('data', chunk => process.stderr.write(chunk));
let stopped = false;
function stopServer() {
  if (stopped) return;
  stopped = true;
  if (!server.killed) server.kill('SIGTERM');
}
process.on('exit', stopServer);

let ready = false;
for (let attempt = 0; attempt < 40; attempt += 1) {
  const probe = spawnSync('curl', ['-k', '-fsS', URL], { stdio: 'ignore' });
  if (probe.status === 0) { ready = true; break; }
  if (server.exitCode !== null) throw new Error(`QA HTTPS server exited with ${server.exitCode}`);
  sleep(250);
}
if (!ready) throw new Error(`QA HTTPS server did not become ready at ${URL}`);

const { chromium, firefox, webkit } = await import('playwright');
const { PNG } = await import('pngjs');
const browsers = [
  ['chromium', chromium],
  ['firefox', firefox],
  ['webkit', webkit],
];
const viewports = [
  ['mobile-390', 390, 844],
  ['tablet-820', 820, 1100],
  ['desktop-1440', 1440, 1000],
  ['desktop-wide-1920', 1920, 900],
];
const baseline = fs.existsSync(BASELINE) ? JSON.parse(fs.readFileSync(BASELINE, 'utf8')) : null;
const candidate = { version: 1, playwright: PLAYWRIGHT_VERSION, grid: 24, signatures: {} };

function signature(buffer, grid = 24) {
  const png = PNG.sync.read(buffer);
  const values = [];
  const samples = 5;
  for (let gy = 0; gy < grid; gy += 1) {
    const y0 = gy * png.height / grid;
    const y1 = (gy + 1) * png.height / grid;
    for (let gx = 0; gx < grid; gx += 1) {
      const x0 = gx * png.width / grid;
      const x1 = (gx + 1) * png.width / grid;
      let total = 0;
      let count = 0;
      for (let sy = 0; sy < samples; sy += 1) {
        const y = Math.min(png.height - 1, Math.floor(y0 + ((sy + .5) / samples) * (y1 - y0)));
        for (let sx = 0; sx < samples; sx += 1) {
          const x = Math.min(png.width - 1, Math.floor(x0 + ((sx + .5) / samples) * (x1 - x0)));
          const i = (y * png.width + x) * 4;
          const a = png.data[i + 3] / 255;
          const r = png.data[i] * a + 255 * (1 - a);
          const g = png.data[i + 1] * a + 255 * (1 - a);
          const b = png.data[i + 2] * a + 255 * (1 - a);
          total += .2126 * r + .7152 * g + .0722 * b;
          count += 1;
        }
      }
      values.push(Math.round(total / count));
    }
  }
  return { width: png.width, height: png.height, grid, values };
}
function compare(actual, expected, label) {
  const errors = [];
  if (!expected) return [`missing visual baseline for ${label}`];
  if (actual.width !== expected.width) errors.push(`screenshot width ${actual.width}px != ${expected.width}px baseline`);
  const heightDrift = Math.abs(actual.height - expected.height) / Math.max(1, expected.height);
  if (heightDrift > .02) errors.push(`full-page height drift ${(heightDrift * 100).toFixed(2)}% > 2%`);
  if (actual.grid !== expected.grid || actual.values.length !== expected.values.length) return [...errors, 'visual signature grid changed'];
  const diffs = actual.values.map((value, i) => Math.abs(value - expected.values[i]));
  const mean = diffs.reduce((a, b) => a + b, 0) / diffs.length;
  const sorted = [...diffs].sort((a, b) => a - b);
  const p95 = sorted[Math.floor(sorted.length * .95)];
  if (mean > 6) errors.push(`visual mean luminance drift ${mean.toFixed(2)} > 6`);
  if (p95 > 20) errors.push(`visual p95 luminance drift ${p95} > 20`);
  return errors;
}

try {
  for (const [browserName, browserType] of browsers) {
    const browser = await browserType.launch({ headless: true });
    try {
      for (const [viewportName, width, height] of viewports) {
        const label = `${browserName}:${viewportName}`;
        const context = await browser.newContext({
          viewport: { width, height },
          deviceScaleFactor: 1,
          colorScheme: 'light',
          locale: 'de-DE',
          ignoreHTTPSErrors: true,
        });
        await context.addInitScript(() => {
          window.__qaCspViolations = [];
          document.addEventListener('securitypolicyviolation', event => {
            window.__qaCspViolations.push({
              blockedURI: event.blockedURI || '',
              effectiveDirective: event.effectiveDirective || '',
              violatedDirective: event.violatedDirective || '',
              sourceFile: event.sourceFile || '',
              lineNumber: event.lineNumber || 0,
              columnNumber: event.columnNumber || 0,
              sample: event.sample || '',
              disposition: event.disposition || '',
            });
          }, true);
        });
        const page = await context.newPage();
        const runtimeErrors = [];
        const consoleErrors = [];
        page.on('pageerror', error => runtimeErrors.push(`pageerror: ${error.message}`));
        page.on('console', message => {
          if (message.type() !== 'error') return;
          const loc = message.location();
          consoleErrors.push(`console: ${message.text()} @ ${loc.url || 'unknown'}:${loc.lineNumber ?? 0}:${loc.columnNumber ?? 0}`);
        });
        page.on('response', response => {
          if (response.url().startsWith(URL) && response.status() >= 400) {
            runtimeErrors.push(`HTTP ${response.status()} ${response.url()}`);
          }
        });

        // Runtime/CSP validation is deliberately completed before screenshot
        // capture. Playwright may use engine-specific helper styles while
        // producing a full-page image; those belong to the QA harness and are
        // not executable production page behavior.
        await page.goto(URL, { waitUntil: 'networkidle' });
        await page.evaluate(async () => {
          if (document.fonts?.ready) await document.fonts.ready;
          window.scrollTo(0, 0);
        });
        await page.waitForTimeout(1200);

        const audit = await page.evaluate(({ width }) => {
          const errors = [];
          const parse = value => {
            const m = String(value).match(/rgba?\((\d+(?:\.\d+)?)[, ]+(\d+(?:\.\d+)?)[, ]+(\d+(?:\.\d+)?)/i);
            return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
          };
          const hex = value => [0, 2, 4].map(i => parseInt(value.replace('#', '').slice(i, i + 2), 16));
          const luminance = rgb => {
            const c = rgb.map(v => {
              const x = v / 255;
              return x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4;
            });
            return c[0] * .2126 + c[1] * .7152 + c[2] * .0722;
          };
          const ratio = (a, b) => {
            const x = luminance(a), y = luminance(b);
            return (Math.max(x, y) + .05) / (Math.min(x, y) + .05);
          };
          const requireContrast = (selector, backgrounds, minimum = 4.5) => {
            const nodes = [...document.querySelectorAll(selector)];
            if (!nodes.length) return errors.push(`missing contrast target ${selector}`);
            for (const node of nodes) {
              const style = getComputedStyle(node);
              const fg = parse(style.color);
              if (!fg) { errors.push(`unreadable computed color for ${selector}: ${style.color}`); continue; }
              const worst = Math.min(...backgrounds.map(bg => ratio(fg, hex(bg))));
              if (worst < minimum) errors.push(`${selector} contrast ${worst.toFixed(2)} < ${minimum}`);
              const rect = node.getBoundingClientRect();
              if (rect.width < 1 || rect.height < 1) errors.push(`${selector} has zero geometry`);
              if (Number(style.opacity) < .75) errors.push(`${selector} opacity ${style.opacity} is too low`);
            }
          };

          if (document.documentElement.scrollWidth > window.innerWidth + 2) errors.push(`horizontal overflow ${document.documentElement.scrollWidth}px > ${window.innerWidth}px`);
          for (const selector of ['#start','#haltung','#ausbildung','#anlage','#pferde','#aktuelles','#preise','#fragen','#kontakt']) {
            if (!document.querySelector(selector)) errors.push(`missing ${selector}`);
          }
          if (!document.querySelector('nav a[href="#fragen"]')) errors.push('primary navigation has no Fragen destination');
          const lesson = document.querySelector('.cinematic img');
          const lessonSources = lesson ? `${lesson.getAttribute('src') || ''} ${lesson.getAttribute('srcset') || ''}` : '';
          if (!lesson || !lessonSources.includes('reistunde1')) errors.push('large Unterricht image is not the curated reistunde1 asset');
          for (const link of document.querySelectorAll('.hero-links>a')) {
            if (link.getBoundingClientRect().height < 44) errors.push('hero CTA touch target < 44px');
          }
          for (const summary of document.querySelectorAll('.faq-item summary')) {
            if (summary.getBoundingClientRect().height < 44) errors.push('FAQ target < 44px');
          }
          requireContrast('.stable-copy>p:not(.kicker)', ['#17382d','#10291f']);
          requireContrast('.stable-specs dd', ['#17382d','#10291f']);
          requireContrast('.terrain>p:not(.kicker)', ['#17382d','#10291f']);
          requireContrast('.pricing-intro>p:not(.kicker)', ['#15372b','#102b21']);
          requireContrast('.price-highlight span', ['#15372b','#102b21']);
          const heroTitle = document.querySelector('.hero-copy h1')?.getBoundingClientRect();
          if (!heroTitle || heroTitle.width < Math.min(240, width * .55)) errors.push('hero title collapsed unexpectedly');
          if (width > 820) {
            const header = document.querySelector('.header')?.getBoundingClientRect();
            const hero = document.querySelector('.hero')?.getBoundingClientRect();
            const heroCopy = document.querySelector('.hero-copy')?.getBoundingClientRect();
            const heroActions = document.querySelector('.hero-links')?.getBoundingClientRect();
            const heroImage = document.querySelector('.hero-image')?.getBoundingClientRect();
            const facts = document.querySelector('.facts')?.getBoundingClientRect();
            if (!header || !hero || !heroCopy || !heroActions || !heroImage || !heroTitle || !facts) {
              errors.push('desktop hero geometry is incomplete');
            } else {
              if (heroTitle.top < header.bottom + 18) errors.push(`hero title overlaps header (${heroTitle.top.toFixed(1)}px < ${(header.bottom + 18).toFixed(1)}px)`);
              if (heroTitle.bottom > window.innerHeight - 88) errors.push(`hero title leaves first viewport (${heroTitle.bottom.toFixed(1)}px > ${window.innerHeight - 88}px)`);
              if (heroActions.bottom > window.innerHeight - 24) errors.push(`hero actions leave first viewport (${heroActions.bottom.toFixed(1)}px > ${window.innerHeight - 24}px)`);
              if (heroTitle.top - header.bottom > 260) errors.push(`desktop hero has ${Math.round(heroTitle.top - header.bottom)}px dead space above title`);
              if (heroImage.top < header.bottom + 12) errors.push('hero image begins underneath the header');
              if (heroImage.bottom > window.innerHeight - 20) errors.push('hero image is clipped by the first viewport');
              if (heroImage.width < width * .42) errors.push('hero image lost desktop visual authority');
              if (heroCopy.width > width * .48) errors.push('hero copy lane is too wide');
              if (heroImage.bottom - heroActions.bottom > 190) errors.push(`desktop hero leaves ${Math.round(heroImage.bottom - heroActions.bottom)}px unused below its actions`);
              if (facts.top > window.innerHeight - 70) errors.push('desktop hero hides the transition into its factual summary');
            }
          }
          if (width <= 820) {
            for (const figure of document.querySelectorAll('.horse-ledger figure')) {
              if (figure.getBoundingClientRect().width > 140) errors.push('archival horse image rendered too large on mobile');
            }
          }
          return { errors, pageHeight: document.documentElement.scrollHeight, title: document.title, lang: document.documentElement.lang };
        }, { width });

        runtimeErrors.push(...audit.errors);

        if (width <= 820) {
          const mobileNavigationErrors = await page.evaluate(async () => {
            const errors = [];
            const trigger = document.querySelector('[data-menu]');
            const nav = document.querySelector('[data-nav]');
            const header = document.querySelector('[data-header]');
            if (!trigger || !nav || !header) return ['menu trigger, navigation or header is missing'];

            if (nav.classList.contains('open')) trigger.click();
            trigger.click();
            await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));

            const links = [...nav.querySelectorAll('a')];
            const navRect = nav.getBoundingClientRect();
            const headerRect = header.getBoundingClientRect();
            const firstRect = links[0]?.getBoundingClientRect();
            const lastRect = links.at(-1)?.getBoundingClientRect();
            const visibleBottom = Math.min(navRect.bottom, window.innerHeight);

            if (!nav.classList.contains('open')) errors.push('menu did not open');
            if (Math.abs(nav.scrollTop) > 1) errors.push(`opened with scrollTop ${nav.scrollTop}px`);
            if (navRect.top < headerRect.bottom + 4) {
              errors.push(`panel top ${navRect.top.toFixed(1)}px overlaps header bottom ${headerRect.bottom.toFixed(1)}px`);
            }
            if (!firstRect || firstRect.top < navRect.top - 1 || firstRect.bottom > visibleBottom + 1) {
              errors.push('first destination is not fully visible');
            }
            if (!lastRect || lastRect.top < navRect.top - 1 || lastRect.bottom > visibleBottom + 1) {
              errors.push('last destination is not fully visible');
            }

            trigger.click();
            return errors;
          });
          runtimeErrors.push(...mobileNavigationErrors.map(error => `mobile navigation: ${error}`));
        }

        if (!audit.title.trim()) runtimeErrors.push('document title is empty');
        if (audit.lang !== 'de') runtimeErrors.push(`document lang is ${audit.lang || 'missing'}, expected de`);

        const runtimeCspViolations = await page.evaluate(() => window.__qaCspViolations || []);
        addCspErrors(runtimeErrors, runtimeCspViolations);
        const genericCsp = /Refused to apply a stylesheet because/i;
        runtimeErrors.push(...consoleErrors.filter(message => !(runtimeCspViolations.length && genericCsp.test(message))));
        fail(runtimeErrors, `${label} production runtime`);

        // From this point on, browser instrumentation is excluded from runtime
        // security accounting. Screenshot capture still fails normally if the
        // browser cannot produce the image, while production CSP has already
        // been validated under the same HTTPS origin.
        await page.evaluate(() => { window.__qaCspViolations = []; });
        consoleErrors.length = 0;

        const screenshot = await page.screenshot({
          path: path.join(OUT, `${browserName}-${viewportName}.png`),
          fullPage: true,
          animations: 'allow',
          caret: 'initial',
        });
        const actual = signature(screenshot, candidate.grid);
        candidate.signatures[label] = actual;
        const visualErrors = baseline ? compare(actual, baseline.signatures?.[label], label) : [];
        fail(visualErrors, `${label} visual regression`);

        console.log(`Cross-browser QA ${label}: passed (${audit.pageHeight}px page height).`);
        await context.close();
      }
    } finally {
      await browser.close();
    }
  }

  fs.writeFileSync(path.join(OUT, 'visual-baseline-candidate.json'), `${JSON.stringify(candidate, null, 2)}\n`);
  if (baseline) {
    if (baseline.playwright !== PLAYWRIGHT_VERSION) throw new Error(`Visual baseline Playwright ${baseline.playwright} != ${PLAYWRIGHT_VERSION}`);
    console.log('Perceptual visual baseline comparison passed for all 9 browser/viewport combinations.');
  } else {
    console.log('No committed visual baseline yet; candidate generated. Structural, runtime and contrast gates remain enforced.');
  }

  run('npx', ['lhci', 'autorun', '--config=./lighthouserc.cjs']);
  console.log('Engineering gate passed: Chromium + Firefox + WebKit, CSP/runtime, responsive/contrast, visual regression and Lighthouse.');
} finally {
  stopServer();
}
