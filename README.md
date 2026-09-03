# sakamoto-ai-lp

AI業務改革パートナー LP。GitHub → Vercel の自動デプロイ。本番ドメインは ai-ops-partner.vercel.app（`main` ブランチ）。

## ページ

| パス | 中身 | 状態 |
|---|---|---|
| `/` | LP 本体 | 公開中 |
| `/cases/case-01.html` 〜 `case-03.html` | 事例詳細（01 には60秒の実演動画） | 公開中 |
| `/demo/` | 動くデモの索引（実演動画・触れるダッシュボード） | ブランチ `feat/demo-index`・本番未反映 |
| `/ecosystem/` | AIの使い方の「型」 | ブランチ `feat/ecosystem`・本番未反映 |

`/demo/` と `/ecosystem/` は `<meta name="robots" content="noindex, nofollow">` を入れてある。

## preview URL（ブランチ固定・push のたびに最新を指す）

同じリポジトリに Vercel プロジェクトが2つ接続されていて、push すると両方が deploy される。

- `feat/demo-index`
  - https://sakamoto-ai-lp-git-feat-demo-index-daisuke09024s-projects.vercel.app/demo/
  - https://sakamoto-ai-lp-k73t-git-feat-demo-index-daisuke09024s-projects.vercel.app/demo/
- `feat/ecosystem`
  - https://sakamoto-ai-lp-k73t-git-feat-ecosystem-daisuke09024s-projects.vercel.app/ecosystem/

preview は Deployment Protection（Vercel Authentication）で保護されている。Vercel にログイン済みのブラウザで開く。未ログインだと SSO へリダイレクトされるので、`curl` では中身を確認できない。

見る手順は `cases/README_demo.md` の §3 と同じ（Deployments タブ → 該当ブランチの行 → Visit → パスを足す）。

## /demo/ の中身と素材

| 置き場所 | 使っているもの |
|---|---|
| ヒーロー | `demo/media/mechanism_30s.*`（30秒・無音・仕組みの図解アニメ） |
| 事例① | `cases/media/case-01_demo.*` を参照（事例ページと同じ実体・重複して置かない） |
| 事例② | `demo/media/case-02_demo.*`（60秒・無音・字幕） |
| 事例③ | 動画は準備中（プレースホルダのカード） |
| 触ってみる | `demo/kpi-dashboard_demo.html`（1ファイル自己完結・外部読込なし・架空データ） |
| 長編 | 準備中のカードのみ（動画は未収録の場面が残っているため未掲載） |

`demo/media/` の合計は約13MB。動画はすべて `<video autoplay muted loop playsinline poster>` で、画面の外に出ると JS で一時停止する。

## 公開前の検査（main へマージする前に必ず通す）

1. NG検査（顧客名・ローカルパス・価格表現）
2. 機械ゲート（1080 / 640 幅ではみ出し・折り返し・リンク切れ・video の属性）

どちらも検査器はこのリポジトリの外（デモ制作PJ側）にある。手順は `cases/README_demo.md` を参照。

## 本番反映

`main` へのマージは坂本の判断。Vercel の設定変更（Deployment Protection・プラン・Domains）も同様に未実施。
