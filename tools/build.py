#!/usr/bin/env python3
"""LP の生成器。tools/cases.json から index.html（事例のまとめ＝ポートフォリオ）と cases/case-NN.html（事例9本）を書き出す。

使い方:
  python3 tools/build.py            # index.html と cases/*.html を全部作り直す
  python3 tools/build.py --check    # 生成せず、素材（図解・動画）の欠けだけ報告する

ページの本文は cases.json が正（文言を直す時は HTML ではなく JSON を直してから build する）。
CSS はこのファイルの中に1本だけ持ち、各 HTML に埋め込む（ページ単体で自己完結させるため）。
"""
import argparse, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))
SITE = "https://ai-ops-partner.vercel.app"
TALLY = "https://tally.so/r/QKdxx1"
BRAND = "AI業務改革パートナー"

def esc(s):
    return html.escape(str(s), quote=True)

# ------------------------------------------------------------------ CSS
CSS = r"""
:root{
  --c:1200px;
  --bg:#fafbfe;--bg2:#f1f4f9;--bg3:#e8edf5;--card:#fff;
  --dark:#0c1222;--dark2:#1a2240;
  --tx:#111827;--tx2:#4b5563;--tx3:#6b7280;
  --blue:#2563eb;--blue-d:#1d4ed8;--blue-l:#60a5fa;--blue-bg:rgba(37,99,235,.06);--blue-bg2:rgba(37,99,235,.12);
  --amber:#b45309;--amber-bg:rgba(217,119,6,.10);
  --rose:#be123c;--rose-bg:rgba(225,29,72,.07);
  --green:#047857;--green-bg:rgba(5,150,105,.09);
  --violet:#6d28d9;--violet-bg:rgba(109,40,217,.08);
  --border:#e5e7eb;--border2:#d1d5db;
  --sh:0 1px 3px rgba(0,0,0,.06);--sh2:0 6px 24px rgba(15,23,42,.08);--sh3:0 16px 48px rgba(15,23,42,.14);
  --r:14px;--r2:20px;
  --tr:.25s cubic-bezier(.4,0,.2,1);
  --fj:'Zen Kaku Gothic New',sans-serif;--fe:'Plus Jakarta Sans',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:var(--fj);background:var(--bg);color:var(--tx);line-height:1.85;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,video{max-width:100%;height:auto;display:block}
a{color:inherit}
.w{max-width:var(--c);margin:0 auto;padding:0 clamp(20px,4vw,48px)}
.sec{padding:clamp(56px,8vw,96px) 0}
.eyebrow{font-family:var(--fe);font-size:.78rem;font-weight:700;letter-spacing:.14em;color:var(--blue);text-transform:uppercase;display:flex;align-items:center;gap:10px;margin-bottom:12px}
.eyebrow::before{content:'';width:22px;height:2px;background:var(--blue);border-radius:2px}
.h2{font-size:clamp(1.5rem,3.4vw,2.1rem);font-weight:900;line-height:1.4;letter-spacing:-.02em;margin-bottom:12px}
.lead{font-size:1rem;color:var(--tx2);max-width:760px}
.sec-head{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;margin-bottom:32px;flex-wrap:wrap}
.count{font-family:var(--fe);font-weight:800;color:var(--blue);font-size:1.4rem;white-space:nowrap}
.count small{font-family:var(--fj);font-size:.85rem;color:var(--tx3);font-weight:500;margin-left:4px}

/* header */
.hd{position:fixed;top:0;left:0;right:0;z-index:999;background:rgba(250,251,254,.9);backdrop-filter:blur(16px) saturate(1.4);border-bottom:1px solid rgba(0,0,0,.05)}
.hd-in{display:flex;align-items:center;justify-content:space-between;height:64px;max-width:var(--c);margin:0 auto;padding:0 clamp(20px,4vw,48px)}
.hd-logo{font-size:1rem;font-weight:900;color:var(--tx);text-decoration:none;display:flex;align-items:center;gap:8px;white-space:nowrap}
.hd-logo span{color:var(--blue)}
.hd-logo i{width:8px;height:8px;background:var(--blue);border-radius:50%;display:inline-block}
.hd-nav{display:flex;align-items:center;gap:26px}
.hd-nav a{font-size:.88rem;color:var(--tx2);text-decoration:none;font-weight:600;transition:var(--tr)}
.hd-nav a:hover{color:var(--tx)}
.hd-cta{background:var(--blue)!important;color:#fff!important;padding:9px 20px!important;border-radius:10px;font-weight:700!important;font-size:.84rem!important;box-shadow:0 2px 8px rgba(37,99,235,.25)}
.hd-cta:hover{background:var(--blue-d)!important;transform:translateY(-1px)}
.hd-back{font-size:.86rem;color:var(--tx2);text-decoration:none;font-weight:600;display:inline-flex;align-items:center;gap:6px}
.hd-back:hover{color:var(--blue)}
@media(max-width:640px){.hd-nav a:not(.hd-cta){display:none}.hd-nav{gap:12px}}
.progress{position:fixed;top:64px;left:0;height:3px;width:0;background:linear-gradient(90deg,var(--blue),var(--blue-l));z-index:998;transition:width .1s linear}

/* buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:14px 30px;border-radius:12px;font-size:.95rem;font-weight:700;text-decoration:none;transition:var(--tr);cursor:pointer;border:0;font-family:var(--fj);line-height:1.4}
.btn-p{background:var(--blue);color:#fff;box-shadow:0 4px 16px rgba(37,99,235,.28)}
.btn-p:hover{background:var(--blue-d);transform:translateY(-2px);box-shadow:0 8px 24px rgba(37,99,235,.35)}
.btn-o{background:rgba(255,255,255,.75);color:var(--tx2);border:1px solid var(--border2)}
.btn-o:hover{background:#fff;color:var(--tx)}
.btn-w{background:#fff;color:var(--blue-d)}
.btn-w:hover{background:#eef2ff;transform:translateY(-2px)}

/* badges */
.bd{display:inline-flex;align-items:center;gap:6px;padding:4px 11px;border-radius:100px;font-size:.76rem;font-weight:700;line-height:1.5;white-space:nowrap}
.bd-site{background:var(--violet-bg);color:var(--violet)}
.bd-cat{background:var(--bg2);color:var(--tx2)}
.bd-video{background:var(--tx);color:#fff}
.bd-video::before{content:'▶';font-size:.62rem}
.bd-soon{background:var(--bg2);color:var(--tx3)}
.bd-ext{background:var(--amber-bg);color:var(--amber)}
.bd-live{background:var(--green-bg);color:var(--green)}
.bd-live::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}

/* ===== index: hero ===== */
.hero{padding:calc(64px + clamp(48px,7vw,88px)) 0 clamp(48px,6vw,72px);position:relative;overflow:hidden;background:linear-gradient(135deg,#f0f4ff 0%,#e6edff 35%,#f6f3ff 70%,#fafbfe 100%)}
.hero::before{content:'';position:absolute;top:-30%;right:-10%;width:60vw;height:60vw;max-width:820px;max-height:820px;background:radial-gradient(circle,rgba(37,99,235,.10) 0%,transparent 70%);pointer-events:none}
.hero-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:clamp(28px,5vw,72px);align-items:center;position:relative;z-index:1}
.hero h1{font-size:clamp(1.9rem,4.6vw,3rem);font-weight:900;line-height:1.3;letter-spacing:-.03em;margin:8px 0 18px}
.hero h1 em{font-style:normal;color:var(--blue)}
.hero-lead{font-size:1.02rem;color:var(--tx2);margin-bottom:28px;max-width:560px}
.hero-btns{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:36px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.st{padding:14px 10px;background:rgba(255,255,255,.75);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.9);border-radius:var(--r);box-shadow:0 2px 8px rgba(0,0,0,.04);text-align:center;display:flex;flex-direction:column;justify-content:center}
.st-n{font-family:var(--fe);font-size:clamp(1.3rem,2.2vw,1.7rem);font-weight:800;color:var(--blue);line-height:1.2;letter-spacing:-.02em;white-space:nowrap}
.st-n small{font-size:.6em;font-weight:700;margin-left:2px}
.st-l{font-size:.76rem;color:var(--tx3);margin-top:3px;line-height:1.4}
.hero-vid{position:relative;width:100%;max-width:560px;justify-self:end;padding:12px;background:rgba(255,255,255,.85);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.95);border-radius:var(--r2);box-shadow:var(--sh3)}
.hero-vid-fr{position:relative;aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:var(--bg3)}
.hero-vid-fr video,.hero-vid-fr img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hero-vid-fr img.still{display:none}
.hero-vid-cap{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:4px 12px;margin:10px 4px 0}
.hero-vid-cap b{font-size:.84rem;font-weight:700}
.hero-vid-cap span{font-size:.74rem;color:var(--tx3)}
@media(prefers-reduced-motion:reduce){.hero-vid-fr video{display:none}.hero-vid-fr img.still{display:block}}
@media(max-width:900px){.hero-grid{grid-template-columns:1fr}.hero-vid{justify-self:stretch;max-width:100%}.stats{grid-template-columns:repeat(2,1fr)}}

/* 読み方の帯 */
.rules{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:clamp(28px,4vw,40px)}
.rule{display:flex;gap:12px;align-items:flex-start;padding:16px 18px;background:rgba(255,255,255,.6);border:1px solid rgba(37,99,235,.10);border-radius:var(--r);font-size:.88rem;color:var(--tx2);line-height:1.7}
.rule b{color:var(--tx);display:block;font-size:.9rem}
.rule i{flex-shrink:0;width:28px;height:28px;border-radius:8px;background:var(--blue-bg2);color:var(--blue);font-style:normal;font-family:var(--fe);font-weight:800;font-size:.8rem;display:flex;align-items:center;justify-content:center}
@media(max-width:768px){.rules{grid-template-columns:1fr}}

/* filters */
.filters{display:flex;flex-direction:column;gap:10px;margin-bottom:28px}
.frow{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.frow .flb{font-size:.78rem;color:var(--tx3);font-weight:700;margin-right:4px;white-space:nowrap}
.chip{border:1px solid var(--border);background:#fff;color:var(--tx2);padding:7px 14px;border-radius:100px;font-size:.84rem;font-weight:600;cursor:pointer;font-family:var(--fj);transition:var(--tr);display:inline-flex;align-items:center;gap:6px}
.chip small{font-family:var(--fe);font-size:.72rem;color:var(--tx3);font-weight:700}
.chip:hover{border-color:var(--blue);color:var(--blue)}
.chip.on{background:var(--tx);color:#fff;border-color:var(--tx)}
.chip.on small{color:rgba(255,255,255,.7)}

/* case cards */
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
@media(max-width:1000px){.grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){.grid{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r2);overflow:hidden;display:flex;flex-direction:column;text-decoration:none;color:inherit;transition:var(--tr);position:relative}
.card:hover{transform:translateY(-4px);box-shadow:var(--sh2);border-color:#cbd5e1}
.card.hide{display:none}
.thumb{position:relative;aspect-ratio:16/9;background:var(--bg3);overflow:hidden}
.thumb img{width:100%;height:100%;object-fit:cover;object-position:top;transition:transform .5s ease}
.card:hover .thumb img{transform:scale(1.03)}
.cbody{padding:18px 20px 20px;display:flex;flex-direction:column;flex:1}
.cmeta{display:flex;align-items:center;gap:8px;font-family:var(--fe);font-size:.74rem;font-weight:700;color:var(--tx3);letter-spacing:.06em;margin-bottom:8px}
.cmeta .cat{font-family:var(--fj);letter-spacing:0;font-weight:600;color:var(--tx2)}
.cmeta .cat::before{content:'·';margin-right:8px;color:var(--border2)}
.cbds{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.card h3{font-size:1.06rem;font-weight:800;line-height:1.55;margin-bottom:8px;letter-spacing:-.01em}
.card p{font-size:.9rem;color:var(--tx2);line-height:1.7;margin-bottom:14px;flex:1}
.kpi{background:var(--blue-bg);border:1px solid rgba(37,99,235,.10);border-radius:12px;padding:10px 14px;margin-bottom:12px}
.kpi small{display:block;font-size:.74rem;color:var(--tx3);font-weight:600}
.kpi b{font-family:var(--fe);font-size:1.05rem;font-weight:800;color:var(--blue-d);letter-spacing:-.01em;line-height:1.35;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.kpi b .ar{color:var(--tx3);font-weight:400}
.kpi b .old{color:var(--tx3);text-decoration:line-through;text-decoration-color:var(--rose);font-weight:700}
.kpi .sub{font-size:.78rem;color:var(--tx2);font-weight:500;font-family:var(--fj);margin-top:2px}
.more{font-size:.86rem;color:var(--blue);font-weight:700;display:inline-flex;align-items:center;gap:4px;transition:var(--tr)}
.card:hover .more{gap:9px}

/* systems (一覧) */
.sgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:16px}
@media(max-width:1100px){.sgrid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:640px){.sgrid{grid-template-columns:repeat(2,1fr)}}
.scard{background:var(--card);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;cursor:zoom-in;transition:var(--tr)}
.scard:hover{box-shadow:var(--sh2);transform:translateY(-3px)}
.scard .thumb{aspect-ratio:16/9}
.sbody{padding:12px 14px 14px}
.sbody h3{font-size:.9rem;font-weight:800;line-height:1.5;margin:6px 0 4px}
.sbody p{font-size:.78rem;color:var(--tx3);line-height:1.6}

/* cta */
.cta{background:linear-gradient(135deg,#0c1222 0%,#1a2240 55%,#0f172a 100%);color:#fff;text-align:center;padding:clamp(64px,9vw,104px) 0;position:relative;overflow:hidden}
.cta::before{content:'';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:640px;height:640px;background:radial-gradient(circle,rgba(37,99,235,.16) 0%,transparent 70%);pointer-events:none}
.cta .w{position:relative;z-index:1}
.cta h2{font-size:clamp(1.4rem,3.6vw,2.2rem);font-weight:900;line-height:1.4;margin-bottom:14px}
.cta p{color:rgba(255,255,255,.66);font-size:1rem;max-width:640px;margin:0 auto 28px}
.cta .note{font-size:.8rem;color:rgba(255,255,255,.45);margin-top:14px}
.ft{padding:36px 0;border-top:1px solid rgba(0,0,0,.05);text-align:center;background:var(--bg)}
.ft-links{display:flex;justify-content:center;gap:24px;margin-bottom:12px;flex-wrap:wrap}
.ft-links a{font-size:.84rem;color:var(--tx3);text-decoration:none}
.ft-links a:hover{color:var(--tx2)}
.ft-copy{font-size:.75rem;color:var(--tx3)}

/* lightbox */
.lb{position:fixed;inset:0;background:rgba(12,18,34,.88);z-index:2000;display:none;align-items:center;justify-content:center;padding:24px;cursor:zoom-out}
.lb.on{display:flex}
.lb img{max-width:min(1600px,96vw);max-height:92vh;width:auto;height:auto;border-radius:10px;box-shadow:var(--sh3);background:#fff}
.lb-cap{position:absolute;bottom:18px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,.75);font-size:.82rem;white-space:nowrap}
.zoomable{cursor:zoom-in}

/* ===== case page ===== */
.chero{padding:calc(64px + clamp(36px,5vw,56px)) 0 clamp(36px,5vw,56px);background:linear-gradient(135deg,#f0f4ff 0%,#e9efff 45%,#fafbfe 100%);position:relative;overflow:hidden}
.chero::before{content:'';position:absolute;top:-40%;right:-10%;width:52vw;height:52vw;max-width:700px;max-height:700px;background:radial-gradient(circle,rgba(37,99,235,.10) 0%,transparent 70%);pointer-events:none}
.crumb{font-size:.8rem;color:var(--tx3);display:flex;gap:8px;align-items:center;margin-bottom:16px;font-weight:600}
.crumb a{color:var(--tx3);text-decoration:none}
.crumb a:hover{color:var(--blue)}
.crumb .cur{color:var(--blue);font-family:var(--fe);letter-spacing:.08em}
.chero-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:clamp(28px,5vw,64px);align-items:center;position:relative;z-index:1}
.chero .bds{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.chero h1{font-size:clamp(1.6rem,3.8vw,2.5rem);font-weight:900;line-height:1.38;letter-spacing:-.025em;margin-bottom:16px}
.chero .lead{margin-bottom:24px}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;max-width:640px}
.kp{padding:12px 14px;background:rgba(255,255,255,.85);border:1px solid rgba(255,255,255,.9);border-radius:var(--r);box-shadow:0 2px 8px rgba(0,0,0,.04)}
.kp small{display:block;font-size:.72rem;color:var(--tx3);font-weight:600;line-height:1.4}
.kp b{display:block;font-family:var(--fe);font-size:clamp(1rem,1.7vw,1.3rem);font-weight:800;color:var(--blue-d);line-height:1.3;letter-spacing:-.01em;margin-top:3px}
.kp b .ja{font-family:var(--fj)}
.chero-vis{position:relative;justify-self:end;width:100%;max-width:540px}
.chero-vis a,.chero-vis .fr{display:block;position:relative;aspect-ratio:16/9;border-radius:var(--r2);overflow:hidden;background:var(--bg3);box-shadow:var(--sh3);border:6px solid #fff}
.chero-vis img{width:100%;height:100%;object-fit:cover;aspect-ratio:auto}
.play{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
.play span{width:64px;height:64px;border-radius:50%;background:rgba(255,255,255,.92);color:var(--blue);display:flex;align-items:center;justify-content:center;font-size:1.3rem;box-shadow:var(--sh3);padding-left:4px;transition:var(--tr)}
.chero-vis a:hover .play span{transform:scale(1.08)}
.vis-cap{font-size:.76rem;color:var(--tx3);margin-top:10px;text-align:center}
@media(max-width:900px){.chero-grid{grid-template-columns:1fr}.chero-vis{justify-self:stretch;max-width:100%}}
@media(max-width:640px){.kpis{grid-template-columns:1fr 1fr}}

.body{padding:clamp(40px,6vw,64px) 0}
.body-grid{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:clamp(28px,4vw,56px);align-items:start}
@media(max-width:1060px){.body-grid{grid-template-columns:1fr}.side{position:static!important}}
.blk{margin-bottom:clamp(40px,6vw,64px)}
.blk-h{display:flex;align-items:center;gap:14px;margin-bottom:18px}
.tag{flex-shrink:0;padding:6px 12px;border-radius:10px;font-size:.78rem;font-weight:800;letter-spacing:.04em;line-height:1.4}
.tag-b{background:var(--blue-bg2);color:var(--blue-d)}
.tag-r{background:var(--rose-bg);color:var(--rose)}
.tag-a{background:var(--amber-bg);color:var(--amber)}
.tag-g{background:var(--green-bg);color:var(--green)}
.tag-v{background:var(--violet-bg);color:var(--violet)}
.tag-d{background:var(--tx);color:#fff}
.blk h2{font-size:clamp(1.15rem,2.4vw,1.5rem);font-weight:800;line-height:1.45;letter-spacing:-.01em}
.blk .sub{font-size:.9rem;color:var(--tx3);margin:-10px 0 16px}
.fig{background:#fff;border:1px solid var(--border);border-radius:var(--r2);padding:10px;box-shadow:var(--sh)}
.fig img{width:100%;height:auto;aspect-ratio:16/9;border-radius:12px}
.fig-cap{font-size:.8rem;color:var(--tx3);margin-top:10px;padding:0 6px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.vid{background:var(--dark);border-radius:var(--r2);padding:10px;box-shadow:var(--sh3)}
.vid video{width:100%;border-radius:12px;aspect-ratio:16/9;background:#000}
.vid-cap{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:rgba(255,255,255,.65);font-size:.8rem;padding:10px 6px 2px}
.vid-cap b{color:#fff}
.soon{border:2px dashed var(--border2);border-radius:var(--r2);padding:28px 24px;background:var(--bg2);display:flex;gap:16px;align-items:center}
.soon i{flex-shrink:0;width:48px;height:48px;border-radius:14px;background:#fff;border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-style:normal;color:var(--tx3);font-size:1.1rem}
.soon b{display:block;font-size:.98rem;margin-bottom:4px}
.soon p{font-size:.88rem;color:var(--tx3);line-height:1.7}
.story{display:grid;grid-template-columns:1fr;gap:14px}
.sbox{border-radius:var(--r2);padding:22px 24px;border:1px solid var(--border);background:#fff;position:relative}
.sbox::before{content:'';position:absolute;left:0;top:18px;bottom:18px;width:4px;border-radius:0 4px 4px 0}
.sbox-r::before{background:var(--rose)}.sbox-b::before{background:var(--blue)}.sbox-g::before{background:var(--green)}
.sbox h3{font-size:1.05rem;font-weight:800;line-height:1.5;margin-bottom:8px;display:flex;gap:10px;align-items:baseline}
.sbox h3 .lb{position:static;display:inline-block;background:none;padding:0;font-size:.74rem;font-weight:800;letter-spacing:.08em;cursor:default}
.sbox-r h3 .lb{color:var(--rose)}.sbox-b h3 .lb{color:var(--blue)}.sbox-g h3 .lb{color:var(--green)}
.sbox p{font-size:.95rem;color:var(--tx2);line-height:1.85}
.tools{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:14px;padding-top:14px;border-top:1px dashed var(--border)}
.tools small{font-size:.76rem;color:var(--tx3);font-weight:700;margin-right:2px}
.tools span{font-size:.8rem;background:var(--bg2);color:var(--tx2);padding:4px 11px;border-radius:100px;font-weight:600}
.callout{border-radius:var(--r2);padding:22px 24px;background:linear-gradient(135deg,rgba(37,99,235,.07),rgba(109,40,217,.06));border:1px solid rgba(37,99,235,.14)}
.callout b{display:block;font-size:1rem;margin-bottom:6px}
.callout p{font-size:.95rem;color:var(--tx2)}
.incl{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:640px){.incl{grid-template-columns:1fr}}
.inc{background:#fff;border:1px solid var(--border);border-radius:var(--r);padding:18px 20px}
.inc .bd{margin-bottom:8px}
.inc h3{font-size:.98rem;font-weight:800;line-height:1.5;margin-bottom:6px}
.inc p{font-size:.86rem;color:var(--tx2);line-height:1.7}
.inc .n{font-family:var(--fe);font-weight:800;color:var(--blue-d);font-size:1.05rem}
.side{position:sticky;top:88px}
.sidebox{background:#fff;border:1px solid var(--border);border-radius:var(--r2);padding:20px 22px;margin-bottom:14px}
.sidebox h4{font-size:.92rem;font-weight:800;margin-bottom:10px}
.srow{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px solid rgba(0,0,0,.05);font-size:.84rem}
.srow:last-child{border-bottom:0}
.srow span:first-child{color:var(--tx3);flex-shrink:0}
.srow span:last-child{text-align:right;font-weight:600;color:var(--tx)}
.sidecta{background:var(--dark);color:#fff;border-radius:var(--r2);padding:22px}
.sidecta b{display:block;font-size:.98rem;margin-bottom:6px}
.sidecta p{font-size:.82rem;color:rgba(255,255,255,.65);margin-bottom:14px;line-height:1.7}
.sidecta .btn{width:100%;padding:12px 16px;font-size:.88rem}
.toc{list-style:none}
.toc li a{display:block;font-size:.84rem;color:var(--tx2);text-decoration:none;padding:6px 0 6px 12px;border-left:2px solid var(--border);transition:var(--tr)}
.toc li a:hover,.toc li a.on{color:var(--blue);border-color:var(--blue)}
.next{background:var(--bg2);padding:clamp(40px,6vw,64px) 0}
.next .h3{font-size:1.1rem;font-weight:800;margin-bottom:16px}
.ngrid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:640px){.ngrid{grid-template-columns:1fr}}
.ncard{display:flex;gap:14px;align-items:center;background:#fff;border:1px solid var(--border);border-radius:var(--r);padding:12px;text-decoration:none;color:inherit;transition:var(--tr)}
.ncard:hover{box-shadow:var(--sh2);transform:translateY(-2px)}
.ncard img{width:132px;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:8px;flex-shrink:0}
.ncard small{font-family:var(--fe);font-size:.72rem;color:var(--tx3);font-weight:700;letter-spacing:.06em}
.ncard b{display:block;font-size:.9rem;line-height:1.5;margin-top:2px}
.back{margin-top:22px}
.back a{font-size:.9rem;color:var(--blue);font-weight:700;text-decoration:none}

/* reveal */
.fi{opacity:0;transform:translateY(20px);transition:opacity .6s ease,transform .6s ease}
.fi.vis{opacity:1;transform:translateY(0)}
@media(prefers-reduced-motion:reduce){.fi{opacity:1;transform:none;transition:none}}
"""

