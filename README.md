# オーガキングダム

YUURI・SAKUの共作によるオリジナル漫画『オーガキングダム』の公開サイトです（GitHub Pages）。
公開URL: https://saku3298.github.io/ogre-kingdom/

画面はジャンププラス風です。縦向きは1ページ表示、横向きは右から左の2ページ見開きで読めます。
一部の話は限定公開で、パスワードを入力すると読めます。

## フォルダ構成

| 場所 | 役割 |
|---|---|
| `work.json` | 作品情報・話数・巻・DEMON図鑑・関連作品のデータ（**ここを編集します**） |
| `tools/build.py` | `work.json` から全HTMLを生成します |
| `tools/encrypt_episode.py` | パスワード付きの話の画像（`.ogk`）を作ります |
| `tools/make_ogp.py` | SNS共有用の画像を `images/ogp/default.jpg` に生成します |
| `css/style.css` | 画面のデザイン（トップ・ビューア・図鑑・404） |
| `js/viewer.js` | ビューア（スワイプ・見開き・続きから読む・進捗バー） |
| `js/top.js` | トップページ（タブ・話数の範囲と並べ替え） |
| `js/protected-reader.js` | パスワード付きの話の復号 |
| `pages/` | 各話のページ `episodeNN-PPP.jpg`、サムネイル `thumb-episodeNN.jpg`、巻の表紙 `volumeN-cover.jpg`、図鑑・相関図の画像など |
| `protected/` | パスワード付きの話の画像 `episodeNN-PPP.ogk`（暗号化済み） |
| `images/` | SNS共有用の画像、「同じ作者の作品」の表紙 |
| `assets/favicon.svg` | タブのアイコン |
| `index.html`, `episodeN.html`, `volumeN.html`, `demon-encyclopedia.html`, `correlation.html`, `404.html` | **自動生成されるので直接編集しません** |

## 新しい話を追加する手順

通常の話（誰でも読める）:

1. 画像を置く: `pages/episode66-001.jpg`, `episode66-002.jpg` …（話2桁-ページ3桁）と、サムネイル `pages/thumb-episode66.jpg`
2. `work.json` の `episodes` で、その話の行（`"status": "preparing"` のもの）を書き換える
   ```json
   { "no": 66, "title": "第66話のタイトル" }
   ```
   まだ行がない場合は、`episodes` の最後に追加します。
3. 単行本に入れるなら、その巻の `volumes` の `episodes` に話の番号を足す
4. `python3 tools/build.py`
5. 変更・追加したファイルをGitHubにアップロードする（`index.html`、`episode66.html`、`volumeN.html`、`work.json`、追加した画像）

パスワード付きの話:

1. 手順1の代わりに、元のJPEG画像を暗号化する（パスワードは既存の話と同じものを使います）
   ```
   python3 tools/encrypt_episode.py 66 画像1.jpg 画像2.jpg 画像3.jpg …
   ```
   `protected/episode66-001.ogk` … ができます（`pip install cryptography` が必要です）。サムネイルは通常どおり `pages/` に置きます。
2. `work.json` の行に `"protected": true` を付ける
   ```json
   { "no": 66, "title": "第66話のタイトル", "protected": true }
   ```
3. 以降は同じです（`python3 tools/build.py` → アップロード）

**注意:** `protected/` の `.ogk` ファイルは、**ファイルの場所と名前も鍵の一部**です。フォルダ名やファイル名を変えたり、別の場所へ移したりすると読めなくなります。

ページ数は画像の枚数から自動で数えます。「準備中」の話は、一覧にグレーの枠で表示されます。

## 操作方法

- 縦向き: 左右スワイプ、または下の「次のページ／前のページ」ボタンでページをめくります。
- 横向き: 右から左の見開き表示です。PCは ← → キーでもめくれます。
- 途中まで読むと、次に開いたときに「続きから」と出ます（この端末のブラウザにだけ保存されます）。
