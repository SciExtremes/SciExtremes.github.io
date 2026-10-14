/* Real rendering tests. Requests are served from build bytes; third-party services are blocked. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium, firefox, webkit } = require('playwright');
const root = path.resolve(process.env.TEST_SITE_DIR || 'public');
const output = process.env.TEST_SCREENSHOTS ? path.resolve(process.env.TEST_SCREENSHOTS) : null;
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const canonical = html.match(/rel=\"?canonical\"?[^>]*href=["']?([^\s"'>]+)/) || html.match(/href=["']([^"']+)["'][^>]*rel=["']canonical/);
const base = canonical ? new URL(canonical[1]).pathname : '/';
const origin = 'http://site.test';
const engines = { chromium, firefox, webkit };
const names = (process.env.TEST_BROWSERS || 'chromium').split(',');
const widths = [320, 390, 520, 521, 760, 761, 768, 1000, 1001, 1024, 1279, 1280, 1440, 1920];
function attributes(tag) {
  const result = {};
  for (const match of tag.matchAll(/([\w-]+)=(?:"([^"]*)"|'([^']*)'|([^\s>]+))/g)) result[match[1]] = match[2] ?? match[3] ?? match[4];
  return result;
}
const navMarkup = html.match(/<nav\b[^>]*\bid=["']?primary-nav["']?[^>]*>([\s\S]*?)<\/nav>/)?.[1];
assert.ok(navMarkup, 'built homepage needs primary navigation');
const sections = ['', ...[...navMarkup.matchAll(/<a\b[^>]*>/g)].map(match => new URL(attributes(match[0]).href, origin).pathname.slice(base.length))];
const languages = [...new Set((html.match(/<link\b[^>]*>/g) || []).map(attributes).filter(link => link.rel === 'alternate' && link.hreflang).map(link => new URL(link.href).pathname.slice(base.length)))];
assert.ok(languages.length, 'built homepage needs language alternatives');
const routes = languages.flatMap(lang => sections.map(section => lang + section));
const mime = { '.html':'text/html', '.css':'text/css', '.js':'application/javascript', '.mjs':'application/javascript', '.wasm':'application/wasm', '.json':'application/json', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp', '.svg':'image/svg+xml', '.gif':'image/gif', '.pdf':'application/pdf' };
let count = 0;

async function mount(context) {
  await context.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.origin !== origin) return route.abort();
    const relative = decodeURIComponent(url.pathname).replace(new RegExp('^' + base.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')), '');
    let file = path.resolve(root, relative);
    if (!file.startsWith(root + path.sep) && file !== root) return route.fulfill({ status: 403, body: 'Forbidden' });
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (!fs.existsSync(file)) return route.fulfill({ status: 404, body: 'Not found' });
    await route.fulfill({ body: fs.readFileSync(file), contentType: mime[path.extname(file)] || 'application/octet-stream' });
  });
}

async function checkLayout(page, label) {
  const problems = await page.evaluate(() => {
    const width = document.documentElement.clientWidth;
    const issues = [];
    if (document.documentElement.scrollWidth > width + 1) { issues.push('page horizontal overflow'); for(const el of document.querySelectorAll('main *')) { const r=el.getBoundingClientRect(); if(r.width&&r.right>width+1) issues.push(el.tagName+'.'+el.className+': right='+Math.round(r.right)); } }
    const selectors = 'main h1,main h2,main h3,.authors,.button,.scientific-question,.framework-stage,.timeline';
    for (const el of document.querySelectorAll(selectors)) {
      const rect = el.getBoundingClientRect();
      if (!rect.width || !rect.height) continue;
      if (rect.left < -1 || rect.right > width + 1) issues.push(`${el.className || el.tagName}: outside viewport`);
      if (el.scrollWidth > el.clientWidth + 2 && !el.matches('.prose pre,.prose table')) issues.push(`${el.className || el.tagName}: clipped content`);
    }
    return [...new Set(issues)];
  });
  assert.deepEqual(problems, [], label + ': ' + problems.join(', '));
  count += 1;
}

async function navigate(page, route) {
  await page.goto(origin + base + route, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    for (const img of document.images) img.loading = 'eager';
    await Promise.race([Promise.all([...document.images].map(img => img.decode().catch(() => {}))), new Promise(resolve => setTimeout(resolve, 3000))]);
  });
}

(async () => {
  if (output) fs.mkdirSync(output, { recursive: true });
  for (const name of names) {
    assert.ok(engines[name], 'unknown browser: ' + name);
    const options = { headless: true };
    const browser = await engines[name].launch(options);
    const deadline = setTimeout(() => { console.error(name+": browser check exceeded 10 minutes"); process.exit(1); }, 600000);
    try {
      const context = await browser.newContext({ reducedMotion: 'reduce', serviceWorkers: 'block' });
      await mount(context);
      const page = await context.newPage();
      const scriptErrors = [];
      page.on('pageerror', error => scriptErrors.push(error.message));
      for (const route of routes) {
        for (const width of widths) {
          await page.setViewportSize({ width, height: 900 });
          await navigate(page, route);
          await checkLayout(page, `${name} ${route || '/'} ${width}`);
          if (output && [390,768,1440].includes(width)) await page.screenshot({ path: path.join(output, `${name}-${route.replace(/\//g,'_') || 'home'}-${width}.png`), fullPage: true, animations: 'disabled' });
        }
        console.log(`${name}: viewports passed ${route || '/'}`);
      }
      // Every detail page is exercised at phone, tablet and desktop widths.
      const details = [];
      function walk(dir) { for (const entry of fs.readdirSync(dir, { withFileTypes: true })) { const file = path.join(dir,entry.name); if(entry.isDirectory()) walk(file); else if(entry.name==='index.html') { const relative=path.relative(root,file).replaceAll(path.sep,'/').replace(/index.html$/,''); if(!routes.includes(relative)) details.push(relative); } } }
      walk(root);
      for (const route of details) for (const width of [390,768,1440]) {
        await page.setViewportSize({ width, height:900 }); await navigate(page, route); await checkLayout(page,`${name} detail ${route} ${width}`);
      }
      for (const lang of languages) {
        await page.setViewportSize({ width:390, height:844 });
        await navigate(page, lang + sections[1]);
        const query = (await page.locator('main h1').innerText()).trim();
        await navigate(page, lang);
        const menu = page.locator('#menu-toggle');
        await menu.click(); assert.equal(await menu.getAttribute('aria-expanded'), 'true');
        await page.keyboard.press('Escape'); assert.equal(await menu.getAttribute('aria-expanded'), 'false');
        assert.ok(await menu.evaluate(el => el === document.activeElement));
        await page.locator('[data-search-open]').click();
        await page.locator('#search-results input').waitFor();
        await page.locator('#search-results input').fill(query);
        await page.locator('.pagefind-ui__result-link').first().waitFor();
        const resultUrl = await page.locator('.pagefind-ui__result-link').first().getAttribute('href');
        assert.ok(resultUrl.includes(base + lang), 'search must preserve language/base path');
        await page.keyboard.press('Escape'); assert.equal(await page.locator('#search-dialog').evaluate(el=>el.open),false);
        for (const route of sections) {
          await navigate(page, lang + route);
          // Text-only enlargement stresses content growth independently of viewport resizing.
          await page.evaluate(() => { const sizes=[...document.querySelectorAll('body,body *:not(svg):not(svg *)')].map(el=>[el,parseFloat(getComputedStyle(el).fontSize)]); for(const [el,size] of sizes) el.style.fontSize=(size*2)+'px'; });
          await checkLayout(page,`${name} text enlargement ${lang+route}`);
        }
      }
      await page.setViewportSize({ width:844, height:390 }); await navigate(page,(languages.find(lang=>lang) || '')+sections[1]); await checkLayout(page,`${name} phone landscape`);
      assert.deepEqual(scriptErrors, [], 'uncaught browser script errors');
      await context.close();
      // Navigation remains usable with JavaScript disabled.
      const plain = await browser.newContext({ javaScriptEnabled:false, viewport:{ width:390,height:844 } });
      await mount(plain); const nojs = await plain.newPage(); await nojs.goto(origin+base);
      assert.equal(await nojs.locator('#primary-nav a:visible').count(),sections.length-1); await plain.close();
      if (name !== 'firefox') for (const width of [320,390,768]) {
        const touch = await browser.newContext({ isMobile:true, hasTouch:true, deviceScaleFactor:2, viewport:{width,height:844} });
        await mount(touch); const phone = await touch.newPage(); await phone.goto(origin+base+'zh/');
        await phone.locator('#menu-toggle').tap(); assert.equal(await phone.locator('#menu-toggle').getAttribute('aria-expanded'),'true');
        await phone.locator('#menu-toggle').tap(); await phone.locator('[data-search-open]').tap(); await phone.locator('#search-results input').waitFor();
        assert.ok(await phone.locator('#search-dialog').evaluate(el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.height<=innerHeight+1;}));
        await touch.close();
      }
      console.log(`${name}: passed (${await browser.version()})`);
    } finally { clearTimeout(deadline); await browser.close(); }
  }
  console.log(`Browser OK: ${count} layout checks; menus, actual search, enlarged text and no-JS navigation.`);
})().catch(error => { console.error(error); process.exitCode=1; });