JS_COMMON = r"""
const obs=new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('vis');obs.unobserve(x.target)}})},{threshold:.06,rootMargin:'0px 0px -40px 0px'});
document.querySelectorAll('.fi').forEach(el=>obs.observe(el));
const lb=document.getElementById('lb');if(lb){const li=lb.querySelector('img'),lc=lb.querySelector('.lb-cap');
document.querySelectorAll('.zoomable').forEach(el=>{el.addEventListener('click',ev=>{ev.preventDefault();const im=el.tagName==='IMG'?el:el.querySelector('img');li.src=im.dataset.full||im.src;li.alt=im.alt;lc.textContent=el.dataset.cap||im.alt||'';lb.classList.add('on');document.body.style.overflow='hidden'})});
const close=()=>{lb.classList.remove('on');document.body.style.overflow=''};lb.addEventListener('click',close);document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});}
(function(){var mq=window.matchMedia('(prefers-reduced-motion: reduce)');document.querySelectorAll('video[autoplay]').forEach(function(v){function ap(){if(mq.matches){v.removeAttribute('autoplay');v.pause()}else{var p=v.play();if(p&&p.catch)p.catch(function(){})}}ap();if(mq.addEventListener)mq.addEventListener('change',ap)})})();
"""

JS_INDEX = r"""
(function(){const cards=[...document.querySelectorAll('#cases .card')];const cnt=document.getElementById('ccount');
let site='all',cat='all';
function apply(){let n=0;cards.forEach(c=>{const ok=(site==='all'||c.dataset.site===site)&&(cat==='all'||c.dataset.cat===cat);c.classList.toggle('hide',!ok);if(ok)n++});cnt.textContent=n;}
document.querySelectorAll('.chip[data-site]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.chip[data-site]').forEach(x=>x.classList.remove('on'));b.classList.add('on');site=b.dataset.site;apply()}));
document.querySelectorAll('.chip[data-cat]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.chip[data-cat]').forEach(x=>x.classList.remove('on'));b.classList.add('on');cat=b.dataset.cat;apply()}));
})();
"""

