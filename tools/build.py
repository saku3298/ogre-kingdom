#!/usr/bin/env python3
"""work.json から、このサイトのHTMLをすべて生成します。

使い方（リポジトリのルートで）:
    python3 tools/build.py

生成されるもの:
    index.html（作品トップ）、episodeN.html（各話）、volumeN.html（単行本）、
    demon-encyclopedia.html（DEMON図鑑）、correlation.html（相関図）、404.html

編集してよいのは work.json、css/、js/ です。生成されたHTMLは直接編集しないでください。

画像の置き場所（既存の画像はそのまま使います）:
    pages/episodeNN-PPP.jpg           各話のページ（話2桁-ページ3桁）
    pages/thumb-episodeNN.jpg         話一覧のサムネイル
    pages/volumeN-cover.jpg           単行本の表紙
    protected/episodeNN-PPP.ogk       パスワード付きの話のページ（暗号化された画像）
                                       ※ このファイルは場所と名前を変えると読めなくなります。

新しい話を追加するとき:
  1. 画像を置く（上の命名規則）。パスワード付きにする場合は
       python3 tools/encrypt_episode.py 66 画像1.jpg 画像2.jpg …
     で protected/ に .ogk を作る。
  2. work.json の "episodes" で、その話の行（status が "preparing" のもの）を
       { "no": 66, "title": "タイトル", "protected": true }
     のように書き換える（パスワード付きでなければ "protected" は不要）。
     最新話が増えるときは、行そのものを追加する。
  3. 単行本に入れるなら、その巻の "episodes" に話の番号を足す。
  4. python3 tools/build.py
ページ数は画像の枚数から自動で数えます。
"""
import glob, hashlib, html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
e = html.escape

data = json.load(open("work.json", encoding="utf-8"))
site, work = data["site"], data["work"]
episodes, volumes = data["episodes"], data["volumes"]
related, site_link = data.get("related", []), data.get("site_link")
TITLE = work["title"]
BASE = site["url"].rstrip("/") + "/"
PER_RANGE = 50


