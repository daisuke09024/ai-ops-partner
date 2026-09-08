#!/usr/bin/env python3
"""LP の生成器。tools/cases.json から index.html（事例のまとめ＝ポートフォリオ）と cases/case-NN.html（事例9本・β 物語順の型）を書き出す。

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

# 公開文の用語の置換表（内輪語→社外の言葉）。JSON に残っていても build 時に置き換え、警告を出す（坂本 2026-09-08 裁定 3a）
GLOSSARY = [("FB", "修正"), ("レール", "流れ"), ("ブリーフ", "依頼メモ"), ("裁定", "決定"), ("回収枠", "答えを返す枠"), ("話者分離", "話した人の分離"), ("記帳", "記録")]
_glossary_hits = []

def pub(s):
    """公開文に内輪語が残っていたら置き換える（esc の前段）"""
    s = str(s)
    for k, v in GLOSSARY:
        if k in s and not (k == "ブリーフ" and "依頼メモ（ブリーフ）" in s):
            _glossary_hits.append(f"{k}→{v}: {s[:40]}")
            s = s.replace(k, v)
    return s

def esc(s):
    return html.escape(pub(s), quote=True)

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
.eyebrow{font-family:var(--fe);font-size:.74rem;font-weight:700;letter-spacing:.16em;color:var(--blue);text-transform:uppercase;display:flex;align-items:center;gap:10px;margin-bottom:12px}
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
.bd-cat{background:var(--bg2);color:var(--tx2)}
.bd-video{background:var(--tx);color:#fff}
.bd-video::before{content:'▶';font-size:.62rem}
.bd-soon{background:var(--bg2);color:var(--tx3)}
.bd-ext{background:var(--amber-bg);color:var(--amber)}
.bd-live{background:var(--green-bg);color:var(--green)}
.bd-live::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}

/* ===== index: hero ===== */
.hero{padding:calc(64px + clamp(40px,6vw,60px)) 0 clamp(40px,5vw,52px);position:relative;background:linear-gradient(180deg,#f7f9fc 0%,#fff 100%);border-bottom:1px solid var(--border)}
.hero-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:clamp(28px,5vw,64px);align-items:center;position:relative;z-index:1}
.hero h1{font-size:clamp(1.9rem,4.6vw,2.8rem);font-weight:900;line-height:1.28;letter-spacing:-.03em;margin:8px 0 18px}
.hero h1 em{font-style:normal;color:var(--blue)}
.hero-lead{font-size:1rem;color:var(--tx2);margin-bottom:26px;max-width:520px}
.hero-btns{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:30px}
.stats{display:flex;flex-wrap:wrap;border-top:1px solid var(--border);padding-top:18px;gap:14px 0}
.st{padding-right:24px;margin-right:24px;border-right:1px solid var(--border)}
.st:last-child{border-right:0;margin-right:0;padding-right:0}
.st-n{font-family:var(--fe);font-size:1.5rem;font-weight:800;color:var(--tx);line-height:1.1;letter-spacing:-.02em;white-space:nowrap}
.st-n small{font-size:.65em;font-weight:700;color:var(--tx2);margin-left:2px}
.st-l{font-size:.74rem;color:var(--tx3);margin-top:4px;line-height:1.4}
.hero-vid{position:relative;width:100%;max-width:560px;justify-self:end;padding:10px;background:#fff;border:1px solid var(--border);border-radius:18px;box-shadow:0 20px 50px rgba(15,29,53,.12)}
.hero-vid-fr{position:relative;aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:var(--dark)}
.hero-vid-fr video,.hero-vid-fr img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hero-vid-fr img.still{display:none}
.hero-vid-cap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px 12px;margin:10px 6px 2px}
.hero-vid-cap b{font-size:.86rem;font-weight:700}
.hero-vid-cap span{font-size:.74rem;color:var(--tx2);font-weight:700;padding:3px 10px;border-radius:100px;background:var(--bg2)}
@media(prefers-reduced-motion:reduce){.hero-vid-fr video{display:none}.hero-vid-fr img.still{display:block}}
@media(max-width:900px){.hero-grid{grid-template-columns:1fr}.hero-vid{justify-self:stretch;max-width:100%}}
@media(max-width:640px){.st{border-right:0;padding-right:18px;margin-right:0}}

/* 読み方の帯 */

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
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;text-decoration:none;color:inherit;transition:var(--tr);position:relative}
.card:hover{transform:translateY(-4px);box-shadow:0 14px 34px rgba(15,29,53,.1)}
.card.hide{display:none}
.thumb{position:relative;aspect-ratio:16/9;background:var(--bg2);overflow:hidden;border-bottom:1px solid var(--border)}
.thumb img{width:100%;height:100%;object-fit:cover;transition:transform .5s ease}
.card:hover .thumb img{transform:scale(1.03)}
.cbody{padding:18px 20px 20px;display:flex;flex-direction:column;flex:1}
.cmeta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-family:var(--fe);font-size:.72rem;font-weight:700;color:var(--blue);letter-spacing:.08em;margin-bottom:8px}
.cmeta .cat{font-family:var(--fj);letter-spacing:0;font-weight:600;color:var(--tx3)}
.cmeta .cat::before{content:'·';margin-right:8px;color:var(--border2)}
.cbds{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.card h3{font-size:1.05rem;font-weight:800;line-height:1.55;margin-bottom:8px;letter-spacing:-.01em}
.card p{font-size:.88rem;color:var(--tx2);line-height:1.7;margin-bottom:16px;flex:1}
.kpi{display:flex;justify-content:space-between;align-items:flex-end;gap:10px;border-top:1px solid var(--border);padding-top:14px}
.kpi small{display:block;font-size:.72rem;color:var(--tx3);font-weight:600}
.kpi b{font-family:var(--fe);font-size:1.25rem;font-weight:800;color:var(--blue-d);letter-spacing:-.01em;line-height:1.3;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.kpi b .ar{color:var(--tx3);font-weight:500}
.kpi b .old{color:var(--tx3);font-weight:700}
.kpi .sub{font-size:.76rem;color:var(--tx2);font-weight:500;font-family:var(--fj)}
.kpi .go{flex-shrink:0;width:34px;height:34px;border-radius:50%;background:var(--blue-bg2);color:var(--blue);display:flex;align-items:center;justify-content:center;font-weight:800;transition:var(--tr)}
.card:hover .kpi .go{background:var(--blue);color:#fff}

/* systems (一覧・図解を2列で大きく) */
.sgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
@media(max-width:640px){.sgrid{grid-template-columns:1fr}}
.scard{background:var(--card);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;cursor:zoom-in;transition:var(--tr)}
.scard:hover{box-shadow:var(--sh2);transform:translateY(-3px)}
.scard .thumb{aspect-ratio:16/9;border-bottom:1px solid var(--border)}
.sbody{padding:14px 18px 16px;display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.sbody h3{font-size:.98rem;font-weight:800;line-height:1.5;margin-bottom:3px}
.sbody p{font-size:.8rem;color:var(--tx3);line-height:1.6}
.sbody .bd{flex-shrink:0;margin-top:2px}

/* cta */
.cta{background:var(--dark);color:#fff;text-align:center;padding:clamp(64px,9vw,96px) 0;position:relative}
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

/* case body（β 物語順: 課題→変えたこと→デモ→結果→仕組み→転用） */
.chero{background:linear-gradient(180deg,#f7f9fc,#fff);border-bottom:1px solid var(--border)}
.chero::before{display:none}
.chero-vis .fr{border:1px solid var(--border);box-shadow:0 20px 50px rgba(15,29,53,.12);background:#fff}
.csec{padding:clamp(40px,6vw,64px) 0}
.csec.tight{padding-top:0}
.csec.alt{background:var(--bg2)}
.in{max-width:1100px;margin:0 auto}
.chd{max-width:1100px;margin:0 auto 16px;display:flex;align-items:center;gap:14px}
.chd h2{font-size:clamp(1.2rem,2.4vw,1.5rem);font-weight:800;line-height:1.45}
p.csub{max-width:1100px;margin:-6px auto 16px;font-size:.95rem;color:var(--tx2);line-height:1.85}
.quote{max-width:1100px;margin:0 auto 14px;padding:14px 18px;border-left:4px solid var(--rose);background:var(--rose-bg);border-radius:0 12px 12px 0;font-size:1rem;font-weight:700;color:var(--tx)}
.vidwrap{max-width:1100px;margin:0 auto;background:var(--dark);border-radius:var(--r2);padding:10px;box-shadow:var(--sh3)}
.vidwrap video{width:100%;aspect-ratio:16/9;border-radius:12px;background:#000}
.vidwrap .vid-cap{padding:10px 8px 2px}
.nums{max-width:1100px;margin:0 auto 16px;display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:16px}
.num{background:#fff;border:1px solid var(--border);border-radius:var(--r2);padding:22px 24px;box-shadow:var(--sh);display:flex;flex-direction:column;justify-content:center}
.num small{display:block;font-size:.8rem;color:var(--tx3);font-weight:700}
.num b{display:block;font-family:var(--fe);font-weight:800;color:var(--blue-d);letter-spacing:-.02em;line-height:1.15;margin-top:6px;font-size:clamp(1.7rem,3.4vw,2.6rem)}
.num.big b{font-size:clamp(2rem,4.6vw,3.4rem);color:var(--tx)}
.num.big b .ar{color:var(--blue);margin:0 8px;font-weight:600}
.num b .nw{white-space:nowrap}
.num.big b.long{font-size:clamp(1.5rem,3.2vw,2.3rem)}
.num .sub{font-size:.82rem;color:var(--tx2);margin-top:6px}
.csec .tools{max-width:1100px;margin:0 auto 16px;border-top:0;padding-top:0}
.note-box{max-width:1100px;margin:16px auto 0;border:1px solid var(--border);border-left:4px solid var(--amber);border-radius:12px;padding:14px 18px;background:#fff}
.note-box b{display:block;font-size:.8rem;color:var(--amber);letter-spacing:.06em;margin-bottom:4px}
.note-box p{font-size:.95rem;color:var(--tx2);line-height:1.85}
.more-fig{max-width:1100px;margin:16px auto 0}
.more-fig summary{cursor:pointer;font-size:.9rem;font-weight:700;color:var(--blue);padding:10px 14px;border:1px solid var(--border);border-radius:10px;background:#fff}
.more-fig[open] summary{margin-bottom:12px}
@media(max-width:900px){.nums{grid-template-columns:1fr}}
.tag{flex-shrink:0;padding:6px 12px;border-radius:10px;font-size:.78rem;font-weight:800;letter-spacing:.04em;line-height:1.4}
.tag-b{background:var(--blue-bg2);color:var(--blue-d)}
.tag-r{background:var(--rose-bg);color:var(--rose)}
.tag-a{background:var(--amber-bg);color:var(--amber)}
.tag-g{background:var(--green-bg);color:var(--green)}
.tag-v{background:var(--violet-bg);color:var(--violet)}
.tag-d{background:var(--tx);color:#fff}
.fig{background:#fff;border:1px solid var(--border);border-radius:var(--r2);padding:10px;box-shadow:var(--sh)}
.fig img{width:100%;height:auto;aspect-ratio:16/9;border-radius:12px}
.fig-cap{font-size:.8rem;color:var(--tx3);margin-top:10px;padding:0 6px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.vid{background:var(--dark);border-radius:var(--r2);padding:10px;box-shadow:var(--sh3)}
.vid video{width:100%;border-radius:12px;aspect-ratio:16/9;background:#000}
.vid-cap{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:rgba(255,255,255,.65);font-size:.8rem;padding:10px 6px 2px}
.vid-cap b{color:#fff}
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

JS_FB = r"""
(function(){if(!/[?&]fb=1(&|$)/.test(location.search))return;
var KEY='lpfb:'+location.pathname.replace(/\/index\.html$/,'/');var notes=[];try{notes=JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){}
var st=document.createElement('style');st.textContent='.fbx{outline:2px dashed #e11d48!important;outline-offset:2px;position:relative}.fbpin{position:absolute;z-index:99998;background:#e11d48;color:#fff;font:700 12px/22px system-ui;width:22px;height:22px;border-radius:50%;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.3);pointer-events:none}#fbp{position:fixed;right:16px;bottom:16px;z-index:99999;width:340px;max-height:70vh;display:flex;flex-direction:column;background:#fff;border:1px solid #cbd5e1;border-radius:12px;box-shadow:0 12px 40px rgba(0,0,0,.25);font:13px/1.5 system-ui,sans-serif;color:#111}#fbp .h{padding:10px 14px;font-weight:700;background:#e11d48;color:#fff;border-radius:12px 12px 0 0}#fbp .l{overflow:auto;padding:8px 14px;flex:1}#fbp .l div{padding:6px 0;border-bottom:1px solid #eee}#fbp .l b{color:#e11d48;margin-right:6px}#fbp .l small{display:block;color:#64748b}#fbp .b{display:flex;gap:6px;padding:8px 14px;flex-wrap:wrap}#fbp button{font:600 12px system-ui;padding:6px 10px;border-radius:8px;border:1px solid #cbd5e1;background:#f8fafc;cursor:pointer}#fbp button.p{background:#111;color:#fff;border-color:#111}#fbp textarea{margin:0 14px 12px;height:90px;font:11px/1.4 ui-monospace,monospace;border:1px solid #cbd5e1;border-radius:8px;padding:6px}#fbp .t{padding:0 14px 8px;color:#64748b;font-size:11px}';document.head.appendChild(st);
var panel=document.createElement('div');panel.id='fbp';panel.innerHTML='<div class="h">FBモード（このページ <span id="fbn">0</span> 件）</div><div class="t">直したい場所をクリック → メモを書く。終わったら「コピー」してチャットに貼る</div><div class="l" id="fbl"></div><div class="b"><button class="p" id="fbcopy">このページ分をコピー</button><button id="fball">全ページ分をコピー</button><button id="fbclr">このページ分を消す</button></div><textarea id="fbout" readonly placeholder="コピーした文がここにも出ます"></textarea>';document.body.appendChild(panel);
function save(){localStorage.setItem(KEY,JSON.stringify(notes));render()}
function place(){document.querySelectorAll('.fbpin').forEach(function(p){p.remove()});document.querySelectorAll('.fbx').forEach(function(e){e.classList.remove('fbx')});notes.forEach(function(n,i){var el=null;try{el=document.querySelector(n.sel)}catch(e){}if(!el)return;el.classList.add('fbx');var r=el.getBoundingClientRect();var pin=document.createElement('div');pin.className='fbpin';pin.textContent=i+1;pin.style.left=(r.left+scrollX-8)+'px';pin.style.top=(r.top+scrollY-8)+'px';document.body.appendChild(pin)})}
function render(){document.getElementById('fbn').textContent=notes.length;document.getElementById('fbl').innerHTML=notes.map(function(n,i){return '<div><b>'+(i+1)+'</b>'+esc(n.note)+'<small>'+esc(n.where)+' 「'+esc(n.text)+'」</small></div>'}).join('')||'<div style="color:#94a3b8">まだありません</div>';place()}
function esc(t){return String(t).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
function selOf(el){var parts=[];while(el&&el!==document.body){var t=el.tagName.toLowerCase();if(el.id){parts.unshift('#'+CSS.escape(el.id));break}var i=1,sib=el;while((sib=sib.previousElementSibling))i++;parts.unshift(t+':nth-child('+i+')');el=el.parentElement}return parts.join('>')}
function whereOf(el){var sec=el.closest('section,header,footer');var h=sec&&sec.querySelector('h1,h2');var w=sec?(sec.id?'#'+sec.id:sec.tagName.toLowerCase()):'';if(h)w+=' '+h.textContent.trim().slice(0,30);return w||'ページ上部'}
function textOf(el){return (el.innerText||el.alt||el.getAttribute('aria-label')||'').replace(/\s+/g,' ').trim().slice(0,60)}
function out(txt){var ta=document.getElementById('fbout');ta.value=txt;ta.select();if(navigator.clipboard)navigator.clipboard.writeText(txt).catch(function(){});}
function md(key,arr){var path=key.replace('lpfb:','');return '## '+path+'\n'+arr.map(function(n,i){return '- ['+(i+1)+'] '+n.where+' 「'+n.text+'」 → '+n.note}).join('\n')+'\n'}
document.addEventListener('click',function(ev){if(panel.contains(ev.target))return;ev.preventDefault();ev.stopPropagation();var el=ev.target.closest('h1,h2,h3,p,li,a,button,img,video,small,b,span,div');if(!el)return;var note=prompt('この場所へのメモ:\n「'+textOf(el)+'」');if(!note)return;notes.push({sel:selOf(el),where:whereOf(el),text:textOf(el),note:note,at:new Date().toISOString().slice(0,16)});save()},true);
document.getElementById('fbcopy').addEventListener('click',function(){out(md(KEY,notes))},true);
document.getElementById('fball').addEventListener('click',function(){var all=[];for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k&&k.indexOf('lpfb:')===0){try{var a=JSON.parse(localStorage.getItem(k)||'[]');if(a.length)all.push(md(k,a))}catch(e){}}}out(all.join('\n')||'（メモはありません）')},true);
document.getElementById('fbclr').addEventListener('click',function(){if(confirm('このページのメモを全部消しますか？')){notes=[];save()}},true);
addEventListener('resize',place);addEventListener('scroll',function(){place()},{passive:true});
document.querySelectorAll('.fi').forEach(function(e){e.style.opacity='1';e.style.transform='none'});
render()})();
"""

JS_INDEX = r"""
(function(){const cards=[...document.querySelectorAll('#cases .card')];const cnt=document.getElementById('ccount');
let cat='all';
function apply(){let n=0;cards.forEach(c=>{const ok=(cat==='all'||c.dataset.cat===cat);c.classList.toggle('hide',!ok);if(ok)n++});cnt.textContent=n;}
document.querySelectorAll('.chip[data-cat]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.chip[data-cat]').forEach(x=>x.classList.remove('on'));b.classList.add('on');cat=b.dataset.cat;apply()}));
})();
"""

JS_CASE = r"""
(function(){const bar=document.getElementById('pg');if(!bar)return;function u(){const h=document.documentElement;const p=h.scrollTop/(h.scrollHeight-h.clientHeight);bar.style.width=(Math.max(0,Math.min(1,p))*100)+'%'}document.addEventListener('scroll',u,{passive:true});u();})();
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
        nav = f'<a href="#cases">事例</a><a href="#systems">動いている仕組み</a><a href="{TALLY}" class="hd-cta" target="_blank" rel="noopener">無料で相談する</a>'
        left = f'<a href="#" class="hd-logo"><i></i>AI業務改革<span>パートナー</span></a>'
    else:
        nav = f'<a href="{root}index.html#cases">事例一覧</a><a href="{root}index.html#systems">動いている仕組み</a><a href="{TALLY}" class="hd-cta" target="_blank" rel="noopener">無料で相談する</a>'
        left = f'<a href="{root}index.html" class="hd-logo"><i></i>AI業務改革<span>パートナー</span></a>'
    return f'<header class="hd"><div class="hd-in">{left}<nav class="hd-nav">{nav}</nav></div></header>'