JS_CASE = r"""
(function(){const bar=document.getElementById('pg');if(!bar)return;function u(){const h=document.documentElement;const p=h.scrollTop/(h.scrollHeight-h.clientHeight);bar.style.width=(Math.max(0,Math.min(1,p))*100)+'%'}document.addEventListener('scroll',u,{passive:true});u();})();
(function(){const links=[...document.querySelectorAll('.toc a')];const secs=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);if(!secs.length)return;
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){links.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id))}})},{rootMargin:'-30% 0px -60% 0px'});secs.forEach(s=>io.observe(s));})();
"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">'

def head(title, desc, url, image, extra=""):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(image)}">
<meta property="og:url" content="{esc(url)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Ccircle cx=%2716%27 cy=%2716%27 r=%2712%27 fill=%27%232563eb%27/%3E%3C/svg%3E">
{FONTS}
{extra}
<style>{CSS}</style>
</head>
<body>
"""

def header(root):
    """root: index からは '' / cases からは '../'"""
    if root == "":
        nav = f'<a href="#cases">事例</a><a href="#systems">仕組み</a><a href="{TALLY}" class="hd-cta" target="_blank" rel="noopener">無料で相談する</a>'
        left = f'<a href="#" class="hd-logo"><i></i>AI業務改革<span>パートナー</span></a>'
    else:
        nav = f'<a href="{root}index.html#cases">事例一覧</a><a href="{root}index.html#systems">仕組み</a><a href="{TALLY}" class="hd-cta" target="_blank" rel="noopener">無料で相談する</a>'
        left = f'<a href="{root}index.html" class="hd-logo"><i></i>AI業務改革<span>パートナー</span></a>'
    return f'<header class="hd"><div class="hd-in">{left}<nav class="hd-nav">{nav}</nav></div></header>'

