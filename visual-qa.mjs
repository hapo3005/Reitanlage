import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';

const ROOT = process.cwd();
const OUT_DIR = path.resolve('_qa');
const BASELINE_PATH = path.resolve('visual-baseline.json');
const PLAYWRIGHT_VERSION = '1.63.0';
const LHCI_VERSION = '0.15.1';
const PNGJS_VERSION = '7.0.0';
const QA_PORT = 4174;
const BASE_URL = `https://127.0.0.1:${QA_PORT}/`;
const TLS_DIR = path.join(OUT_DIR, 'tls');
const CERT_PATH = path.join(TLS_DIR, 'qa-cert.pem');
const KEY_PATH = path.join(TLS_DIR, 'qa-key.pem');

fs.mkdirSync(OUT_DIR, { recursive: true });
fs.mkdirSync(TLS_DIR, { recursive: true });

function run(command, args, options = {}) {
  console.log(`\n> ${command} ${args.join(' ')}`);
  const result = spawnSync(command, args, {
    cwd: ROOT,
    stdio: 'inherit',
    env: options.env || process.env,
  });
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(' ')} failed with exit code ${result.status}`);
  }
}

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

// The deploy workflow deliberately keeps JavaScript tooling ephemeral. Pin the
// exact QA toolchain here so browser rendering and Lighthouse budgets remain
// reproducible even when the runner image changes.
run('npm', [
  'install', '--no-save', '--no-package-lock', '--ignore-scripts',
  `playwright@${PLAYWRIGHT_VERSION}`,
  `@lhci/cli@${LHCI_VERSION}`,
  `pngjs@${PNGJS_VERSION}`,
]);

const browserInstallEnv = { ...process.env };
delete browserInstallEnv.PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD;
run('npx', ['playwright', 'install', '--with-deps', 'chromium', 'firefox', 'webkit'], {
  env: browserInstallEnv,
});

// Production ships with upgrade-insecure-requests. WebKit correctly upgrades
// localhost subresources when the document is served over HTTP, so a plain
// local HTTP server is not production-equivalent. Generate a one-run certificate
// and serve the built artifact over HTTPS for every engine and Lighthouse.
run('openssl', [
  'req', '-x509', '-newkey', 'rsa:2048', '-sha256', '-days', '1', '-nodes',
  '-keyout', KEY_PATH,
  '-out', CERT_PATH,
  '-subj', '/CN=127.0.0.1',
  '-addext', 'subjectAltName=IP:127.0.0.1,DNS:localhost',
]);

const qaServer = spawn(process.execPath, ['qa-https-server.mjs'], {
  cwd: ROOT,
  env: {
    ...process.env,
    QA_SITE_DIR: path.resolve('_site'),
    QA_HTTPS_PORT: String(QA_PORT),
    QA_CERT_PATH: CERT_PATH,
    QA_KEY_PATH: KEY_PATH,
  },
  stdio: ['ignore', 'pipe', 'pipe'],
});
qaServer.stdout.on('data', (chunk) => process.stdout.write(chunk));
qaServer.stderr.on('data', (chunk) => process.stderr.write(chunk));

let serverClosed = false;
function stopServer() {
  if (serverClosed) return;
  serverClosed = true;
  if (!qaServer.killed) qaServer.kill('SIGTERM');
}
process.on('exit', stopServer);
process.on('SIGINT', () => {
  stopServer();
  process.exit(130);
});
process.on('SIGTERM', () => {
  stopServer();
  process.exit(143);
});

let serverReady = false;
for (let attempt = 0; attempt < 40; attempt += 1) {
  if (qaServer.exitCode !== null) {
    throw new Error(`QA HTTPS server exited early with code ${qaServer.exitCode}`);
  }
  const probe = spawnSync('curl', ['-k', '-fsS', BASE_URL], {
    cwd: ROOT,
    stdio: 'ignore',
  });
  if (probe.status === 0) {
    serverReady = true;
    break;
  }
  sleep(250);
}
if (!serverReady) throw new Error(`QA HTTPS server did not become ready at ${BASE_URL}`);

const { chromium, firefox, webkit } = await import('playwright');
const { PNG } = await import('pngjs');

const browsers = [
  { name: 'chromium', type: chromium },
  { name: 'firefox', type: firefox },
  { name: 'webkit', type: webkit },
];

const viewports = [
  { name: 'mobile-390', width: 390, height: 844 },
  { name: 'tablet-820', width: 820, height: 1100 },
  { name: 'desktop-1440', width: 1440, height: 1000 },
];

const baseline = fs.existsSync(BASELINE_PATH)
  ? JSON.parse(fs.readFileSync(BASELINE_PATH, 'utf8'))
  : null;
const candidate = {
  version: 1,
  playwright: PLAYWRIGHT_VERSION,
  grid: 24,
  signatures: {},
};

function fail(messages, label) {
  if (!messages.length) return;
  throw new Error(`${label}:\n- ${messages.join('\n- ')}`);
}

function visualSignature(buffer, grid = 24) {
  const png = PNG.sync.read(buffer);
  const values = [];
  const samplesPerAxis = 5;

  for (let gy = 0; gy < grid; gy += 1) {
    const y0 = (gy * png.height) / grid;
    const y1 = ((gy + 1) * png.height) / grid;
    for (let gx = 0; gx < grid; gx += 1) {
      const x0 = (gx * png.width) / grid;
      const x1 = ((gx + 1) * png.width) / grid;
      let sum = 0;
      let count = 0;
      for (let sy = 0; sy < samplesPerAxis; sy += 1) {
        const y = Math.min(
          png.height - 1,
          Math.floor(y0 + ((sy + 0.5) / samplesPerAxis) * (y1 - y0)),
        );
        for (let sx = 0; sx < samplesPerAxis; sx += 1) {
          const x = Math.min(
            png.width - 1,
            Math.floor(x0 + ((sx + 0.5) / samplesPerAxis) * (x1 - x0)),
          );
          const i = (y * png.width + x) * 4;
          const alpha = png.data[i + 3] / 255;
          const r = png.data[i] * alpha + 255 * (1 - alpha);
          const g = png.data[i + 1] * alpha + 255 * (1 - alpha);
          const b = png.data[i + 2] * alpha + 255 * (1 - alpha);
          sum += 0.2126 * r + 0.7152 * g + 0.0722 * b;
          count += 1;
        }
      }
      values.push(Math.round(sum / count));
    }
  }

  return { width: png.width, height: png.height, grid, values };
}

function compareSignature(actual, expected, label) {
  const errors = [];
  if (!expected) return [`missing visual baseline for ${label}`];
  if (actual.width !== expected.width) {
    errors.push(`screenshot width ${actual.width}px != baseline ${expected.width}px`);
  }
  const heightDrift = Math.abs(actual.height - expected.height) / Math.max(1, expected.height);
  if (heightDrift > 0.02) {
    errors.push(`full-page height drift ${(heightDrift * 100).toFixed(2)}% > 2%`);
  }
  if (actual.grid !== expected.grid || actual.values.length !== expected.values.length) {
    errors.push('visual signature grid changed');
    return errors;
  }

  const diffs = actual.values.map((value, i) => Math.abs(value - expected.values[i]));
  const mean = diffs.reduce((a, b) => a + b, 0) / diffs.length;
  const sorted = [...diffs].sort((a, b) => a - b);
  const p95 = sorted[Math.floor(sorted.length * 0.95)];
  if (mean > 6) errors.push(`visual mean luminance drift ${mean.toFixed(2)} > 6`);
  if (p95 > 20) errors.push(`visual p95 luminance drift ${p95} > 20`);
  return errors;
}

try {
  for (const browserDef of browsers) {
    const browser = await browserDef.type.launch({ headless: true });

    try {
      for (const viewport of viewports) {
        const label = `${browserDef.name}:${viewport.name}`;
        const context = await browser.newContext({
          viewport: { width: viewport.width, height: viewport.height },
          deviceScaleFactor: 1,
          colorScheme: 'light',
          locale: 'de-DE',
          ignoreHTTPSErrors: true,
        });
        const page = await context.newPage();

        const runtimeErrors = [];
        page.on('pageerror', (error) => runtimeErrors.push(`pageerror: ${error.message}`));
        page.on('console', (message) => {
          if (message.type() === 'error') runtimeErrors.push(`console: ${message.text()}`);
        });
        page.on('response', (response) => {
          const url = response.url();
          if (url.startsWith(BASE_URL) && response.status() >= 400) {
            runtimeErrors.push(`HTTP ${response.status()} ${url}`);
          }
        });

        await page.emulateMedia({ reducedMotion: 'reduce' });
        await page.goto(BASE_URL, { waitUntil: 'networkidle' });
        await page.evaluate(async () => {
          if (document.fonts?.ready) await document.fonts.ready;
          window.scrollTo(0, 0);
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
              const worst = Math.min(...backgrounds.map((bg) => contrast(fg, hex(bg))));
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
          const lessonSources = lesson ? `${lesson.getAttribute('src') || ''} ${lesson.getAttribute('srcset') || ''}` : '';
          if (!lesson || !lessonSources.includes('reistunde1')) errors.push('large Unterricht image is not the curated reistunde1 asset');

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

          return {
            errors,
            pageHeight: document.documentElement.scrollHeight,
            title: document.title,
            lang: document.documentElement.lang,
          };
        }, { width: viewport.width });

        runtimeErrors.push(...audit.errors);
        if (!audit.title.trim()) runtimeErrors.push('document title is empty');
        if (audit.lang !== 'de') runtimeErrors.push(`document lang is ${audit.lang || 'missing'}, expected de`);

        // reducedMotion is already emulated above. Do not ask Playwright to
        // inject its own animation-disabling stylesheet: WebKit correctly blocks
        // that internal inline style under our strict production CSP.
        const screenshot = await page.screenshot({
          path: path.join(OUT_DIR, `${browserDef.name}-${viewport.name}.png`),
          fullPage: true,
        });
        const signature = visualSignature(screenshot, candidate.grid);
        candidate.signatures[label] = signature;

        if (baseline) {
          runtimeErrors.push(...compareSignature(signature, baseline.signatures?.[label], label));
        }

        fail(runtimeErrors, label);
        console.log(`Cross-browser QA ${label}: passed (${audit.pageHeight}px page height).`);
        await context.close();
      }
    } finally {
      await browser.close();
    }
  }

  const candidatePath = path.join(OUT_DIR, 'visual-baseline-candidate.json');
  fs.writeFileSync(candidatePath, `${JSON.stringify(candidate, null, 2)}\n`);

  if (baseline) {
    if (baseline.playwright !== PLAYWRIGHT_VERSION) {
      throw new Error(`Visual baseline uses Playwright ${baseline.playwright}; QA is pinned to ${PLAYWRIGHT_VERSION}. Regenerate baseline intentionally.`);
    }
    console.log('Perceptual visual baseline comparison passed for all 9 browser/viewport combinations.');
  } else {
    console.log('No committed visual baseline yet; candidate generated. Cross-browser structural/contrast gates remain enforced for this bootstrap run.');
  }

  // Lighthouse CI is a separate, deterministic release gate. Three mobile runs
  // reduce runner variance; category and Core Web Vitals budgets live in the
  // checked-in lighthouserc.cjs and reports stay private in the workflow artifact.
  run('npx', ['lhci', 'autorun', '--config=./lighthouserc.cjs']);

  console.log('Engineering gate passed: Chromium + Firefox + WebKit, responsive/contrast checks, visual regression and Lighthouse budgets.');
} finally {
  stopServer();
}
