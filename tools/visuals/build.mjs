// Build pages: node build.mjs [name ...]   (no names = all pages in src/<domain>); domain: DOMAIN=<slug> or the domain in domain.json
import { build } from 'esbuild';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync, statSync } from 'node:fs';
import { pathToFileURL, fileURLToPath } from 'node:url';
import path from 'node:path';
import { JSDOM, VirtualConsole } from 'jsdom';

const here = path.dirname(fileURLToPath(import.meta.url));
const domain = process.env.DOMAIN || JSON.parse(readFileSync(path.join(here, 'domain.json'), 'utf8')).domain;
const srcDir = path.join(here, 'src', domain);
const dist = path.join(here, 'dist');
const outDir = path.join(here, '..', '..', 'Visuals', domain, 'html');
mkdirSync(dist, { recursive: true }); mkdirSync(outDir, { recursive: true });

const jsx = { bundle: true, jsx: 'automatic', jsxImportSource: 'preact', target: 'es2019', write: false, loader: { '.js': 'jsx' } };
let names = process.argv.slice(2);
if (!names.length) names = readdirSync(srcDir).filter((f) => f.endsWith('.jsx')).map((f) => f.replace(/\.jsx$/, ''));

// CSS compiled once for all pages (Tailwind scans src/)
const cssIn = path.join(here, 'src', 'shared', 'base.css');
const cssOut = path.join(dist, 'out.css');
execFileSync('npx', ['tailwindcss', '-i', cssIn, '-o', cssOut, '--minify'], { cwd: here, stdio: 'pipe' });
const css = readFileSync(cssOut, 'utf8');

const resultsFile = path.join(here, 'test-results.json');
const results = existsSync(resultsFile) ? JSON.parse(readFileSync(resultsFile, 'utf8')) : {};
let failed = 0;

for (const name of names) {
  const errs = [];
  try {
    const entry = path.join(srcDir, name + '.jsx');
    const client = await build({ ...jsx, minify: true, format: 'iife', platform: 'browser',
      stdin: { contents: `import { hydrate } from 'preact'; import Page from ${JSON.stringify(entry)}; hydrate(<Page />, document.getElementById('root'));`, resolveDir: here, loader: 'jsx', sourcefile: 'client.jsx' } });
    const serverFile = path.join(dist, name + '.server.mjs');
    await build({ ...jsx, write: true, format: 'esm', platform: 'node', outfile: serverFile, entryPoints: [entry], external: ['preact', 'preact/hooks', 'preact-render-to-string'] });
    const mod = await import(pathToFileURL(serverFile).href + '?t=' + Date.now());
    const { render } = await import('preact-render-to-string');
    const { h } = await import('preact');
    const Page = mod.default; const meta = mod.meta;
    const body = render(h(Page, {}));
    const script = client.outputFiles[0].text.replace(/<\/script/gi, '<\\/script');
    const html = `<!doctype html>\n<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${meta.title}</title><meta name="description" content="${(meta.lead || '').replace(/"/g, '&quot;')}"><style>${css}</style></head><body><div id="root">${body}</div><script>${script}</script></body></html>`;
    // static checks
    if (/(src|href)=["']https?:/i.test(html) || /url\(\s*["']?https?:/i.test(css) || /<script[^>]+src=/i.test(html)) errs.push('external reference');
    if (/\bfetch\s*\(|XMLHttpRequest|[^.\w]import\s*\(/.test(script)) errs.push('forbidden API');
    if (Buffer.byteLength(html) > 400 * 1024) errs.push('over 400 KB');
    if (!/<h1[ >]/.test(body) || !/<main/.test(body)) errs.push('static h1/main missing');
    if (!css.includes('scroll-behavior') || !css.includes('prefers-reduced-motion')) errs.push('css scroll/motion');
    if (!html.includes("Educational aid; verify against current standards")) errs.push('notice missing');
    // logic tests
    let testsRun = 0;
    if (mod.tests) for (const t of mod.tests) { testsRun++; try { const ok = t(); if (ok !== true) errs.push('test failed: ' + (t.name || testsRun)); } catch (e) { errs.push('test threw: ' + e.message); } }
    // jsdom load
    const vc = new VirtualConsole(); const runtime = [];
    vc.on('jsdomError', (e) => runtime.push(String(e.message || e))); vc.on('error', (e) => runtime.push(String(e)));
    const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc, url: 'http://localhost/' });
    await new Promise((r) => setTimeout(r, 60));
    {
      const doc = dom.window.document; const w = dom.window;
      for (const r of doc.querySelectorAll('input[type=range]')) {
        for (const v of [r.max, r.min]) { r.value = v; r.dispatchEvent(new w.Event('input', { bubbles: true })); await new Promise((x) => setTimeout(x, 5)); }
      }
      for (const b of Array.from(doc.querySelectorAll('button:not([disabled])')).slice(0, 60)) { b.dispatchEvent(new w.MouseEvent('click', { bubbles: true })); await new Promise((x) => setTimeout(x, 2)); }
      for (const c of doc.querySelectorAll('input[type=checkbox]')) { c.dispatchEvent(new w.MouseEvent('click', { bubbles: true })); }
      for (const sel of doc.querySelectorAll('select')) { sel.selectedIndex = sel.options.length - 1; sel.dispatchEvent(new w.Event('change', { bubbles: true })); }
      await new Promise((x) => setTimeout(x, 20));
      if (!doc.querySelector('#root h1')) errs.push('h1 lost after interaction');
    }
    if (mod.smoke) { try { await mod.smoke(dom.window.document, dom.window); await new Promise((r) => setTimeout(r, 30)); } catch (e) { errs.push('smoke: ' + e.message); } }
    if (runtime.length) errs.push('runtime: ' + runtime[0]);
    const file = path.join(outDir, (meta.file || name) + '.html');
    if (!errs.length) writeFileSync(file, html);
    results[name] = { pass: errs.length === 0, errors: errs, bytes: Buffer.byteLength(html), tests: testsRun, hasSmoke: !!mod.smoke };
  } catch (e) { errs.push('build: ' + (e.message || e)); results[name] = { pass: false, errors: errs }; }
  if (errs.length) { failed++; console.log('FAIL', name, errs.join(' | ')); } else console.log('ok  ', name, results[name].bytes + ' B');
}
writeFileSync(resultsFile, JSON.stringify(results, null, 1));
process.exit(failed ? 1 : 0);