def footer(root):
    return f"""<footer class="ft"><div class="w">
<div class="ft-links"><a href="{root}index.html#cases">事例</a><a href="{root}index.html#systems">仕組み</a><a href="{TALLY}" target="_blank" rel="noopener">お問い合わせ</a></div>
<p class="ft-copy">© 2026 {BRAND}</p></div></footer>
<div class="lb" id="lb" role="dialog" aria-label="図解を拡大"><img src="" alt=""><div class="lb-cap"></div></div>
"""

def kpi_html(face):
    """カードの数字タイル。face が before/after 型と big/sub 型の2種"""
    if "before" in face:
        sub = f'<div class="sub">{esc(face["sub"])}</div>' if face.get("sub") else ""
        return f'<div class="kpi"><small>{esc(face["label"])}</small><b><span class="old">{esc(face["before"])}</span><span class="ar">→</span>{esc(face["after"])}</b>{sub}</div>'
    return f'<div class="kpi"><small>{esc(face.get("sub",""))}</small><b>{esc(face["big"])}</b></div>'

SITE_LABELS = DATA["meta"]["site_labels"]

def case_card(c, root):
    num = c["num"]
    vid = '<span class="bd bd-video">60秒デモ</span>' if c["video"] else '<span class="bd bd-soon">図解＋成果</span>'
    return f"""<a class="card fi" href="{root}cases/case-{num}.html" data-site="{c['site']}" data-cat="{esc(c['cat'])}">
<div class="thumb"><img src="{root}cases/media/case-{num}_zukai.webp" alt="{esc(c['src_title'])}の図解" loading="lazy" width="1600" height="900"></div>
<div class="cbody"><div class="cmeta">CASE {num}<span class="cat">{esc(c['cat'])}</span></div>
<div class="cbds"><span class="bd bd-site">{esc(SITE_LABELS[c['site']])}</span>{vid}</div>
<h3>{esc(c['headline'])}</h3>
<p>{esc(c['src_problem'])}</p>
{kpi_html(c['src_face'])}
<span class="more">詳しく見る →</span></div></a>"""

