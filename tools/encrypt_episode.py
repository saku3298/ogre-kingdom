#!/usr/bin/env python3
"""パスワード付きの話の画像（.ogk）を作ります。

使い方（リポジトリのルートで）:
    python3 tools/encrypt_episode.py 66 原稿.pdf
    python3 tools/encrypt_episode.py 66 画像1.jpg 画像2.jpg 画像3.jpg …

  - 手書き原稿のPDF（1ページ＝1枚）か、JPEG画像を渡します。PDFを使うときは
    pymupdf が必要です（pip install pymupdf）。
  - 画像は渡した順に protected/episode66-001.ogk, 002.ogk … になります。
  - パスワードは実行中に聞かれます（入力は画面に表示されません）。
    環境変数 OGK_PASSWORD に入れておくこともできます。
  - 既存の話と必ず同じパスワードを使ってください（サイト全体で共通です）。

必要なもの: Python 3 と cryptography（pip install cryptography）。PDFを使うときは pymupdf も。

※ .ogk は「ファイルの場所と名前」も鍵の一部です。protected/ の中のファイルは、
   名前を変えたり別の場所へ移したりすると読めなくなります（作り直しが必要です）。
形式: 'OGK1' + IV(12バイト) + AES-GCM暗号文。鍵は PBKDF2-SHA256（15万回）で
      パスワードから作ります。js/protected-reader.js の復号と対になっています。
"""
import getpass, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_pages import load_inputs
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SALT = b"OgreKingdom2026!"
ITERATIONS = 150000

if len(sys.argv) < 3 or not sys.argv[1].isdigit():
    sys.exit(__doc__)
no = int(sys.argv[1])
files = sys.argv[2:]
password = os.environ.get("OGK_PASSWORD") or getpass.getpass("パスワード: ")
if not os.environ.get("OGK_PASSWORD") and getpass.getpass("もう一度: ") != password:
    sys.exit("パスワードが一致しません。")

key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=ITERATIONS).derive(password.encode("utf-8"))
os.makedirs("protected", exist_ok=True)
pages = load_inputs(files)
for i, data in enumerate(pages, 1):
    path = f"protected/episode{no:02d}-{i:03d}.ogk"
    iv = os.urandom(12)
    enc = AESGCM(key).encrypt(iv, data, path.encode("utf-8"))   # 追加認証データ＝ファイルのパス
    open(path, "wb").write(b"OGK1" + iv + enc)
    print("作成:", path)
print(f"\n{len(pages)}枚を暗号化しました。work.json の第{no}話に \"protected\": true を付けて、python3 tools/build.py を実行してください。")
