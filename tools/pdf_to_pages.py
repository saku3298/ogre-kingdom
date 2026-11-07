#!/usr/bin/env python3
"""手書き原稿のPDFを、通常の話（パスワードなし）のページ画像に変換します。

使い方（リポジトリのルートで）:
    python3 tools/pdf_to_pages.py 66 原稿.pdf
    python3 tools/pdf_to_pages.py 66 画像1.jpg 画像2.jpg …   （JPEG画像でも可）

pages/episode66-001.jpg, 002.jpg … ができます（PDFは1ページ＝1枚）。
そのあと、サムネイル pages/thumb-episode66.jpg を置き、work.json を編集して
python3 tools/build.py を実行してください（手順は README.md を参照）。

パスワード付きの話にする場合は、このツールではなく tools/encrypt_episode.py を使います。
必要なもの: Python 3（PDFを使うときは pymupdf: pip install pymupdf）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_pages import load_inputs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
if len(sys.argv) < 3 or not sys.argv[1].isdigit():
    sys.exit(__doc__)
no = int(sys.argv[1])
os.makedirs("pages", exist_ok=True)
pages = load_inputs(sys.argv[2:])
for i, data in enumerate(pages, 1):
    path = f"pages/episode{no:02d}-{i:03d}.jpg"
    open(path, "wb").write(data)
    print("作成:", path)
print(f"\n{len(pages)}ページを作成しました。")