def sys_card(l, root):
    ext = l.get("src_origin") == "external"
    badge = '<span class="bd bd-ext">他社の事例</span>' if ext else f'<span class="bd bd-live">{esc(l["src_status"].split("（")[0].replace("⚡ ","").replace("🧰 ","").replace("🤝 ",""))}</span>'
    return f"""<div class="scard zoomable fi" data-cap="{esc(l['src_title'])}"><div class="thumb"><img src="{root}cases/media/{l['key']}.webp" alt="{esc(l['src_title'])}の図解" loading="lazy" width="1600" height="900"></div>
<div class="sbody">{badge}<h3>{esc(l['src_title'])}</h3><p>{esc(l['src_problem'])}</p></div></div>"""

# ------------------------------------------------------------------ index
def build_index():
    cases = DATA["cases"]; lists = DATA["lists"]; meta = DATA["meta"]
    n_video = sum(1 for c in cases if c["video"])
    site_counts = {k: sum(1 for c in cases if c["site"] == k) for k in SITE_LABELS}
    cat_counts = {k: sum(1 for c in cases if c["cat"] == k) for k in meta["cats"]}
    chips_site = '<button class="chip on" data-site="all">すべて<small>9</small></button>' + "".join(
        f'<button class="chip" data-site="{k}">{esc(v)}<small>{site_counts[k]}</small></button>' for k, v in SITE_LABELS.items())
    chips_cat = '<button class="chip on" data-cat="all">すべて</button>' + "".join(
        f'<button class="chip" data-cat="{esc(k)}">{esc(k)}<small>{cat_counts[k]}</small></button>' for k in meta["cats"] if cat_counts[k])
    title = f"{BRAND}｜AIで業務を動かした事例とデモ"
    desc = "前職の45名組織・顧客の環境・自社の運用で実際に動いた（動いている）AI活用の事例9本と、日々動いている仕組み10件。数字は実測、動画は架空データで再現。"
    body = f"""{header("")}
<section class="hero"><div class="w">
<div class="hero-grid">
<div class="hero-text">
<div class="eyebrow">AI業務改革パートナー ／ 事例とデモ</div>
<h1>業務をAIに任せた、<br><em>実物の記録</em>。</h1>
<p class="hero-lead">前職の45名組織、顧客の環境、自社の運用で、実際に動いた（動いている）ものだけを載せています。口で説明する代わりに、図解と動く画面で。</p>
<div class="hero-btns"><a href="#cases" class="btn btn-p">事例を見る ↓</a><a href="{TALLY}" class="btn btn-o" target="_blank" rel="noopener">無料で相談する</a></div>
<div class="stats">
<div class="st"><div class="st-n">9</div><div class="st-l">事例</div></div>
<div class="st"><div class="st-n">{n_video}</div><div class="st-l">60秒の実演動画</div></div>
<div class="st"><div class="st-n">10</div><div class="st-l">動いている仕組み</div></div>
<div class="st"><div class="st-n">1,740<small>万円</small></div><div class="st-l">年間の削減額<br>（前職3事例の合計）</div></div>
</div>
</div>
<div class="hero-vid fi">
<div class="hero-vid-fr">
<video autoplay muted loop playsinline preload="metadata" poster="media/hero_demo_poster.jpg" aria-label="売上集計をAIが自動化する画面の実演。架空データ・音なし"><source src="media/hero_demo.webm" type="video/webm"><source src="media/hero_demo.mp4" type="video/mp4"></video>
<img class="still" src="media/hero_demo_poster.jpg" alt="自動集計ダッシュボードの画面（架空データ）">
</div>
<div class="hero-vid-cap"><b>3枚のシート → 自動集計ダッシュボード</b><span>事例01の実演から12秒・音なし・架空データ</span></div>
</div>
</div>
<div class="rules">
<div class="rule"><i>1</i><div><b>実際に動いたものだけ</b>構想や試作は載せていません。導入先を各事例に明記しています。</div></div>
<div class="rule"><i>2</i><div><b>数字は実測か公開済みの実績</b>前職の数字は公開スライドの値。他社の事例には数字を付けていません。</div></div>
<div class="rule"><i>3</i><div><b>動画は架空データで再現</b>顧客の実データは映しません。実演は同じ仕組みを架空の会社で動かしたものです。</div></div>
</div>
</div></section>

<section class="sec" id="cases"><div class="w">
<div class="sec-head"><div><div class="eyebrow">Cases</div><h2 class="h2">事例</h2><p class="lead">1件1ページ。全体像の図解、60秒の実演、できたことと届いていないこと、まで載せています。</p></div><div class="count"><span id="ccount">9</span><small>件</small></div></div>
<div class="filters"><div class="frow"><span class="flb">導入先</span>{chips_site}</div><div class="frow"><span class="flb">業務</span>{chips_cat}</div></div>
<div class="grid">{"".join(case_card(c, "") for c in cases)}</div>
</div></section>

<section class="sec" id="systems" style="background:var(--bg2)"><div class="w">
<div class="sec-head"><div><div class="eyebrow">Systems</div><h2 class="h2">動いている仕組み</h2><p class="lead">1件1ページにはしていない、日々動いている仕組みと、参考にしている他社の実践。図解を押すと拡大します。</p></div><div class="count">10<small>件</small></div></div>
<div class="sgrid">{"".join(sys_card(l, "") for l in lists)}</div>
</div></section>

<section class="cta"><div class="w">
<h2>まずは30分、いまの業務を聞かせてください。</h2>
<p>同じような課題があれば、御社の業務でどう組み替えるかをその場で話します。オンライン・無料です。</p>
<a href="{TALLY}" class="btn btn-w" target="_blank" rel="noopener">無料で相談する</a>
<div class="note">3営業日以内に返信します。売り込みの電話はしません。</div>
</div></section>
{footer("")}
<script>{JS_COMMON}{JS_INDEX}</script>
</body></html>"""
    return head(title, desc, f"{SITE}/", f"{SITE}/cases/media/case-01_zukai.webp") + body

