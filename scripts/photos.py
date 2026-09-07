# -*- coding: utf-8 -*-
"""Pexels 직접 이미지 URL로 사진을 받아 자르고 base64로 인코딩한다.
API 키가 필요 없다 (사진 ID는 themes.py에 미리 담아 둔 목록에서 고른다).
"""
import base64
import io
import urllib.request

from PIL import Image, ImageEnhance

UA = "Mozilla/5.0 (compatible; escape-game-factory/1.0)"


def fetch(pid, w=1100, timeout=40):
    url = ("https://images.pexels.com/photos/%d/pexels-photo-%d.jpeg"
           "?auto=compress&cs=tinysrgb&w=%d" % (pid, pid, w))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    if len(data) < 3000:
        raise IOError("too small: %d" % pid)
    return Image.open(io.BytesIO(data)).convert("RGB")


def crop_to(im, W, H, yb=0.35):
    tw = W / float(H)
    if im.width / float(im.height) > tw:
        nw = int(im.height * tw)
        x = (im.width - nw) // 2
        im = im.crop((x, 0, x + nw, im.height))
    else:
        nh = int(im.width / tw)
        y = int((im.height - nh) * yb)
        im = im.crop((0, y, im.width, y + nh))
    return im.resize((W, H), Image.LANCZOS)


def enc(im, q=68):
    b = io.BytesIO()
    im.save(b, "JPEG", quality=q, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def scene(pid, W=860, H=300, q=66, sat=1.05):
    im = ImageEnhance.Color(crop_to(fetch(pid), W, H)).enhance(sat)
    return enc(im, q)


def square(pid, size=300, q=70):
    return enc(crop_to(fetch(pid, 600), size, size), q)


PLACEHOLDER = ("data:image/svg+xml;base64," + base64.b64encode(
    ('<svg xmlns="http://www.w3.org/2000/svg" width="860" height="300">'
     '<rect width="860" height="300" fill="#2b2118"/>'
     '<text x="430" y="160" font-size="26" text-anchor="middle" fill="#8a7a66">'
     'photo unavailable</text></svg>').encode()).decode())


def safe(fn, *a, **k):
    try:
        return fn(*a, **k)
    except Exception as e:          # 네트워크 실패해도 게임은 만들어진다
        print("  ! photo failed (%s) — placeholder 사용" % e)
        return PLACEHOLDER
