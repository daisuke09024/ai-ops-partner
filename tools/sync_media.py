#!/usr/bin/env python3
"""図解PNG・実演動画を素材の家からこのリポジトリへ取り込む（ローカル専用・公開物には素材の家のパスを書かない）。

使い方:
  python3 tools/sync_media.py --src "<デモ見せ方PJのフォルダ>"
  （<フォルダ>/anim/zukai/本番/*.png と <フォルダ>/demo-clips/case-0N_demo.* を読む）

図解は 1920x1080 の PNG を横1600pxの WebP に変換して cases/media/ に置く（1枚 約110KB。Pillow が要る）。
動画は無加工でコピーする。既にあるファイルは上書きする。
"""
import argparse, glob, os, re, shutil, subprocess, sys

# LPの番号 → 素材の接頭辞（冒頭図解は接頭辞のあとに "_M_" "_S_" "_T3_" が付かないもの）
CASES = {
    "01": "case-01", "02": "case-02", "03": "case-03", "04": "case-04",
    "05": "ca-ai", "06": "naisei-lecture", "07": "case-07",
    "08": "shodan-rail", "09": "shiryo-2gate",
}
VIDEO = ["01", "02", "03", "04", "07", "08", "09"]
LISTS = ["list-map", "list-flow", "list-form", "list-lp", "list-saki",
         "list-nikki", "list-1on1", "list-shodan", "list-growth", "list-slack"]

def scale_png(src, dst, width=1600, quality=90):
    """PNG を横 width px の WebP に変換して保存する（Pillow）。1920x1080 の PNG 約240KB → 約110KB"""
    from PIL import Image
    im = Image.open(src).convert("RGB")
    h = round(im.height * width / im.width)
    im.resize((width, h), Image.LANCZOS).save(dst, "WEBP", quality=quality, method=6)

def pick(files, infix):
    """infix: None=冒頭（_M_/_S_/_T3_ を含まない）, 'M'/'S'=中盤/締め"""
    for f in files:
        b = os.path.basename(f)
        if infix is None and not any(t in b for t in ("_M_", "_S_", "_T3_")):
            return f
        if infix and f"_{infix}_" in b:
            return f
    # 冒頭が T3 型の事例（shodan-rail / shiryo-2gate）
    if infix is None:
        for f in files:
            if "_T3_" in os.path.basename(f):
                return f
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--videos-dir", default=None, help="確定動画の家（営業/事例/動画）。case-NN_短編60秒.{mp4,webm} と _poster.jpg を case-NN_demo.* として上書きする")
    ap.add_argument("--no-zukai", action="store_true", help="図解（case-NN_zukai*.webp）を触らない。LP 側で作り直した図解（02/03/09）を PJ 本番の旧版で上書きしないための逃げ道")
    a = ap.parse_args()
    zdir = os.path.join(a.src, "anim", "zukai", "本番")
    ddir = os.path.join(a.src, "demo-clips")
    out = os.path.join(os.path.dirname(__file__), "..", "cases", "media")
    os.makedirs(out, exist_ok=True)
    done = []
    for num, pre in CASES.items():
        files = [] if a.no_zukai else sorted(glob.glob(os.path.join(zdir, f"{pre}_*.png")))
        if a.no_zukai:
            pass  # 図解は触らない（LP 側で作り直した版が正本）
        elif not files:
            print(f"!! 図解が無い: {pre}", file=sys.stderr); continue
        for infix, suf in (() if a.no_zukai else ((None, ""), ("M", "_m"), ("S", "_s"))):
            f = pick(files, infix)
            if not f:
                print(f"!! {pre} の {infix or '冒頭'} が無い", file=sys.stderr); continue
            dst = os.path.join(out, f"case-{num}_zukai{suf}.webp")
            scale_png(f, dst); done.append(dst)
        if num in VIDEO:
            src_pre = pre if pre.startswith("case-") else None
            for ext in ("mp4", "webm"):
                s = os.path.join(ddir, f"{src_pre}_demo.{ext}")
                if os.path.exists(s):
                    shutil.copy2(s, os.path.join(out, f"case-{num}_demo.{ext}")); done.append(s)
            s = os.path.join(ddir, f"{src_pre}_demo_poster.jpg")
            if os.path.exists(s):
                shutil.copy2(s, os.path.join(out, f"case-{num}_demo_poster.jpg")); done.append(s)
    for key in LISTS:
        files = sorted(glob.glob(os.path.join(zdir, f"{key}_*.png")))
        if not files:
            print(f"!! 一覧の図解が無い: {key}", file=sys.stderr); continue
        dst = os.path.join(out, f"{key}.webp")
        scale_png(files[0], dst); done.append(dst)
    print(f"取り込み {len(done)} 件")

    if a.videos_dir:
        ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); out = os.path.join(ROOT, "cases", "media"); n = 0
        for f in sorted(os.listdir(a.videos_dir)):
            m = re.match(r"(.+?)_短編60秒(_poster\.jpg|\.mp4|\.webm)$", f)
            if not m: continue
            pre = m.group(1)
            num = next((k for k, v in CASES.items() if v == pre), None)  # 決定版の名前は事例 id（08=shodan-rail・09=shiryo-2gate）
            if num is None:
                m2 = re.fullmatch(r"case-(\d{2})", pre)   # 決定版が case-NN の名前で置かれている事例（05・06）も拾う
                if m2 and m2.group(1) in CASES: num = m2.group(1)
            if num is None:
                print(f"!! 対応する事例が無いので飛ばす: {f}", file=sys.stderr); continue   # 黙って落とさない（2026-09-12）
            dst = os.path.join(out, f"case-{num}_demo" + m.group(2))
            shutil.copy2(os.path.join(a.videos_dir, f), dst); n += 1; print("video:", f, "->", os.path.relpath(dst, ROOT))
        print(f"videos: {n} files")

if __name__ == "__main__":
    main()