# ------------------------------------------------------------------ case page
def kp_tile(k):
    v = esc(k["v"]).replace("→", '<span class="ar">→</span>')
    return f'<div class="kp"><small>{esc(k["l"])}</small><b>{v}</b></div>'

def build_case(c, prev_c, next_c):
    num = c["num"]; sh = c["src_sheet"]; face = c["src_face"]
    title = f"事例{num}：{c['headline']}｜{BRAND}"
    url = f"{SITE}/cases/case-{num}.html"
    img = f"{SITE}/cases/media/case-{num}_zukai.webp"
    site_label = c["site_label"]
    overview_h = c.get("overview_h", "これまでと、AI導入後を1枚で")
    # hero visual
    if c["video"]:
        vis = f"""<div class="chero-vis fi"><a href="#demo" aria-label="実演動画へ"><img src="media/case-{num}_demo_poster.jpg" alt="実演動画のポスター画像（架空データ）" width="1920" height="1080"><div class="play"><span>▶</span></div></a><div class="vis-cap">60秒の実演動画（音なし・架空データ）へ</div></div>"""
    else:
        vis = f"""<div class="chero-vis fi"><div class="fr zoomable" data-cap="{esc(c['src_title'])}"><img src="media/case-{num}_zukai.webp" alt="{esc(c['src_title'])}の図解" width="1600" height="900"></div><div class="vis-cap">全体像の図解（押すと拡大）</div></div>"""
    # demo block
    if c["video"]:
        demo = f"""<div class="vid"><video autoplay muted loop playsinline preload="metadata" poster="media/case-{num}_demo_poster.jpg" controls aria-label="{esc(c['src_title'])}の実演（60秒・音なし・架空データ）"><source src="media/case-{num}_demo.webm" type="video/webm"><source src="media/case-{num}_demo.mp4" type="video/mp4"></video>
<div class="vid-cap"><b>60秒・音なし・字幕つき</b><span>架空データで再現。実際の導入では御社のツールに合わせて組みます。</span></div></div>"""
        demo_sub = "見出しの順に、入口から出口まで通しで動かしています。"
    else:
        demo = """<div class="soon"><i>▶</i><div><b>実演動画は準備中です</b><p>撮影でき次第、ここに60秒の実演（音なし・架空データ）が入ります。それまでは上の図解と、下の「できた3つと、まだ届かない1つ」を見てください。</p></div></div>"""
        demo_sub = "この事例は動画の前に、図解と成果の数字で公開しています。"
    tools = "".join(f"<span>{esc(t)}</span>" for t in c["tools"])
    # includes（統合した仕組み）
    incl = ""
    if c.get("includes"):
        cards = []
        for k in c["includes"]:
            x = DATA["includes"][k]; f = x["face"]
            n = f'<span class="n">{esc(f["big"])}</span> <small style="color:var(--tx3);font-size:.78rem">{esc(f.get("sub",""))}</small>' if "big" in f else ""
            cards.append(f'<div class="inc"><span class="bd bd-live">{esc(x["status"].split("（")[0].replace("⚡ ","").replace("🌱 ",""))}</span><h3>{esc(x["title"])}</h3>{n}<p>{esc(x["desc"])}</p></div>')
        incl = f"""<div class="blk fi" id="incl"><div class="blk-h"><span class="tag tag-b">含む</span><h2>この事例に含めている仕組み</h2></div><p class="sub">別々に動いている2つの仕組みを、資料づくりの一連の流れとしてここにまとめています。</p><div class="incl">{"".join(cards)}</div></div>"""
    # side
    src_note = c.get("source_note", "")
    toc = [("overview", "全体像"), ("demo", "実演"), ("story", "課題・やったこと・成果"), ("honest", "できた3つ、まだ1つ"), ("line", "仕組みの一本線"), ("hint", "御社への転用")]
    if c.get("includes"): toc.insert(3, ("incl", "含めている仕組み"))
    toc_html = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)
    side = f"""<aside class="side">
<div class="sidebox"><h4>この事例の概要</h4>
<div class="srow"><span>導入先</span><span>{esc(site_label)}</span></div>
<div class="srow"><span>業務</span><span>{esc(c['cat'])}</span></div>
<div class="srow"><span>使った道具</span><span>{esc("・".join(c['tools']))}</span></div>
<div class="srow"><span>実演動画</span><span>{"あり（60秒）" if c['video'] else "準備中"}</span></div>
<div class="srow"><span>数字の出どころ</span><span>{esc(src_note)}</span></div>
</div>
<div class="sidebox"><h4>このページの中身</h4><ul class="toc">{toc_html}</ul></div>
<div class="sidecta"><b>同じ課題がありますか</b><p>御社の業務でどう組み替えるかを、30分で話します。オンライン・無料。</p><a href="{TALLY}" class="btn btn-p" target="_blank" rel="noopener">無料で相談する</a></div>
</aside>"""
    def ncard(x, label):
        return f'<a class="ncard" href="case-{x["num"]}.html"><img src="media/case-{x["num"]}_zukai.webp" alt="" loading="lazy" width="1600" height="900"><div><small>{label} · CASE {x["num"]}</small><b>{esc(x["headline"])}</b></div></a>'
    nxt = f'<div class="ngrid">{ncard(prev_c, "前の事例")}{ncard(next_c, "次の事例")}</div>'
    body = f"""{header("../")}<div class="progress" id="pg"></div>
<section class="chero"><div class="w">
<div class="crumb"><a href="../index.html">事例一覧</a><span>›</span><span class="cur">CASE {num}</span></div>
<div class="chero-grid">
<div>
<div class="bds"><span class="bd bd-site">{esc(site_label)}</span><span class="bd bd-cat">{esc(c['cat'])}</span>{'<span class="bd bd-video">60秒デモあり</span>' if c['video'] else ''}</div>
<h1>{esc(c['headline'])}</h1>
<p class="lead">{esc(c['lead'])}</p>
<div class="kpis">{"".join(kp_tile(k) for k in c['kpi'])}</div>
</div>
{vis}
</div>
</div></section>

<section class="body"><div class="w"><div class="body-grid">
<div class="main">

<div class="blk fi" id="overview"><div class="blk-h"><span class="tag tag-b">全体像</span><h2>{esc(overview_h)}</h2></div>
<p class="sub">{esc(c['src_problem'])}</p>
<div class="fig"><img class="zoomable" src="media/case-{num}_zukai.webp" alt="{esc(c['src_title'])}の図解（これまでとAI導入後）" width="1600" height="900" data-cap="{esc(c['src_title'])}"><div class="fig-cap"><span>図解を押すと拡大</span><span>{esc(site_label)}</span></div></div></div>

<div class="blk fi" id="demo"><div class="blk-h"><span class="tag tag-d">実演</span><h2>実際の動き</h2></div>
<p class="sub">{esc(demo_sub)}</p>
{demo}</div>

<div class="blk fi" id="story"><div class="blk-h"><span class="tag tag-a">経緯</span><h2>課題、やったこと、成果</h2></div>
<div class="story">
<div class="sbox sbox-r"><h3><span class="lb">課題</span>{esc(sh['haikei_t'])}</h3><p>{esc(sh['haikei'])}</p></div>
<div class="sbox sbox-b"><h3><span class="lb">やったこと</span>{esc(sh['jisshi_t'])}</h3><p>{esc(sh['jisshi'])}</p><div class="tools"><small>使った道具</small>{tools}</div></div>
<div class="sbox sbox-g"><h3><span class="lb">成果</span>{esc(sh['seika_t'])}</h3><p>{esc(sh['seika'])}</p></div>
</div></div>
{incl}
<div class="blk fi" id="honest"><div class="blk-h"><span class="tag tag-r">正直に</span><h2>できた3つと、まだ届かない1つ</h2></div>
<p class="sub">{esc(c['src_wow'])}</p>
<div class="fig"><img class="zoomable" src="media/case-{num}_zukai_m.webp" alt="{esc(c['src_title'])}：ここまでできたことと、まだ届かないこと" width="1600" height="900" data-cap="できた3つと、まだ届かない1つ"><div class="fig-cap"><span>図解を押すと拡大</span><span>4つのうち3つが動いている</span></div></div></div>

<div class="blk fi" id="line"><div class="blk-h"><span class="tag tag-g">仕組み</span><h2>入口から出口、次の行動まで一本の線で</h2></div>
<div class="fig"><img class="zoomable" src="media/case-{num}_zukai_s.webp" alt="{esc(c['src_title'])}：入口→AI→出口→次の行動の流れと成果" width="1600" height="900" data-cap="入口から出口、次の行動まで"><div class="fig-cap"><span>図解を押すと拡大</span><span>成果の数字つき</span></div></div></div>

<div class="blk fi" id="hint"><div class="blk-h"><span class="tag tag-v">御社なら</span><h2>御社への転用</h2></div>
<div class="callout"><b>{esc(c['src_hint'])}</b><p>同じ課題があれば、御社のツールと業務の流れに合わせて組み替えます。まずは30分、いまの業務を聞かせてください。</p></div></div>

</div>
{side}
</div></div></section>

<section class="next"><div class="w"><div class="h3">ほかの事例</div>{nxt}<div class="back"><a href="../index.html#cases">← 事例一覧へ戻る</a></div></div></section>

<section class="cta"><div class="w">
<h2>同じような課題を抱えていませんか？</h2>
<p>御社の業務でどう組み替えるかを、30分で話します。オンライン・無料です。</p>
<a href="{TALLY}" class="btn btn-w" target="_blank" rel="noopener">無料で相談する</a>
</div></section>
{footer("../")}
<script>{JS_COMMON}{JS_CASE}</script>
</body></html>"""
    return head(title, c["lead"], url, img) + body

