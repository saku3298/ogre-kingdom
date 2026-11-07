"""PDF（手書き原稿）を、サイト用のJPEG画像に変換する共通部品です（単独では使いません）。

tools/encrypt_episode.py と tools/pdf_to_pages.py から呼ばれます。
必要なもの: pymupdf（pip install pymupdf）
"""
import io, os, sys

TARGET_WIDTH = 884   # 既存の話の画像と同じ幅（884×1254 前後）
QUALITY = 88


def pdf_to_jpegs(pdf_path):
    """PDFの各ページを、幅884pxのJPEGのバイト列にして順に返す"""
    try:
        import pymupdf
    except ImportError:
        sys.exit("PDFを読むには pymupdf が必要です:  pip install pymupdf")
    out = []
    with pymupdf.open(pdf_path) as doc:
        for page in doc:
            zoom = TARGET_WIDTH / page.rect.width
            pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
            out.append(pix.tobytes("jpeg", jpg_quality=QUALITY))
    if not out:
        sys.exit(f"ページが読めませんでした: {pdf_path}")
    return out


def load_inputs(paths):
    """PDF/JPEG のファイル名のリストを、JPEGバイト列のリストにする（渡した順）"""
    data = []
    for p in paths:
        if p.lower().endswith(".pdf"):
            data += pdf_to_jpegs(p)
        else:
            b = open(p, "rb").read()
            if b[:2] != b"\xff\xd8":
                sys.exit(f"JPEG画像かPDFを渡してください: {p}")
            data.append(b)
    return data
