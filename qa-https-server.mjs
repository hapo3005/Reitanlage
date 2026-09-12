import https from 'node:https';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const ROOT = path.resolve(process.env.QA_SITE_DIR || '_site');
const PORT = Number(process.env.QA_HTTPS_PORT || 4174);
const certPath = process.env.QA_CERT_PATH;
const keyPath = process.env.QA_KEY_PATH;

if (!certPath || !keyPath) throw new Error('QA_CERT_PATH and QA_KEY_PATH are required.');

const mime = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
  ['.jpg', 'image/jpeg'],
  ['.jpeg', 'image/jpeg'],
  ['.webp', 'image/webp'],
  ['.xml', 'application/xml; charset=utf-8'],
  ['.txt', 'text/plain; charset=utf-8'],
  ['.webmanifest', 'application/manifest+json; charset=utf-8'],
]);
const compressible = new Set(['.html', '.css', '.js', '.json', '.svg', '.xml', '.txt', '.webmanifest']);

function resolveRequest(urlPath) {
  const clean = decodeURIComponent(urlPath.split('?')[0]).replace(/^\/+/, '');
  const relative = clean === '' ? 'index.html' : clean.endsWith('/') ? `${clean}index.html` : clean;
  const target = path.resolve(ROOT, relative);
  if (!target.startsWith(`${ROOT}${path.sep}`) && target !== ROOT) return null;
  return target;
}

const server = https.createServer({
  cert: fs.readFileSync(certPath),
  key: fs.readFileSync(keyPath),
}, (req, res) => {
  const target = resolveRequest(req.url || '/');
  if (!target || !fs.existsSync(target) || !fs.statSync(target).isFile()) {
    res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
    res.end('Not found');
    return;
  }

  const ext = path.extname(target).toLowerCase();
  const type = mime.get(ext) || 'application/octet-stream';
  const acceptsGzip = /(?:^|,)\s*gzip\s*(?:,|$)/i.test(req.headers['accept-encoding'] || '');
  const useGzip = acceptsGzip && compressible.has(ext);
  const headers = {
    'content-type': type,
    // GitHub Pages serves cacheable public resources rather than no-store.
    // A short cache policy is production-representative while keeping every
    // one-run QA origin deterministic.
    'cache-control': ext === '.html' ? 'public, max-age=0, must-revalidate' : 'public, max-age=600',
  };
  if (useGzip) {
    headers['content-encoding'] = 'gzip';
    headers.vary = 'Accept-Encoding';
  }
  res.writeHead(200, headers);

  const stream = fs.createReadStream(target);
  if (useGzip) stream.pipe(zlib.createGzip({ level: 9 })).pipe(res);
  else stream.pipe(res);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`QA HTTPS server listening on https://127.0.0.1:${PORT}/`);
});

for (const signal of ['SIGTERM', 'SIGINT']) {
  process.on(signal, () => server.close(() => process.exit(0)));
}
