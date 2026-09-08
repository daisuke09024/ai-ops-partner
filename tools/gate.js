// LP の機械ゲート（はみ出し・画像の歪み・リンク切れ）を index＋事例9本×2幅で一括実行する。
// 使い方: cd <LP> && python3 -m http.server 8769 &  →  node tools/gate.js <playwright-core のパス> <出力ディレクトリ> [<headless shell の実行ファイル>]
// 例: node tools/gate.js ~/.npm/_npx/<hash>/node_modules/playwright-core /tmp/gate ~/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell
// 出力: 20行（ov=はみ出し・broken=読めない画像・distort=歪み）と、index/case-01/05/09 の全景スクショ
const PW = process.argv[2]; const OUT = process.argv[3];
const {chromium} = require(PW);
const pages = ['index.html', ...Array.from({length: 9}, (_, i) => `cases/case-0${i + 1}.html`)];
const shots = new Set(['index.html', 'cases/case-01.html', 'cases/case-05.html', 'cases/case-09.html']);
const gate = async () => {
  document.querySelectorAll('.fi').forEach(e => e.classList.add('vis'));
  const h = document.documentElement.scrollHeight;
  for (let y = 0; y < h; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
  window.scrollTo(0, h); await new Promise(r => setTimeout(r, 900)); window.scrollTo(0, 0);
  const imgs = [...document.querySelectorAll('img')].filter(i => i.getAttribute('src'));
  await Promise.all(imgs.map(i => i.complete ? null : new Promise(r => { i.onload = r; i.onerror = r; setTimeout(r, 6000); })));
  const d = document.documentElement;
  const out = {sw: d.scrollWidth, w: innerWidth, overflow: d.scrollWidth > innerWidth, h: d.scrollHeight, broken: [], distort: [], overflowEls: []};
  imgs.forEach(i => {
    if (!i.complete || i.naturalWidth === 0) { out.broken.push(i.getAttribute('src')); return; }
    const r = i.getBoundingClientRect(); if (r.width < 10) return;
    const cs = getComputedStyle(i); if (cs.objectFit === 'cover' || cs.objectFit === 'contain') return;
    const nat = i.naturalWidth / i.naturalHeight, ren = r.width / r.height;
    if (Math.abs(nat - ren) / nat > 0.03) out.distort.push(i.getAttribute('src') + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
  });
  document.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect(); if (r.right > innerWidth + 1 && r.width > 0) out.overflowEls.push(e.tagName + '.' + e.className); });
  const v = document.querySelector('video'); out.video = v ? v.readyState : null;
  return out;
};
(async () => {
  const browser = await chromium.launch(process.argv[4] ? {executablePath: process.argv[4]} : {});
  const res = [];
  for (const w of [1280, 375]) {
    const ctx = await browser.newContext({viewport: {width: w, height: w === 1280 ? 800 : 812}});
    const page = await ctx.newPage();
    for (const p of pages) {
      await page.goto('http://localhost:8769/' + p, {waitUntil: 'load'});
      const r = await page.evaluate(gate);
      res.push({p, w, ov: r.overflow, h: r.h, broken: r.broken, distort: r.distort, ovEls: r.overflowEls.slice(0, 4), video: r.video});
      if (shots.has(p)) await page.screenshot({path: `${OUT}/${p.replace('cases/', '').replace('.html', '')}_${w}.jpg`, fullPage: true, type: 'jpeg', quality: 85});
    }
    await ctx.close();
  }
  await browser.close();
  for (const r of res) console.log(`${r.p} @${r.w}: ov=${r.ov} h=${r.h} broken=${r.broken.length}${r.broken.length ? ' ' + r.broken.slice(0, 3).join(',') : ''} distort=${r.distort.length}${r.distort.length ? ' ' + r.distort.slice(0, 2).join(',') : ''}${r.ovEls.length ? ' OVER:' + r.ovEls.join('|') : ''} video=${r.video}`);
})().catch(e => { console.error('ERR', e.message.split('\n')[0]); process.exit(1); });