def ver(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()[:8]


def first_existing(base, exts, what):
    for ext in exts:
        if os.path.exists(f"{base}.{ext}"):
            return f"{base}.{ext}"
    sys.exit(f"エラー: {what}が見つかりません: {base}.{exts[0]}")


def img(base):
    return first_existing(base, ("webp", "jpg", "png"), "画像")


def ep_pages(ep):
    """各話のページファイル（パスワード付きは .ogk）。戻り値は (パス, 保護か)"""
    n = ep["no"]
    if ep.get("protected"):
        files = sorted(glob.glob(f"protected/episode{n:02d}-*.ogk"))
        prot = True
    else:
        stems = set()
        for ext in ("webp", "jpg", "png"):
            stems |= {os.path.splitext(p)[0] for p in glob.glob(f"pages/episode{n:02d}-*.{ext}")}
        files = [img(s) for s in sorted(stems)]
        prot = False
    if not files:
        sys.exit(f"エラー: 第{n}話の画像がありません（protected: {prot}）")
    return [(f, prot) for f in files]


published = [ep for ep in episodes if ep.get("status") != "preparing"]
pub_by_no = {ep["no"]: ep for ep in published}
pages_of = {ep["no"]: ep_pages(ep) for ep in published}
vol_of_ep = {n: v for v in volumes for n in v["episodes"]}
latest = published[-1]
V_CSS, V_VIEWER, V_TOP, V_PROT = ver("css/style.css"), ver("js/viewer.js"), ver("js/top.js"), ver("js/protected-reader.js")


def head(title, desc, url, typ, theme=False, extra=""):
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{'<meta name="theme-color" content="#111111">' if theme else ''}
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{typ}">
<meta property="og:site_name" content="{e(site["name"])}">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}images/ogp/default.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(TITLE)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/style.css?v={V_CSS}">{extra}</head>
'''


# ---------------------------------------------------------------- トップ
def index_page():
    max_no = max(ep["no"] for ep in episodes)
    ranges = "".join(
        f'<button class="range-btn{" active" if s == 1 else ""}" data-range="{s}-{min(s + PER_RANGE - 1, max_no)}">{s}-{min(s + PER_RANGE - 1, max_no)}</button>'
        for s in range(1, max_no + 1, PER_RANGE))
    rows = ""
    for ep in episodes:
        n = ep["no"]
        if ep.get("status") == "preparing":
            rows += (f'<div class="episode-row preparing" data-ep="{n}"><div class="episode-thumb placeholder">{n}</div>'
                     f'<div class="episode-meta"><div class="episode-title">第{n}話 <span>準備中</span></div><div class="episode-sub">公開準備中です</div></div>'
                     f'<div class="episode-status">準備中</div></div>')
        else:
            badge = '<span class="protected-badge">🔒 パスワード</span>' if ep.get("protected") else ""
            rows += (f'<a class="episode-row" href="episode{n}.html" data-ep="{n}">'
                     f'<img class="episode-thumb" src="{img(f"pages/thumb-episode{n:02d}")}" alt="第{n}話 {e(ep["title"])}">'
                     f'<div class="episode-meta"><div class="episode-title">第{n}話 <span>{e(ep["title"])}</span></div>{badge}</div>'
                     f'<div class="episode-read">読む</div></a>')
    tiles = "".join(
        f'<a class="volume-tile" href="volume{v["no"]}.html"><img src="{img(f"pages/volume{v["no"]}-cover")}" alt="第{v["no"]}巻 表紙">'
        f'<div><strong>第{v["no"]}巻</strong><span>{e(v["summary"])}</span></div></a>' for v in volumes)
    tab = ' target="_blank" rel="noopener"'
    cards = "".join(
        f'<a class="author-work-card" href="{e(r["url"])}"{tab if r.get("new_tab") else ""}><img src="{r["cover"]}" alt="{e(r["cover_alt"])}">'
        f'<div><div class="author-work-title">{e(r["title"])}</div><div class="author-work-author">作者：{e(r["author"])}</div>'
        f'<div class="author-work-label">コミックス</div></div></a>' for r in related)
    if site_link:
        cards += (f'<a class="author-work-card" href="{e(site_link["url"])}"{tab if site_link.get("new_tab") else ""}><img src="{site_link["image"]}" alt="{e(site_link["title"])}">'
                  f'<div><div class="author-work-title">{e(site_link["title"])}</div><div class="author-work-author">{e(site_link["description"])}</div>'
                  f'<div class="author-work-label">作品集</div></div></a>')
    ls = data.get("line_stickers")
    line_html = ""
    if ls:
        items = "".join(f'<div class="line-sticker-card"><div class="line-sticker-title">{e(i["title"])}</div>'
                        f'<a class="line-sticker-btn" href="{e(i["url"])}" target="_blank" rel="noopener">LINE STOREで見る</a></div>' for i in ls["items"])
        line_html = (f'<div class="info-section"><h2>LINEスタンプ</h2><img class="line-sticker-promo" loading="lazy" src="{img("pages/" + ls["promo"])}" alt="{e(ls["promo_alt"])}">'
                     f'<div class="line-sticker-grid">{items}</div></div>')
    footer_link = f' ｜ <a href="{e(site_link["url"])}" target="_blank" rel="noopener" style="text-decoration:underline">{e(site_link["title"])}</a>' if site_link else ""
    n_ep = len(episodes)
    return head(TITLE, site["description"], BASE, "website") + f'''<body class="top-page">
<div class="jp-shell">
<section class="jp-hero"><img src="{img("pages/" + work.get("hero_cover", "volume1-cover"))}" alt="{e(TITLE)} 第1巻表紙"><div class="jp-hero-right"><div class="jp-hero-text"><div class="jp-kicker">ORIGINAL MANGA</div><div class="jp-logo">{e(TITLE)}</div></div></div></section>
<section class="jp-info"><h1 class="jp-title">{e(TITLE)}</h1><div class="jp-author">{e(work["author"])}</div><div class="jp-tags"><span>オリジナル漫画</span><span>全{n_ep}話</span><span>全{len(volumes)}巻</span><span>{e(work.get("status", "連載中"))}</span></div>
<div class="jp-actions"><a class="jp-btn primary" href="episode1.html">第1話から読む</a><a class="jp-btn" href="episode{latest["no"]}.html">最新話から読む</a></div></section>
<nav class="jp-tabs"><button class="jp-tab active" data-tab="episodes">話</button><button class="jp-tab" data-tab="comics">コミックス</button><button class="jp-tab" data-tab="info">作品情報</button></nav>
<section id="episodes" class="jp-panel active">
<div class="episode-sort-header">
  <span>全{n_ep}話</span>
  <div class="sort-switch episode-sort">
    <button type="button" class="sort-btn active" data-order="asc">1話から</button>
    <span>|</span>
    <button type="button" class="sort-btn" data-order="desc">最新話から</button>
  </div>
</div>
<div class="range-bar">{ranges}
</div>
<div>{rows}</div></section>

<section id="comics" class="jp-panel">
  <div class="comics-header">
    <span>全{len(volumes)}巻</span>
    <div class="sort-switch comics-sort">
      <button type="button" class="sort-btn active" data-order="asc">1巻から</button>
      <span>|</span>
      <button type="button" class="sort-btn" data-order="desc">最新巻から</button>
    </div>
  </div>
  <div class="volume-list">{tiles}</div>