def footer(root):
    return f"""<footer class="ft"><div class="w">
<div class="ft-links"><a href="{root}index.html#cases">事例</a><a href="{root}index.html#systems">動いている仕組み</a><a href="{TALLY}" target="_blank" rel="noopener">お問い合わせ</a></div>
<p class="ft-copy">© 2026 {BRAND}</p></div></footer>
<div class="lb" id="lb" role="dialog" aria-label="図解を拡大"><img src="" alt=""><div class="lb-cap"></div></div>
"""

def kpi_html(face):
    """カードの数字タイル。face が before/after 型と big/sub 型の2種"""
    if "before" in face:
        sub = f'<div class="sub">{esc(face["sub"])}</div>' if face.get("sub") else ""
        inner = f'<small>{esc(face["label"])}</small><b><span class="old">{esc(face["before"])}</span><span class="ar">→</span>{esc(face["after"])}</b>{sub}'
    else:
        inner = f'<small>{esc(face.get("sub",""))}</small><b>{esc(face["big"])}</b>'
    return f'<div class="kpi"><div>{inner}</div><span class="go" aria-hidden="true">↗</span></div>'

def ill_src(num, root, size=""):
    """事例カードの挿絵。無ければ図解にフォールバック（挿絵は cases/media/case-NN_ill{_m}.webp）"""
    name = f"case-{num}_ill{size}.webp"
    if os.path.exists(os.path.join(ROOT, "cases", "media", name)):
        return f"{root}cases/media/{name}"
    return f"{root}cases/media/case-{num}_zukai.webp"


