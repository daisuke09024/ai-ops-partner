# 架空の「受注→入金」業務フロー図（As-Is・スイムレーン）を 1600x900 の HTML に書き出す
# 顧客名・実データは一切含まない。矢印は直線（H/V）だけ。
W, H = 1600, 900
TOP = 96            # タイトル帯の高さ
LABEL_W = 132       # レーン名の列
LANES = ["顧客", "営業", "制作", "品質確認", "経理"]
LANE_H = 140
BOT = TOP + LANE_H * len(LANES)   # 796
STEPS = [  # (label, lane, kind)  kind: manual/system/wait
    ("問い合わせ", 0, "manual"), ("ヒアリング", 1, "manual"), ("見積作成", 1, "manual"), ("見積承認", 0, "manual"),
    ("受注登録", 1, "system"), ("制作依頼", 1, "manual"), ("初稿制作", 2, "manual"), ("社内チェック", 3, "wait"),
    ("修正", 2, "manual"), ("顧客確認", 0, "wait"), ("納品", 2, "system"), ("検収", 0, "manual"),
    ("請求書発行", 4, "wait"), ("入金確認", 4, "manual"),
]
N = len(STEPS)
AREA_X0, AREA_X1 = LABEL_W + 24, W - 24
COL = (AREA_X1 - AREA_X0) / N          # ≈ 103
BW, BH = 90, 56
NOTES = {7: "平均3日待ち", 9: "担当者不在で止まる", 12: "手で転記"}

def box_xy(i, lane):
    x = AREA_X0 + COL * i + (COL - BW) / 2
    y = TOP + LANE_H * lane + (LANE_H - BH) / 2 - 8
    return x, y

parts = []
parts.append(f'<div class="title">業務フロー図（As-Is）｜受注から入金まで</div>')
parts.append(f'<div class="meta">5部門・14工程・架空の例</div>')
for li, name in enumerate(LANES):
    y = TOP + LANE_H * li
    parts.append(f'<div class="lane" style="top:{y}px;height:{LANE_H}px"></div>')
    parts.append(f'<div class="lane-label" style="top:{y}px;height:{LANE_H}px">{name}</div>')
svg = []
for i, (label, lane, kind) in enumerate(STEPS):
    x, y = box_xy(i, lane)
    parts.append(f'<div class="box {kind}" style="left:{x:.0f}px;top:{y:.0f}px"><i>{i+1}</i>{label}</div>')
    if i in NOTES:
        parts.append(f'<div class="note" style="left:{x-6:.0f}px;top:{y+BH+6:.0f}px">! {NOTES[i]}</div>')
    if i + 1 < N:
        _, lane2, _ = STEPS[i + 1]
        x2, y2 = box_xy(i + 1, lane2)
        ax, ay = x + BW, y + BH / 2
        bx, by = x2, y2 + BH / 2
        if lane == lane2:
            d = f"M{ax:.0f} {ay:.0f} L{bx:.0f} {by:.0f}"
        else:
            mx = (ax + bx) / 2
            d = f"M{ax:.0f} {ay:.0f} L{mx:.0f} {ay:.0f} L{mx:.0f} {by:.0f} L{bx:.0f} {by:.0f}"
        svg.append(f'<path d="{d}" marker-end="url(#ar)"/>')
parts.append(f'<svg class="arrows" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><marker id="ar" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#2563eb"/></marker></defs>{"".join(svg)}</svg>')
parts.append(f'<div class="legend" style="top:{BOT+18}px"><span><b class="k manual"></b>手作業</span><span><b class="k system"></b>システムに入力</span><span><b class="k wait"></b>待ちが出る工程</span><span class="ex">! 滞留ポイント（この例では3か所）</span></div>')

html = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><title>flow</title>
<style>
html,body{{margin:0;background:#fff}}
body{{width:{W}px;height:{H}px;position:relative;overflow:hidden;font-family:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",sans-serif;color:#0f1d35}}
.title{{position:absolute;left:32px;top:26px;font-size:34px;font-weight:900;letter-spacing:-.01em;height:48px;line-height:48px;width:1100px;white-space:nowrap;overflow:hidden}}
.meta{{position:absolute;right:32px;top:36px;font-size:18px;color:#5b6b85;font-weight:700;height:28px;line-height:28px;white-space:nowrap}}
.lane{{position:absolute;left:0;width:{W}px;border-top:1px solid #dbe2ee;background:#fff}}
.lane:nth-of-type(odd){{background:#f6f8fc}}
.lane-label{{position:absolute;left:0;width:{LABEL_W}px;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:#0f1d35;border-right:2px solid #c7d2e6;background:#eef2f9;box-sizing:border-box}}
.box{{position:absolute;width:{BW}px;height:{BH}px;box-sizing:border-box;border:2px solid #2563eb;border-radius:10px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;line-height:1.2;text-align:center;padding:4px 3px 0;white-space:nowrap;overflow:hidden}}
.box i{{position:absolute;left:-1px;top:-1px;font-style:normal;font-size:11px;font-weight:800;color:#fff;background:#2563eb;border-radius:8px 0 8px 0;padding:1px 6px;line-height:14px}}
.box.system{{background:#e9efff}}
.box.wait{{border-color:#f59e0b;background:#fff7e6}}
.note{{position:absolute;font-size:13px;font-weight:800;color:#b45309;background:#fff;border:1.5px solid #f59e0b;border-radius:6px;padding:2px 7px;white-space:nowrap;height:22px;line-height:18px;box-sizing:border-box}}
.arrows{{position:absolute;left:0;top:0;pointer-events:none}}
.arrows path{{fill:none;stroke:#2563eb;stroke-width:2.5}}
.legend{{position:absolute;left:{LABEL_W+24}px;display:flex;gap:28px;font-size:16px;color:#3b4a63;font-weight:700;height:26px;line-height:26px;white-space:nowrap}}
.legend span{{display:inline-flex;align-items:center;gap:8px}}
.k{{display:inline-block;width:22px;height:16px;border:2px solid #2563eb;border-radius:5px;background:#fff;box-sizing:border-box}}
.k.system{{background:#e9efff}} .k.wait{{border-color:#f59e0b;background:#fff7e6}}
.legend .ex{{color:#b45309}}
</style>
<body>{"".join(parts)}</body></html>'''
open(__import__('sys').argv[1], 'w', encoding='utf-8').write(html)
print('wrote', __import__('sys').argv[1])