</section>

<section id="info" class="jp-panel">
  <div class="info-panel">
    <div class="work-intro">
      <div class="work-catch">{e(work["catch"])}</div>
      <p class="work-summary">{e(work["summary"])}</p>
      <div class="author-chip">{e(work["author"])}</div>
      <div class="info-links">
        <a class="jp-btn" href="demon-encyclopedia.html">DEMON図鑑</a>
        <a class="jp-btn" href="correlation.html">相関図</a>
      </div>
    </div>

    {line_html}

    <div class="info-section">
      <h2>同じ作者の作品</h2>
      {cards}
    </div>
  </div>
</section>
<div class="continue-bar"><a href="episode{latest["no"]}.html">最新話 第{latest["no"]}話を読む</a></div>
</div>
<script src="js/top.js?v={V_TOP}"></script></body></html>
'''


# ---------------------------------------------------------------- 読書ページ
LOCK = '''<section class="protected-lock" id="protected-lock" aria-labelledby="protected-lock-title">
  <div class="protected-lock-card">
    <div class="protected-lock-mark" aria-hidden="true">🔒</div>
    <h1 id="protected-lock-title">この話はパスワードが必要です</h1>
    <p>この話は限定公開です。<br>パスワードを入力すると漫画を読めます。</p>
    <form class="protected-lock-form" id="protected-lock-form">
      <label class="sr-only" for="protected-password">パスワード</label>
      <input id="protected-password" name="password" type="password" autocomplete="current-password" inputmode="text" placeholder="パスワード" required>
      <button id="protected-submit" type="submit">読む</button>
      <p class="protected-lock-error" id="protected-error" role="alert" aria-live="polite"></p>
    </form>
  </div>
