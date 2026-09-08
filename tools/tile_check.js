// 事例9本の FV と結果タイルの「3行落ち・はみ出し」と、見出しの「4行以上・PC で想定行数と違う・文節の途中で折返し」を検査し、切り出し画像を出す: node tools/tile_check.js <playwright-core> <headless-shell> <baseUrl> <outDir> [幅=1280] [noshot]
const path = require('path');
const [, , pwDir, exe, base, outDir, W = '1280', noshot = ''] = process.argv;
const { chromium } = require(pwDir);
(async () => {
  const b = await chromium.launch({ executablePath: exe });
  const p = await b.newPage({ viewport: { width: parseInt(W, 10), height: 900 } });
  const report = [];
  for (let i = 1; i <= 9; i++) {
    const n = String(i).padStart(2, '0');
    await p.goto(`${base}/cases/case-${n}.html`, { waitUntil: 'load' });
    await p.evaluate(() => document.querySelectorAll('.fi').forEach(e => { e.style.opacity = '1'; e.style.transform = 'none'; }));
    await p.waitForTimeout(300);
    const r = await p.evaluate(() => {
      const out = [];
      document.querySelectorAll('.kp b, .num b').forEach(e => {
        const lh = parseFloat(getComputedStyle(e).lineHeight); const lines = Math.round(e.getBoundingClientRect().height / lh);
        if (lines > 2) out.push('3行+: ' + e.textContent.trim());
        if (e.scrollWidth > e.clientWidth + 1) out.push('はみ出し: ' + e.textContent.trim());
      });
      const h = document.querySelector('.chero h1');
      if (h) {
        const lh = parseFloat(getComputedStyle(h).lineHeight); const lines = Math.round(h.getBoundingClientRect().height / lh);
        if (lines > 3) out.push('見出し4行+: ' + h.textContent.trim());
        if (window.innerWidth >= 1200) { const n = h.querySelectorAll('br.hb').length + 1; if (lines !== n) out.push('見出し: PCで' + lines + '行（想定' + n + '）'); }
        h.querySelectorAll('.seg').forEach(s => { if (Math.round(s.getBoundingClientRect().height / lh) > 1) out.push('見出し文節内で折返し: ' + s.textContent); });
      }
      return out;
    });
    report.push(`case-${n}: ${r.length ? r.join(' / ') : 'ok'}`);
    if (!noshot) await p.locator('.chero').screenshot({ path: path.join(outDir, `fv-${n}.png`) });
    if (!noshot) await p.locator('#result .nums').screenshot({ path: path.join(outDir, `res-${n}.png`) });
  }
  await b.close();
  console.log(report.join('\n'));
})().catch(e => { console.error(e); process.exit(1); });
