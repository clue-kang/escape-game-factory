# -*- coding: utf-8 -*-
"""Gemini 비전 호출.

모델 이름을 하드코딩하지 않는다. 계정에서 실제로 쓸 수 있는 모델 목록을 받아
비전이 되는 flash 계열 중 최신을 골라 쓰고, 실패하면 다음 후보로 넘어간다.
(모델이 은퇴해도 코드를 고칠 필요가 없다.)
"""
import base64
import io
import json
import re
import urllib.error
import urllib.request

BASE = "https://generativelanguage.googleapis.com/v1beta"
FALLBACK = ["gemini-2.5-flash", "gemini-2.0-flash"]
SKIP = ("embedding", "aqa", "tts", "imagen", "image-generation", "live",
        "veo", "learnlm", "audio")


def _get(url, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(
            url, headers={"User-Agent": "escape-game-factory"}), timeout=timeout) as r:
        return json.loads(r.read().decode())


def _post(url, body, timeout=90):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def list_models(key):
    """generateContent 가능한 모델을 좋은 순서로 정렬해 반환"""
    try:
        data = _get("%s/models?key=%s&pageSize=200" % (BASE, key))
    except Exception:
        return list(FALLBACK)
    names = []
    for m in data.get("models", []):
        n = m.get("name", "").split("/")[-1]
        if "generateContent" not in (m.get("supportedGenerationMethods") or []):
            continue
        if any(b in n for b in SKIP):
            continue
        names.append(n)

    def score(n):
        v = re.search(r"gemini-(\d+(?:\.\d+)?)", n)
        return (1 if "flash" in n else 0,               # flash 우선 (무료 등급)
                float(v.group(1)) if v else 0.0,        # 최신 버전 우선
                0 if "lite" in n else 1,                # lite 아닌 쪽
                0 if ("preview" in n or "exp" in n) else 1)   # 정식판 우선

    names.sort(key=score, reverse=True)
    return names or list(FALLBACK)


def _shrink(path, maxpx=1400, q=80):
    """사진을 줄여 base64 크기를 낮춘다"""
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        if max(im.size) > maxpx:
            r = maxpx / float(max(im.size))
            im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
        b = io.BytesIO()
        im.save(b, "JPEG", quality=q, optimize=True)
        return b.getvalue()
    except Exception:
        return open(path, "rb").read()


def _text(resp):
    parts = (resp.get("candidates") or [{}])[0].get("content", {}).get("parts", []) or []
    return "\n".join(p.get("text", "") for p in parts if isinstance(p, dict))


def ask(key, prompt, image_paths, tries=3):
    """(응답 텍스트, 사용한 모델) 반환. 전부 실패하면 예외."""
    parts = [{"text": prompt}]
    for p in image_paths[:3]:
        parts.append({"inline_data": {"mime_type": "image/jpeg",
                                      "data": base64.b64encode(_shrink(p)).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 400}}
    last = None
    for model in list_models(key)[:tries]:
        try:
            r = _post("%s/models/%s:generateContent?key=%s" % (BASE, model, key), body)
            t = _text(r)
            if t.strip():
                return t, model
            last = "빈 응답 (%s)" % model
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = e.read().decode()[:200]
            except Exception:
                pass
            last = "%s → HTTP %s %s" % (model, e.code, detail)
        except Exception as e:
            last = "%s → %s" % (model, e)
        print("  · %s 실패, 다음 모델 시도" % model)
    raise RuntimeError(last or "사용 가능한 모델 없음")