</section>'''


def manga_page(src, prot, alt, i, eager, cover=False):
    attr = ' data-volume-cover="true"' if cover else ""
    if prot:
        return f'<div class="manga-page"{attr}><img data-protected-src="{src}" alt="{e(alt)}"></div>'
    lazy = "" if i < eager else ' loading="lazy"'
    return f'<div class="manga-page"{attr}><img{lazy} src="{src}" alt="{e(alt)}"></div>'


def reader_page(title, page_title, desc, url, items, protected, volume_reader, back_href, back_text, vol, nav_html, footer):
    pages = "".join(manga_page(s, p, a, i, 3, c) for i, (s, p, a, c) in enumerate(items))
    vattr = f' data-volume-href="volume{vol["no"]}.html" data-volume-label="第{vol["no"]}巻"' if vol else ""
    extra = ""
    body_cls = "reader-page protected-locked" if protected else "reader-page"
    tail = f'<script src="js/viewer.js?v={V_VIEWER}"></script>' + (f'<script src="js/protected-reader.js?v={V_PROT}"></script>' if protected else "")
    return (head(page_title, desc, url, "article", theme=True, extra=extra)
            + f'<body class="{body_cls}">{LOCK if protected else ""}<header class="reader-bar"><div class="reader-bar-inner"><div class="reader-title"><a id="context-back" href="{back_href}">{back_text}</a></div>'
              f'<div class="reader-controls"><button class="small-btn" id="top" type="button">先頭へ</button></div></div>'
              f'<div class="progress" aria-hidden="true"><div id="progress-fill"></div></div></header>'
              f'<main class="viewer" id="viewer" data-volume-reader="{str(volume_reader).lower()}"{vattr}>{pages}</main>{nav_html}'
              f'<div class="page-nav"><button id="prev" type="button">← 次のページ</button><button id="next" type="button">前のページ →</button></div>'
              f'<div class="counter" id="counter">1 / {len(items)}</div>'
              f'<div class="reader-footer">{footer}</div>{tail}</body></html>\n')


EXTRA_LINKS = '　|　<a href="demon-encyclopedia.html">DEMON図鑑</a>　|　<a href="correlation.html">相関図</a>'


def episode_page(ep):
    n = ep["no"]
    items = [(src, prot, f"第{n}話 ページ {i + 1}", False) for i, (src, prot) in enumerate(pages_of[n])]
    v = vol_of_ep.get(n)
    links = []
    if n + 1 in pub_by_no:
        links.append(f'<a class="small-btn" href="episode{n + 1}.html">← 第{n + 1}話</a>')
    if v:
        links.append(f'<a class="small-btn" href="volume{v["no"]}.html">第{v["no"]}巻の目次</a>')
    if n - 1 in pub_by_no:
        links.append(f'<a class="small-btn" href="episode{n - 1}.html">第{n - 1}話 →</a>')
    nav = f'<div class="episode-nav">{"".join(links)}</div>' if links else ""
    footer = '<a href="index.html">HOME</a>' + (f'　|　<a href="volume{v["no"]}.html">第{v["no"]}巻</a>' if v else "") + EXTRA_LINKS
    t = f'第{n}話「{ep["title"]}」'
    return reader_page(t, f'{t} | {TITLE}', f'オリジナル漫画『{TITLE}』{t}', f"{BASE}episode{n}.html", items,
                       bool(ep.get("protected")), False, "index.html", "← 話一覧へ戻る", v, nav, footer)


def volume_page(v):
    no = v["no"]
    items = [(img(f"pages/volume{no}-cover"), False, f"{TITLE} 第{no}巻 表紙", True)]
    for n in v["episodes"]:
        items += [(src, prot, f"第{n}話 ページ {i + 1}", False) for i, (src, prot) in enumerate(pages_of[n])]
    footer = '<a href="index.html">HOME</a>　|　<a href="index.html#comics">コミックス一覧</a>' + EXTRA_LINKS
    t = f"第{no}巻"
    return reader_page(t, f"{t} | {TITLE}", f"オリジナル漫画『{TITLE}』{t}", f"{BASE}volume{no}.html", items,
                       bool(v.get("protected")), True, "index.html#comics", "← コミックス一覧へ戻る", None, "", footer)


# ---------------------------------------------------------------- 図鑑・相関図・404
def site_header(with_corr):
    corr = '<a href="correlation.html">相関図</a>' if with_corr else ""
    return (f'<header class="site-header"><div class="header-inner"><a class="brand" href="index.html">{e(TITLE)}<small>OGRE KINGDOM</small></a>\n'
            f'<nav><a href="index.html#comics">漫画</a><a href="demon-encyclopedia.html">DEMON図鑑</a>{corr}</nav></div></header>\n')


SITE_FOOT = f'<footer><a href="index.html">HOMEへ戻る</a>　|　{e(site["copyright"])}</footer></body></html>\n'


def demon_page():
    d = data["demon_encyclopedia"]
    arts = "".join(f'<article id="no{x["no"]}"><img src="{img("pages/demon-%03d" % x["no"])}" alt="DEMON図鑑 No.{x["no"]} {e(x["name"])}">'
                   f'<div class="card-body"><span class="badge">No.{x["no"]}</span><strong>{e(x["name"])}</strong></div></article>' for x in d)
    return (head(f"DEMON図鑑 | {TITLE}", f"{TITLE} DEMON図鑑 No.1〜No.{len(d)}", f"{BASE}demon-encyclopedia.html", "article") + "<body>\n" + site_header(False)
            + f'<main class="dictionary-page"><div class="kicker">DEMON ENCYCLOPEDIA</div><h1>DEMON図鑑</h1>\n'
              f'<p class="lead">DEMON図鑑 No.1〜No.{len(d)}をカラー原稿でまとめて閲覧できます。</p>\n<div class="dict-full">{arts}</div></main>\n' + SITE_FOOT)


def correlation_page():
    return (head(f"相関図 | {TITLE}", f"{TITLE} 相関図", f"{BASE}correlation.html", "article") + "<body>\n" + site_header(True)
            + f'<main class="dictionary-page"><div class="kicker">CHARACTER RELATIONSHIP</div><h1>相関図</h1>\n'
              f'<p class="lead">登場人物・組織・勢力の関係をまとめた相関図です。</p>\n'
              f'<div class="dict-full"><article><img src="{img("pages/correlation-chart")}" alt="{e(TITLE)} 相関図"></article></div></main>\n' + SITE_FOOT)


def not_found_page():
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>ページが見つかりません | {e(TITLE)}</title>
<link rel="icon" href="{BASE}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{BASE}css/style.css?v={V_CSS}"></head>
<body class="top-page"><div class="jp-shell"><div class="nf">
<p class="nf-code" aria-hidden="true">404</p>
<h1>ページが見つかりません</h1>
<p>URLがまちがっているか、ページが移動したのかもしれません。</p>
<div class="jp-actions" style="justify-content:center"><a class="jp-btn primary" href="{BASE}">{e(TITLE)}のトップへ</a></div>
</div></div></body></html>
'''


def write(path, text):
    open(path, "w", encoding="utf-8", newline="\n").write(text)


write("index.html", index_page())
for ep in published:
    write(f"episode{ep['no']}.html", episode_page(ep))
for v in volumes:
    write(f"volume{v['no']}.html", volume_page(v))
write("demon-encyclopedia.html", demon_page())
write("correlation.html", correlation_page())
write("404.html", not_found_page())
print(f"完了: index.html, 話{len(published)}（準備中{len(episodes) - len(published)}）, 巻{len(volumes)}, 図鑑, 相関図, 404.html")