def case_card(c, root):
    num = c["num"]
    vid = '<div class="cbds"><span class="bd bd-video">60秒デモ</span></div>' if c["video"] else ""
    return f"""<a class="card fi" href="{root}cases/case-{num}.html" data-cat="{esc(c['cat'])}">
<div class="thumb"><img src="{ill_src(num, root, "_m")}" alt="{esc(c['src_title'])}のイメージ" loading="lazy" width="1600" height="900"></div>
<div class="cbody"><div class="cmeta">CASE {num}<span class="cat">{esc(c['cat'])}</span></div>
{vid}<h3>{esc(c['headline'])}</h3>
{kpi_html(c['src_face'])}</div></a>"""

def sys_card(l, root):
    ext = l.get("src_origin") == "external"
    badge = '<span class="bd bd-ext">他社の事例</span>' if ext else f'<span class="bd bd-live">{esc(l["src_status"].split("（")[0].replace("⚡ ","").replace("🧰 ","").replace("🤝 ",""))}</span>'
    img = l.get("img") or f"{l['key']}.webp"
    return f"""<div class="scard zoomable fi" data-cap="{esc(l['src_title'])}"><div class="thumb"><img src="{root}cases/media/{img}" alt="{esc(l['src_title'])}の図解" loading="lazy" width="1600" height="900"></div>
<div class="sbody"><div><h3>{esc(l['src_title'])}</h3><p>{esc(l['src_problem'])}</p></div>{badge}</div></div>"""