# ------------------------------------------------------------------ main
def check_assets():
    missing = []
    for c in DATA["cases"]:
        n = c["num"]
        for f in (f"case-{n}_zukai.webp", f"case-{n}_zukai_m.webp", f"case-{n}_zukai_s.webp"):
            if not os.path.exists(os.path.join(ROOT, "cases", "media", f)): missing.append(f)
        if c["video"]:
            for f in (f"case-{n}_demo.mp4", f"case-{n}_demo.webm", f"case-{n}_demo_poster.jpg"):
                if not os.path.exists(os.path.join(ROOT, "cases", "media", f)): missing.append(f)
    for l in DATA["lists"]:
        if not os.path.exists(os.path.join(ROOT, "cases", "media", f"{l['key']}.webp")): missing.append(f"{l['key']}.webp")
    for f in ("hero_demo.mp4", "hero_demo.webm", "hero_demo_poster.jpg"):
        if not os.path.exists(os.path.join(ROOT, "media", f)): missing.append(f)
    return missing

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    miss = check_assets()
    if miss:
        print("!! 素材が足りない:", ", ".join(miss), file=sys.stderr)
        if a.check: sys.exit(1)
    elif a.check:
        print("素材は揃っている"); return
    cases = DATA["cases"]
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(build_index())
    for i, c in enumerate(cases):
        prev_c = cases[i - 1]; next_c = cases[(i + 1) % len(cases)]
        open(os.path.join(ROOT, "cases", f"case-{c['num']}.html"), "w", encoding="utf-8").write(build_case(c, prev_c, next_c))
    print(f"index.html と cases/case-01〜{cases[-1]['num']}.html を書き出した")

if __name__ == "__main__":
    main()
