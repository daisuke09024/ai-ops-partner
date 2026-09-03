# cases/ 実演ブロック（デモ動画）の運用メモ — ブランチ `demo/case-01`

> 2026-09-03 作成。main と本番（ai-ops-partner.vercel.app）は未変更。マージ・本番反映は坂本のOK後。

## 1. このブランチで何をしたか

- `cases/case-01.html`: 「施策」ブロックの直後に「実演」ブロックを追加。`<video autoplay muted loop playsinline preload="metadata" poster>` で、WebM → MP4 の2ソース構成
- `cases/media/`: プレースホルダ動画 `placeholder.webm` / `placeholder.mp4` とポスター `placeholder_poster.jpg`（架空データ・合計約6MB）
- `src` / `poster` は `media/` からの相対パス。本物の動画ができたら同名で上書きするだけで差し替わる（HTML の変更不要）

## 2. Vercel preview の状態（2026-09-03 確認）

- **GitHub 連携は生きている。** push（コミット `bb96fff`）から約20秒で Vercel が preview を作成し、GitHub のコミットステータスが `Vercel – sakamoto-ai-lp` / `Vercel – sakamoto-ai-lp-k73t` ともに「Deployment has completed（success）」になった
- 同じリポジトリに Vercel プロジェクトが **2つ** 接続されている（`sakamoto-ai-lp` と `sakamoto-ai-lp-k73t`。チームは `daisuke09024s-projects`）。push のたびに両方が deploy される。どちらが ai-ops-partner.vercel.app を配信しているかは Vercel の Domains 画面でしか分からない（未確認）
- ブランチ固定の preview URL（push するたびに最新を指す）:
  - https://sakamoto-ai-lp-git-demo-case-01-daisuke09024s-projects.vercel.app/cases/case-01.html
  - https://sakamoto-ai-lp-k73t-git-demo-case-01-daisuke09024s-projects.vercel.app/cases/case-01.html
- **ただし preview は Deployment Protection（Vercel Authentication）で保護されている。** 未ログインで開くと `vercel.com/sso-api` へ 302 リダイレクトされる。Vercel にログイン済みのブラウザで開けば見える。ログインなしの `curl` では `<video>` の有無を機械検証できない（本番ドメインだけが保護なしで公開されている）
- 本番ドメイン `ai-ops-partner.vercel.app/cases/case-01.html` は `<video>` 0件のまま（未変更を確認）

## 3. 坂本が preview を確認する手順（Vercel の Deployments 画面）

1. https://vercel.com/daisuke09024s-projects にログイン
2. プロジェクト `sakamoto-ai-lp`（または `sakamoto-ai-lp-k73t`）を開き、**Deployments** タブへ
3. Branch が `demo/case-01` の行（Environment = Preview）を開き、**Visit** を押す
4. 開いた URL の末尾に `/cases/case-01.html` を足す
5. 「実演」見出しの下でポスター画像が出て、動画が自動再生（音なし・ループ）されることを確認する
6. スマホなど未ログインの端末で見たい場合は、Settings → Deployment Protection で preview の保護を外す必要がある（**設定変更なので坂本の判断**。本番ドメインには影響しない）

## 4. 本番に出す前の確認3点（Vercel 公式ドキュメントで確認・2026-09-03）

### ① Hobby プランは商用利用不可 — 現プランの確認が要る

- 出典: [Fair Use Guidelines § Commercial usage](https://vercel.com/docs/limits/fair-use-guidelines#commercial-usage)（last_updated 2026-07-29）
  > "Hobby teams are restricted to non-commercial personal use only. All commercial usage of the platform requires either a Pro or Enterprise plan."
  > 商用利用の定義: "any Deployment that is used for the purpose of financial gain of anyone involved in any part of the production of the project"。例示に "Advertising the sale of a product or service" が入っている
- この LP はサービスの販売を告知するページなので、定義にそのまま当てはまる。**現プランが Hobby なら Pro が要る**
- Pro の価格: **$20 / 月（開発者シート1人あたり・税別）**。出典: [Pricing](https://vercel.com/pricing) と [Hobby Plan Docs § Upgrading to Pro](https://vercel.com/docs/plans/hobby#upgrading-to-pro)（last_updated 2026-08-11）
- 現プランが Hobby か Pro かは Vercel の Settings → Billing でしか分からない（**未確認**）

### ② 帯域（Fast Data Transfer）の上限と超過時の挙動

- Hobby: **100GB / 月**。Pro: **1TB / 月込み、超過は $0.15/GB〜**。出典: [Pricing](https://vercel.com/pricing)、[Fair Use Guidelines § Typical monthly usage guidelines](https://vercel.com/docs/limits/fair-use-guidelines)
- Hobby で超過した場合は買い足せず止まる。出典: [Hobby Plan Docs § Hobby billing cycle](https://vercel.com/docs/plans/hobby)
  > "if you exceed your usage limits on the Hobby plan, you will have to wait until 30 days have passed before you can use the feature again."
- 目安: 実演ブロックの動画は1本 約3MB（WebM）。ポスター込みで1PVあたり最大 約3.3MB → 100GB は **約30,000 PV / 月** に相当（動画が1本のページの場合）。事例ページ3本すべてに動画を付けても、現状の流入規模なら余裕がある見込み

### ③ 動画ファイルの置き方（リポジトリ直置きでよいか）

- 出典: [Vercel 公式KB: Best practices for hosting videos](https://vercel.com/kb/guide/best-practices-for-hosting-videos-on-vercel-nextjs-mp4-gif)（2025-11-10 更新）
  > "large video files can often lead to excessive bandwidth usage" とし、Vercel Blob か外部サービス（Vimeo / Mux / Cloudinary / S3 + CDN）を推奨。"It's important to ensure your videos are compressed and optimized regardless of the platform they're being hosted on."
- サイズ上限: CLI からのアップロードは source files 合計 **100MB（Hobby）/ 1GB（Pro）**。出典: [Limits § Static file uploads](https://vercel.com/docs/limits)（last_updated 2026-08-25）。Git 連携デプロイでの1ファイル上限は公式 Docs に明記が見つからなかった（**未確認**）。今回の合計約6MB は十分小さい
- 判断の目安: 30秒・720p・3MB級の短尺が数本なら直置きで帯域内に収まる。本数が増える／長尺になる／流入が伸びたら Vercel Blob か外部 CDN へ移す

## 5. 本物の動画への差し替え手順

1. `cases/media/` の `placeholder.webm` / `placeholder.mp4` / `placeholder_poster.jpg` を同名で上書き（720p・音声なし・faststart）
2. 顧客名・ローカルパス・価格表現の NG 検査を通す
3. commit → push（preview が自動で更新される）→ §3 の手順で確認

## 6. やらないこと（坂本のOK後に実施）

- main へのマージ・本番デプロイ
- Vercel の設定変更（Deployment Protection・プラン変更・Domains）