# ------------------------------------------------------------------ index
def build_index():
    cases = DATA["cases"]; lists = DATA["lists"]; meta = DATA["meta"]
    n_video = sum(1 for c in cases if c["video"])
    cat_counts = {k: sum(1 for c in cases if c["cat"] == k) for k in meta["cats"]}
    chips_cat = '<button class="chip on" data-cat="all">すべて</button>' + "".join(
        f'<button class="chip" data-cat="{esc(k)}">{esc(k)}<small>{cat_counts[k]}</small></button>' for k in meta["cats"] if cat_counts[k])
    title = f"{BRAND}｜AIで業務を動かした事例とデモ"
    desc = "実際に動いた（動いている）AI活用の事例9本と、日々動いている仕組み10件。図解と60秒のデモで載せています。"
    body = f"""{header("")}
<section class="hero"><div class="w">
<div class="hero-grid">
<div class="hero-text">
<div class="eyebrow">事例とデモ</div>
<h1>AIに任せた業務の、<br><em>実物だけ。</em></h1>
<p class="hero-lead">実際に動いたものだけを、図解と60秒のデモで載せています。構想や試作はありません。</p>
<div class="hero-btns"><a href="#cases" class="btn btn-p">事例を見る ↓</a><a href="{TALLY}" class="btn btn-o" target="_blank" rel="noopener">30分、無料で相談する</a></div>
<div class="stats">
<div class="st"><div class="st-n">9</div><div class="st-l">事例</div></div>
<div class="st"><div class="st-n">{n_video}</div><div class="st-l">60秒のデモ</div></div>
<div class="st"><div class="st-n">10</div><div class="st-l">動いている仕組み</div></div>
<div class="st"><div class="st-n">1,740<small>万円</small></div><div class="st-l">年間の削減額（3事例の合計）</div></div>
</div>
</div>
<div class="hero-vid fi">
<div class="hero-vid-fr">
<video autoplay muted loop playsinline preload="metadata" poster="media/hero_demo_poster.jpg" aria-label="売上集計をAIが自動化する画面のデモ。架空データ・音なし"><source src="media/hero_demo.webm" type="video/webm"><source src="media/hero_demo.mp4" type="video/mp4"></video>
<img class="still" src="media/hero_demo_poster.jpg" alt="自動集計ダッシュボードの画面（架空データ）">
</div>
<div class="hero-vid-cap"><b>3枚のシート → 自動集計ダッシュボード</b><span>デモ 12秒・架空データ</span></div>
</div>
</div>
</div></section>

<section class="sec" id="cases"><div class="w">
<div class="sec-head"><div><div class="eyebrow">Cases</div><h2 class="h2">事例</h2><p class="lead">1件1ページ。課題、変えたこと、60秒のデモ、結果まで載せています。</p></div><div class="count"><span id="ccount">9</span><small>件</small></div></div>
<div class="filters"><div class="frow"><span class="flb">業務</span>{chips_cat}</div></div>
<div class="grid">{"".join(case_card(c, "") for c in cases)}</div>
</div></section>

<section class="sec" id="systems" style="background:var(--bg2)"><div class="w">
<div class="sec-head"><div><div class="eyebrow">Systems</div><h2 class="h2">動いている仕組み</h2><p class="lead">日々動いている仕組み。図解を押すと拡大します。</p></div><div class="count">{len(lists)}<small>件</small></div></div>
<div class="sgrid">{"".join(sys_card(l, "") for l in lists)}</div>
</div></section>

<section class="cta"><div class="w">
<h2>まずは30分、いまの業務を聞かせてください。</h2>
<p>同じような課題があれば、御社の業務でどう組み替えるかをその場で話します。オンライン・無料です。</p>
<a href="{TALLY}" class="btn btn-w" target="_blank" rel="noopener">無料で相談する</a>
<div class="note">3営業日以内に返信します。売り込みの電話はしません。</div>
</div></section>
{footer("")}
<script>{JS_COMMON}{JS_INDEX}{JS_FB}</script>
</body></html>"""
    return head(title, desc, f"{SITE}/", f"{SITE}/cases/media/case-01_zukai.webp") + body

