# media/ — ヒーローの実演デモ動画

> 2026-09-03 追加。ブランチ `feat/hero-video-a`（右カラムに16:9の動画カード）と
> `feat/hero-video-b`（背景に薄く敷く）で**同じ素材**を使い、置き方だけを比べる。
> main と本番（ai-ops-partner.vercel.app）は未変更。マージは坂本のOK後。

## ファイル

| ファイル | 中身 | サイズ |
|---|---|---|
| `hero_demo.webm` | VP9 / 1920×1080 / 12秒 / 音声なし（優先ソース） | 0.64 MB |
| `hero_demo.mp4` | H.264 / 1920×1080 / 12秒 / 音声なし / faststart | 0.61 MB |
| `hero_demo_poster.jpg` | 1600px幅。導入後ダッシュボードの1枚 | 0.11 MB |

1回の表示で読むのは WebM 0.64MB ＋ poster 0.11MB。Vercel 公式が動画の直置きを非推奨としているため
**2MB 以下**を上限に置いている（本数が増えるか長尺化したら Vercel Blob か外部CDNへ移す）。

## 中身

事例01の実演短編（60秒・無音字幕つき）の **16.0〜28.0秒** を切り出したもの。
「担当ごとに分かれた3枚のシート」→「AIが自動集計したダッシュボード」への切り替わりを含む区間で、
ループさせると Before と After を往復して見せられる。数値・社名はすべて架空データ。

## 作り直す手順

素材の正本は work 配下の `思考/壁打ち/_wip/2026-09-02_デモ見せ方/demo-clips/case-01_demo.mp4`。
`demo-clips/tools/convert.sh` と同じ設定を直接叩く（GIFは不要なので convert.sh は通さない）。

```bash
SRC=case-01_demo.mp4
ffmpeg -y -ss 16 -i "$SRC" -t 12 -vf "scale=-2:1080" \
  -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p -an -movflags +faststart hero_demo.mp4
ffmpeg -y -ss 16 -i "$SRC" -t 12 -vf "scale=-2:1080" \
  -c:v libvpx-vp9 -b:v 0 -crf 32 -row-mt 1 -deadline good -cpu-used 2 -an hero_demo.webm
ffmpeg -y -ss 22.0 -i "$SRC" -frames:v 1 -vf "scale=1600:-2" -q:v 5 hero_demo_poster.jpg
```

## 差し替えるときの決まり

- **ファイル名は変えない**（HTML側は `media/` からの相対パスで参照しているだけなので、同名で上書きすれば差し替わる）
- 音声トラックは入れない（`-an`）。自動再生は muted が前提
- 差し替えたら NG検査（`demo-clips/tools/check_ng.py`）と、幅1280/375・
  `prefers-reduced-motion` あり/なしの4通りの実測を通してから push する

## preview の見方

push すると Vercel が自動で preview を作る（2026-09-03 実測: 両ブランチとも
`sakamoto-ai-lp` / `sakamoto-ai-lp-k73t` の2プロジェクトで success）。

- ブランチ固定の URL（push のたびに最新を指す）
  - A案: https://sakamoto-ai-lp-git-feat-hero-video-a-daisuke09024s-projects.vercel.app/
  - B案: https://sakamoto-ai-lp-git-feat-hero-video-b-daisuke09024s-projects.vercel.app/
- **未ログインでは開けない**（Deployment Protection が効いていて `vercel.com/sso-api` へ 302 される）。
  Vercel にログイン済みのブラウザで開く
- もう一方のプロジェクト `sakamoto-ai-lp-k73t` はブランチ名を足すとホスト名が
  DNS の63文字上限を超えるため、この形の URL では引けない。Deployments 画面から Visit で開く

## この2案の違い

| | A案 `feat/hero-video-a` | B案 `feat/hero-video-b` |
|---|---|---|
| 置き方 | 右カラムに 16:9 の動画カード | 第一画面の背景に薄く敷く（文字は前面） |
| 浮遊カード3枚 | 動画カードに差し替え | 撤去 |
| スマホ（375px） | 本文の下に出る（従来は非表示） | 背景として薄く出る |
| 第一画面に入るか | デスクトップは入る。スマホは入らない | どの幅でも入る |
| 見せ方の工夫 | 下に「3枚のシート → 自動集計ダッシュボード」の説明 | ぼかし2.5px＋上寄せトリミングで焼き込み字幕を画角外へ |

どちらを採るかは坂本の判断。採らなかった側のブランチは消してよい。
