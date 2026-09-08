// usage: node render.js <playwright-core dir> <chrome-headless-shell> <html path or url> <out.png> [wait ms] [check]
const path = require('path');
const [, , pwDir, exe, src, out, waitMs = '1500', check = '', clipY = '0', clickText = ''] = process.argv;
const cy = parseInt(clipY, 10);
const { chromium } = require(pwDir);
(async () => {
  const browser = await chromium.launch({ executablePath: exe });
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 + cy }, deviceScaleFactor: 1 });
  const url = src.startsWith('http') ? src : 'file://' + path.resolve(src);
  await page.goto(url, { waitUntil: 'load' });
  if (clickText) { await page.click('text=' + clickText); }
  await page.waitForTimeout(parseInt(waitMs, 10));
  if (check) {
    const r = await page.evaluate(() => {
      const bad = [];
      const els = [...document.querySelectorAll('.box, .lane-label, .title, .meta, .legend, .note')];
      for (const el of els) {
        if (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1) bad.push('overflow:' + (el.textContent || '').trim().slice(0, 20));
        const r = el.getBoundingClientRect();
        if (r.right > innerWidth + 0.5 || r.bottom > innerHeight + 0.5) bad.push('outside:' + (el.textContent || '').trim().slice(0, 20));
      }
      const labels = [...document.querySelectorAll('.box')].map(e => e.textContent.trim());
      const dup = labels.filter((l, i) => labels.indexOf(l) !== i);
      if (dup.length) bad.push('dup:' + dup.join('|'));
      const curves = (document.body.innerHTML.match(/ d="[^"]*[CSQ][^"]*"/g) || []).length;
      return { bad, curves, docW: document.documentElement.scrollWidth, docH: document.documentElement.scrollHeight };
    });
    console.log('check', JSON.stringify(r));
  }
  await page.screenshot({ path: out, clip: { x: 0, y: cy, width: 1600, height: 900 } });
  await browser.close();
  console.log('wrote', out);
})().catch(e => { console.error(e); process.exit(1); });
