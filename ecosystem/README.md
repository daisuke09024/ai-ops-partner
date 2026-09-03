# `/ecosystem/` — AIの使い方の「型」を公開するページ

`index.html`（要約＋動画2本＋役割分担＋地図の埋め込み＋事例カード＋CTA）と `map.html`（AIエコシステム地図の公開版）の2枚。
どちらも **自動生成物なので手で編集しない**。中身を変える時はビルドを回し直す。

## preview

- ブランチ固定 URL: https://sakamoto-ai-lp-k73t-git-feat-ecosystem-daisuke09024s-projects.vercel.app/ecosystem/
- **Vercel の Deployment Protection がかかっている**ので、Vercel にログインしたブラウザで開く（未ログインだと `vercel.com/sso-api` にリダイレクトされる）
- push すると Vercel が2プロジェクト分の preview を作る（このリポジトリに2つ接続されている）
- **main へのマージ＝本番公開は坂本の OK 後**

## 中身

| ファイル | 何か |
|---|---|
| `index.html` | 公開ページ本体。noindex |
| `map.html` | 地図（公開版）。`index.html` から iframe で読み込み、全画面リンクもある |
| `media/ecosystem_walkthrough.mp4` / `.webm` / `_poster.jpg` | 地図を実際に操作した60秒のウォークスルー（1920×1080・音声なし） |
| `media/shikumi_30s_1080p.mp4` / `.webm` / `_poster.jpg` | 仕組みの図解30秒（1920×1080・音声なし） |

動画は「動きで見る」節に `<video autoplay muted loop playsinline poster>` で埋め込んでいる。合計 14MB。

## 作り直し方

作り方の手順・道具は**このリポジトリの外**にある（公開リポジトリに内部の道具を置かないため）。

- ページ本体: `ai-ops/思考/壁打ち/_wip/2026-09-02_デモ見せ方/ecosystem-build/再生成手順.md`
- ウォークスルー動画: 同 `ecosystem-walk/README.md`
- 30秒の図解: 同 `anim/README.md`

**地図を再生成していない時は、ビルドに `--index-only` を付ける**（付けないと地図が古い版に戻る。ビルド側にも鮮度ガードが入っていて、古い地図で上書きしようとすると止まる）。

## 載せないもの

顧客名・案件名・金額・ローカルの絶対パス・Notion の私有ページへのリンク。
ビルドが可視テキストと属性に加えて、地図に埋め込まれたデータも復号して機械検査する（1件でも当たると書き出さない）。
