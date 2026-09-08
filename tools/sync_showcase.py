#!/usr/bin/env python3
"""ユースケースの正本（showcase_meta.json）から、LPに載せる本文だけを tools/cases.json へ写す（ローカル専用）。

使い方:
  python3 tools/sync_showcase.py --source "<showcase_meta.json のパス>"

写すのは公開してよい文言だけ（title / face / problem / desc / wow / hint / sheet / category / status）。
リンク（file:// や Notion）は写さない。LP 固有の項目（num / headline / lead / tools / site / video）は
cases.json 側で手で持つので、この script は既存の値を保ったまま正本側の文言だけ更新する。
"""
import argparse, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cases.json")
CASE_ORDER = ["acrove-sales-viz", "acrove-minutes", "acrove-docs", "kyozai-factory",
              "ca-ai", "naisei-lecture", "worklog", "shodan-rail", "shiryo-human-two-gates"]
LIST_ORDER = [("ecosystem-map", "list-map"), ("biz-flow-diagram", "list-flow"),
              ("form-sales", "list-form"), ("ficks-lp", "list-lp"), ("task-prep", "list-saki"),
              ("diary", "list-nikki"), ("gaisha-1on1-prep", "list-1on1"),
              ("gaisha-sales-process-automation", "list-shodan"),
              ("gaisha-member-growth-os", "list-growth"), ("gaisha-slack-engagement", "list-slack")]
COPY = ["title", "face", "problem", "desc", "wow", "hint", "sheet", "category", "status", "origin"]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--source", required=True); a = ap.parse_args()
    src = {c["id"]: c for c in json.load(open(a.source, encoding="utf-8"))["cards"]}
    cur = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"cases": [], "lists": []}
    by_id = {c["id"]: c for c in cur["cases"]}
    cases = []
    for i, cid in enumerate(CASE_ORDER, 1):
        c = by_id.get(cid, {"id": cid})
        c["num"] = f"{i:02d}"
        for k in COPY:
            if k in src[cid]: c[f"src_{k}"] = src[cid][k]
        cases.append(c)
    lists = []
    lby = {c["id"]: c for c in cur["lists"]}
    for cid, key in LIST_ORDER:
        c = lby.get(cid, {"id": cid}); c["key"] = key
        for k in COPY:
            if k in src[cid]: c[f"src_{k}"] = src[cid][k]
        lists.append(c)
    cur["cases"] = cases; cur["lists"] = lists
    json.dump(cur, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"cases {len(cases)} / lists {len(lists)} → {OUT}")

if __name__ == "__main__":
    main()