# ------------------------------------------------------------------ case page
def kp_tile(k):
    v = esc(k["v"]).replace("→", '<span class="ar">→</span>')
    return f'<div class="kp"><small>{esc(k["l"])}</small><b>{v}</b></div>'

def build_case(c, prev_c, next_c):
    """事例ページ（β 物語順）: FV → 課題 → 変えたこと → デモ（動画のある事例だけ）→ 結果 → 仕組み → 含む（09）→ 御社への転用。
    任意項目: c["sakamoto_note"]（なぜこの組み方にしたか。あれば仕組みの下に出す）／ c["detail_m"]=true（図解Mを折りたたみで出す。既定は出さない）"""
    num = c["num"]; sh = c["src_sheet"]; face = c["src_face"]
    title = f"事例{num}：{c['headline']}｜{BRAND}"
    url = f"{SITE}/cases/case-{num}.html"
    img = f"{SITE}/cases/media/case-{num}_ill.webp"
    tools = "".join(f"<span>{esc(t)}</span>" for t in c["tools"])
    kpis = "".join(kp_tile(k) for k in c["kpi"])
    ill = ill_src(num, "", "").replace("cases/", "", 1)
    def zukai(suffix, alt, cap):
        return f'<div class="fig"><img class="zoomable" src="media/case-{num}_zukai{suffix}.webp" alt="{esc(alt)}" width="1600" height="900" data-cap="{esc(cap)}"><div class="fig-cap"><span>図解を押すと拡大</span><span>{esc(cap)}</span></div></div>'
    badges = f'<div class="bds"><span class="bd bd-cat">{esc(c["cat"])}</span>{"<span class=\"bd bd-video\">デモあり</span>" if c["video"] else ""}</div>'
    fv = f"""<section class="chero"><div class="w"><div class="crumb"><a href="../index.html">事例一覧</a><span>›</span><span class="cur">CASE {num}</span></div>
<div class="chero-grid"><div>{badges}<h1>{esc(c['headline'])}</h1><p class="lead">{esc(c['lead'])}</p><div class="kpis">{kpis}</div></div>
<div class="chero-vis fi"><div class="fr"><img src="{ill}" alt="{esc(c['src_title'])}のイメージ" width="1600" height="900"></div></div></div></div></section>"""
    sec_problem = f"""<section class="csec" id="problem"><div class="w"><div class="chd"><span class="tag tag-r">課題</span><h2>{esc(sh['haikei_t'])}</h2></div><div class="quote">{esc(c['src_problem'])}</div><p class="csub" style="margin-top:0">{esc(sh['haikei'])}</p></div></section>"""
    overview_cap = c.get("overview_h", "これまでと、AI導入後")
    sec_change = f"""<section class="csec tight" id="change"><div class="w"><div class="chd"><span class="tag tag-b">変えたこと</span><h2>{esc(sh['jisshi_t'])}</h2></div><p class="csub">{esc(sh['jisshi'])}</p><div class="tools"><small>使った道具</small>{tools}</div>
<div class="in fi">{zukai('', c['src_title'] + 'の図解（これまでとAI導入後）', overview_cap)}</div></div></section>"""
    if c["video"]:
        voice = c.get("voice")
        cap_b = "60秒・字幕とナレーションつき（自動再生中は無音）" if voice else "60秒・字幕つき"
        sec_demo = f"""<section class="csec alt" id="demo"><div class="w"><div class="chd"><span class="tag tag-d">デモ</span><h2>実際の動き（60秒・架空データ）</h2></div><p class="csub">見出しの順に、入口から出口まで通しで動かしています。</p>
<div class="vidwrap fi"><video autoplay muted loop playsinline preload="metadata" poster="media/case-{num}_demo_poster.jpg" controls aria-label="{esc(c['src_title'])}のデモ（60秒・架空データ）"><source src="media/case-{num}_demo.webm" type="video/webm"><source src="media/case-{num}_demo.mp4" type="video/mp4"></video>
<div class="vid-cap"><b>{cap_b}</b><span>架空データで再現。実際の導入では御社のツールに合わせて組みます。</span></div></div></div></section>"""
    else:
        sec_demo = ""
    if "before" in face:
        sub = f'<div class="sub">{esc(face["sub"])}</div>' if face.get("sub") else ""
        long = " long" if len(face["before"]) + len(face["after"]) > 9 else ""
        big = f'<div class="num big"><small>{esc(face["label"])}</small><b class="{long.strip()}"><span class="nw">{esc(face["before"])}</span><span class="ar">→</span><span class="nw">{esc(face["after"])}</span></b>{sub}</div>'
    else:
        long = " long" if len(face["big"]) > 7 else ""
        big = f'<div class="num big"><small>{esc(face.get("sub",""))}</small><b class="{long.strip()}">{esc(face["big"])}</b></div>'
    others = "".join(f'<div class="num"><small>{esc(k["l"])}</small><b>{esc(k["v"])}</b></div>' for k in c["kpi"][1:3])
    sec_result = f"""<section class="csec{'' if c['video'] else ' alt'}" id="result"><div class="w"><div class="chd"><span class="tag tag-g">結果</span><h2>{esc(sh['seika_t'])}</h2></div>
<div class="nums fi">{big}{others}</div><p class="csub" style="margin-top:0">{esc(sh['seika'])}</p></div></section>"""
    note = f'<div class="note-box"><b>なぜこの組み方にしたか</b><p>{esc(c["sakamoto_note"])}</p></div>' if c.get("sakamoto_note") else ""
    detail = f'<details class="more-fig"><summary>設計の細部を見る</summary>{zukai("_m", c["src_title"] + "：動かしてから足した1手", "動かしてから足した1手")}</details>' if c.get("detail_m") else ""
    sec_system = f"""<section class="csec tight" id="system"><div class="w"><div class="chd"><span class="tag tag-g">仕組み</span><h2>入口から出口、次の行動まで一本の線で</h2></div>
<div class="in fi">{zukai('_s', c['src_title'] + '：入口→AI→出口→次の行動の流れと成果', '入口から出口、次の行動まで')}</div>{note}{detail}</div></section>"""
    incl = ""
    if c.get("includes"):
        cards = []
        for k in c["includes"]:
            x = DATA["includes"][k]; f = x["face"]
            n = f'<span class="n">{esc(f["big"])}</span> <small style="color:var(--tx3);font-size:.78rem">{esc(f.get("sub",""))}</small>' if "big" in f else ""
            cards.append(f'<div class="inc"><span class="bd bd-live">{esc(x["status"].split("（")[0].replace("⚡ ","").replace("🌱 ",""))}</span><h3>{esc(x["title"])}</h3>{n}<p>{esc(x["desc"])}</p></div>')
        incl = f"""<section class="csec" id="incl"><div class="w"><div class="chd"><span class="tag tag-b">含む</span><h2>この事例に含めている仕組み</h2></div><p class="csub">別々に動いている2つの仕組みを、資料づくりの一連の流れとしてここにまとめています。</p><div class="in incl fi">{"".join(cards)}</div></div></section>"""
    wow = c.get("src_wow", "").rstrip("。")
    sec_hint = f"""<section class="csec" id="hint"><div class="w"><div class="chd"><span class="tag tag-v">御社なら</span><h2>御社への転用</h2></div><div class="in fi"><div class="callout"><b>{esc(c['src_hint'])}</b><p>{esc(wow)}。同じ課題があれば、御社のツールと業務の流れに合わせて組み替えます。まずは30分、いまの業務を聞かせてください。</p></div></div></div></section>"""
    def ncard(x, label):
        return f'<a class="ncard" href="case-{x["num"]}.html"><img src="{ill_src(x["num"], "", "_m").replace("cases/", "", 1)}" alt="" loading="lazy" width="1600" height="900"><div><small>{label} · CASE {x["num"]}</small><b>{esc(x["headline"])}</b></div></a>'
    nxt = f'<div class="ngrid">{ncard(prev_c, "前の事例")}{ncard(next_c, "次の事例")}</div>'
    body = f"""{header("../")}<div class="progress" id="pg"></div>
{fv}
{sec_problem}
{sec_change}
{sec_demo}
{sec_result}
{sec_system}
{incl}
{sec_hint}
<section class="next"><div class="w"><div class="h3">ほかの事例</div>{nxt}<div class="back"><a href="../index.html#cases">← 事例一覧へ戻る</a></div></div></section>

<section class="cta"><div class="w">
<h2>同じような課題を抱えていませんか？</h2>
<p>御社の業務でどう組み替えるかを、30分で話します。オンライン・無料です。</p>
<a href="{TALLY}" class="btn btn-w" target="_blank" rel="noopener">無料で相談する</a>
</div></section>
{footer("../")}
<script>{JS_COMMON}{JS_CASE}{JS_FB}</script>
</body></html>"""
    return head(title, c["lead"], url, img) + body

# ------------------------------------------------------------------ main
def check_assets():
    missing = []
    for c in DATA["cases"]:
        n = c["num"]
        for f in (f"case-{n}_zukai.webp", f"case-{n}_zukai_m.webp", f"case-{n}_zukai_s.webp", f"case-{n}_ill.webp", f"case-{n}_ill_m.webp"):
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
    _glossary_hits.clear()
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(build_index())
    for i, c in enumerate(cases):
        prev_c = cases[i - 1]; next_c = cases[(i + 1) % len(cases)]
        open(os.path.join(ROOT, "cases", f"case-{c['num']}.html"), "w", encoding="utf-8").write(build_case(c, prev_c, next_c))
    if _glossary_hits:
        print("!! 内輪語を置き換えた（JSON 側も直すこと）:", file=sys.stderr)
        for h in sorted(set(_glossary_hits)): print("   ", h, file=sys.stderr)
    print(f"index.html と cases/case-01〜{cases[-1]['num']}.html を書き出した")

if __name__ == "__main__":
    main()
