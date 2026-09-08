# -*- coding: utf-8 -*-
"""이슈 하나 → 방탈출 게임 HTML 한 개.

사용법:
  python scripts/build_game.py --issue issue.json [--out docs/games]
  python scripts/build_game.py --demo            # 로컬 미리보기(이슈 없이)
"""
import argparse
import datetime
import html
import json
import os
import random
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generators as G          # noqa: E402
import photos as P              # noqa: E402
from analyze import detect      # noqa: E402
from themes import THEMES, OBJECTS, by_key   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMG_RE = re.compile(r'!\[[^\]]*\]\((https?://[^)\s]+)\)|<img[^>]+src="(https?://[^"]+)"')
ZONE_SPLIT = [3, 2, 2, 3]        # 구역별 문제 수 (합 10)
TITLE_RE = re.compile(r"^\s*(?:제목|title)\s*[:：]\s*(.+)$", re.M | re.I)


class _DropAuthOnRedirect(urllib.request.HTTPRedirectHandler):
    """비공개 저장소 첨부는 서명 URL로 리다이렉트된다.
    이때 Authorization 헤더를 같이 보내면 저장소 서버가 403으로 거절하므로 떼어낸다."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        r = super().redirect_request(req, fp, code, msg, headers, newurl)
        if r is not None:
            for h in list(r.headers):
                if h.lower() == "authorization":
                    del r.headers[h]
            r.unredirected_hdrs.pop("Authorization", None)
        return r


_OPENER = urllib.request.build_opener(_DropAuthOnRedirect)


def download_images(body, outdir):
    os.makedirs(outdir, exist_ok=True)
    urls = []
    for m in IMG_RE.finditer(body or ""):
        u = m.group(1) or m.group(2)
        if u and u not in urls:
            urls.append(u)
    tok = os.environ.get("GITHUB_TOKEN", "")
    paths = []
    for i, u in enumerate(urls[:5]):
        try:
            req = urllib.request.Request(u, headers={
                "User-Agent": "Mozilla/5.0 (escape-game-factory)",
                **({"Authorization": "Bearer " + tok} if tok else {})})
            with _OPENER.open(req, timeout=60) as r:
                data = r.read()
            if len(data) < 2000:
                continue
            p = os.path.join(outdir, "img%d.jpg" % i)
            # PIL로 다시 저장해 형식을 통일 (png/heic 등 대응)
            from PIL import Image
            import io
            Image.open(io.BytesIO(data)).convert("RGB").save(p, "JPEG", quality=85)
            paths.append(p)
        except Exception as e:
            print("  ! 이미지 내려받기 실패:", u[:60], e)
    return paths


def pick_theme(rng, text):
    """이슈 글에 테마 이름·키·한글 별칭이 있으면 그걸로, 없으면 랜덤"""
    raw = text or ""
    low = raw.lower()
    hits = []
    for th in THEMES:
        for w in [th["key"], th["name"]] + th.get("alias", []):
            if (w.lower() in low) if w.isascii() else (w in raw):
                hits.append((len(w), th))
                break
    if hits:
        hits.sort(key=lambda x: -x[0])      # 가장 긴(구체적인) 단어가 이김
        return hits[0][1]
    return rng.choice(THEMES)


def build(issue, outdir):
    title_in = (issue.get("title") or "").strip()
    body = issue.get("body") or ""
    number = issue.get("number") or 0

    seed = int(issue.get("seed") or 0) or random.randrange(1 << 30)
    rng = random.Random(seed)

    work = os.path.join(ROOT, ".work")
    paths = download_images(body, work) if body else []
    print("· 첨부 사진 %d장" % len(paths))

    if issue.get("types"):
        types, how = issue["types"], "유형 직접 지정"
    else:
        types, how = detect(paths, title_in + "\n" + body)
    print("· 문제 유형 판별: %s → %s" % (how, types or "(없음)"))

    qs = G.make(rng, types, OBJECTS)
    if len(qs) < 10:
        raise SystemExit("문제 생성 실패 (%d개)" % len(qs))

    theme = pick_theme(rng, title_in + " " + body)
    m = TITLE_RE.search(body or "")
    custom = (m.group(1).strip()[:40] if m else "")
    print("· 테마: %s %s%s" % (theme["emoji"], theme["name"],
                              (" (제목: %s)" % custom) if custom else ""))

    # 구역 배정
    zi, cnt = 0, 0
    for q in qs:
        q["zone"] = zi
        cnt += 1
        if cnt >= ZONE_SPLIT[zi] and zi < 3:
            zi += 1
            cnt = 0

    # 사진
    ph = {}
    print("· 사진 내려받는 중…")
    for k in ("hero", "end"):
        ph[k] = P.safe(P.scene, theme["photos"][k], 860, 392, 68)
    for k in ("z0", "z1", "z2", "z3"):
        ph[k] = P.safe(P.scene, theme["photos"][k], 860, 300, 66)
    for q in qs:
        for pid in q.get("chImg", []) or []:
            key = "obj%d" % pid
            if key not in ph:
                ph[key] = P.safe(P.square, pid)

    zones = []
    for i, z in enumerate(theme["zones"]):
        zones.append({"name": z["name"], "icon": z["icon"], "intro": z["intro"],
                      "clear": z["clear"], "ph": "z%d" % i,
                      "amb": theme["amb"][i] if i < len(theme["amb"]) else "cave"})

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    slug = ("game-%04d-%s" % (number, theme["key"])) if number else ("manual-%s-%s" % (stamp, theme["key"]))
    stars = "★" * 5 + "☆"
    game = {
        "slug": slug,
        "title": custom or theme["name"],
        "emoji": theme["emoji"],
        "subtitle": "7살 & 초2 협동 · 사고력 문제 %d개" % len(qs),
        "stars": stars,
        "gauge": theme["gauge"],
        "intro": theme["intro"],
        "heroCap": theme["heroCap"],
        "endCap": theme["endCap"],
        "photos": ph,
        "zones": zones,
        "qs": [{k: q[k] for k in
                ("id", "role", "title", "story", "ic", "prompt", "kind", "ans", "fig", "hints", "zone")
                if k in q} | ({"digits": q["digits"]} if q.get("digits") else {})
               | ({"ch": q["ch"], "chImg": q["chImg"], "balance": q["balance"]} if q.get("ch") else {})
               for q in qs],
    }

    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    c = theme["colors"]
    out = (tpl.replace("__TITLE__", html.escape(theme["emoji"] + " " + theme["name"]))
              .replace("__BG1__", c["bg1"]).replace("__BG2__", c["bg2"])
              .replace("__LINE__", c["line"]).replace("__AMBER__", c["amber"])
              .replace("__LIME__", c["lime"]).replace("__PAPER__", c["paper"])
              .replace("__DATA__", json.dumps(game, ensure_ascii=False)))

    os.makedirs(outdir, exist_ok=True)
    dest = os.path.join(outdir, slug + ".html")
    open(dest, "w", encoding="utf-8").write(out)
    kb = os.path.getsize(dest) // 1024
    print("· 저장: %s (%d KB)" % (dest, kb))

    meta = {"slug": slug, "title": custom or theme["name"], "emoji": theme["emoji"],
            "issue": number, "seed": seed, "how": how,
            "types": [q["type"] for q in qs],
            "answers": {str(q["id"]): q["ans"] for q in qs},
            "date": datetime.date.today().isoformat()}
    return meta


def write_index(docs):
    idx = os.path.join(docs, "index.html")
    games = []
    metadir = os.path.join(docs, "meta")
    if os.path.isdir(metadir):
        for f in sorted(os.listdir(metadir), reverse=True):
            if f.endswith(".json"):
                try:
                    games.append(json.load(open(os.path.join(metadir, f), encoding="utf-8")))
                except Exception:
                    pass
    cards = "".join(
        '<a class="g" href="games/%s.html"><span class="e">%s</span>'
        '<span class="t">%s</span><span class="d">#%s · %s</span></a>'
        % (g["slug"], g["emoji"], html.escape(g["title"]), g.get("issue", "-"), g.get("date", ""))
        for g in games)
    open(idx, "w", encoding="utf-8").write(
        '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>🎮 방탈출 게임 목록</title><style>'
        'body{margin:0;padding:24px 16px 60px;background:#12100c;color:#f5ece0;'
        "font-family:'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif}"
        'h1{text-align:center;font-size:1.6rem;margin:.2em 0}'
        'p.s{text-align:center;color:#b9a88f;font-size:.9rem;margin-bottom:22px}'
        '.wrap{max-width:720px;margin:0 auto;display:grid;gap:12px}'
        '.g{display:flex;align-items:center;gap:14px;padding:16px 18px;border-radius:16px;'
        'background:#221b12;border:1px solid rgba(224,161,58,.3);text-decoration:none;color:inherit}'
        '.g:active{transform:scale(.99)}.e{font-size:2rem}'
        '.t{font-size:1.15rem;font-weight:800;flex:1}.d{color:#b9a88f;font-size:.82rem}'
        '</style></head><body><h1>🎮 방탈출 게임 목록</h1>'
        '<p class="s">이슈에 문제집 사진을 올리면 새 게임이 여기에 추가돼요</p>'
        '<div class="wrap">' + (cards or '<p class="s">아직 만들어진 게임이 없어요.</p>') +
        '</div></body></html>')
    print("· 목록 갱신: %d개" % len(games))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--docs", default=os.path.join(ROOT, "docs"),
                    help="게임 목록·메타를 쓸 폴더 (기본: 이 저장소의 docs)")
    ap.add_argument("--out", help="게임 HTML 저장 폴더 (기본: <docs>/games)")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--types", help="유형 직접 지정 (쉼표 구분, 분석 건너뜀)")
    a = ap.parse_args()

    if a.demo or not a.issue:
        issue = {"title": "데모", "body": "", "number": 0}
    else:
        issue = json.load(open(a.issue, encoding="utf-8"))
    if a.seed:
        issue["seed"] = a.seed
    if a.types:
        issue["types"] = [t.strip() for t in a.types.split(",") if t.strip()]

    outdir = a.out or os.path.join(a.docs, "games")
    meta = build(issue, outdir)

    md = os.path.join(a.docs, "meta")
    os.makedirs(md, exist_ok=True)
    json.dump(meta, open(os.path.join(md, meta["slug"] + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    write_index(a.docs)

    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a", encoding="utf-8") as f:
            f.write("slug=%s\n" % meta["slug"])
            f.write("title=%s\n" % meta["title"])
            f.write("emoji=%s\n" % meta["emoji"])
            f.write("how=%s\n" % meta["how"])
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
