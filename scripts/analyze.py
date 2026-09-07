# -*- coding: utf-8 -*-
"""문제집 사진에서 '어떤 유형의 문제인지'만 알아낸다.

우선순위대로 시도하고, 전부 실패하면 랜덤 유형으로 넘어간다.
게임은 어떤 경우에도 만들어진다.

  1) GEMINI_API_KEY   → Gemini 비전 (무료 등급 있음)
  2) ANTHROPIC_API_KEY → Claude 비전
  3) pytesseract      → 한국어 OCR + 키워드
  4) 이슈 본문 키워드
  5) 랜덤
"""
import base64
import json
import os
import re
import urllib.request

from generators import ALL_TYPES, KEYWORDS

PROMPT = (
    "이 사진은 초등 저학년 사고력 수학 문제집 페이지입니다.\n"
    "아래 유형 중 이 페이지에 실제로 등장하는 것만 골라 JSON 배열로만 답하세요.\n"
    "설명·마크다운·코드펜스 없이 배열만 출력합니다.\n\n"
    "유형: " + ", ".join(ALL_TYPES) + "\n\n"
    "cond2=조건에 맞는 두 자리 수, cond3=조건에 맞는 세 자리 수, cards=수 카드로 만든 수,\n"
    "balance=저울 무게 비교, sudoku4=스도쿠, magic3=마방진, maxpath=격자 경로,\n"
    "newop=새로운 연산 기호 약속, twenty=질문·대답으로 수 맞히기, abc=여러 사람의 개수 관계 추리,\n"
    "seq=수 배열 규칙, ancient=기호로 나타낸 수 해독\n\n"
    '예시 출력: ["cond2","balance","seq"]'
)


def _post(url, body, headers, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _parse(text):
    m = re.search(r"\[[^\]]*\]", text, re.S)
    if not m:
        return []
    try:
        arr = json.loads(m.group(0))
    except Exception:
        return []
    return [t for t in arr if isinstance(t, str) and t in ALL_TYPES]


def _gemini(paths, key):
    """모델은 gemini.py가 자동으로 고른다 (은퇴 대비)"""
    from gemini import ask
    text, model = ask(key, PROMPT, paths)
    print("  · Gemini 모델: %s" % model)
    return _parse(text), model


def _claude(paths, key):
    content = [{"type": "text", "text": PROMPT}]
    for p in paths[:3]:
        content.append({"type": "image", "source": {
            "type": "base64", "media_type": "image/jpeg",
            "data": base64.b64encode(open(p, "rb").read()).decode()}})
    r = _post("https://api.anthropic.com/v1/messages",
              {"model": "claude-sonnet-5", "max_tokens": 300,
               "messages": [{"role": "user", "content": content}]},
              {"Content-Type": "application/json", "x-api-key": key,
               "anthropic-version": "2023-06-01"})
    return _parse(r["content"][0]["text"])


def _ocr(paths):
    try:
        import pytesseract
        from PIL import Image
    except Exception:
        return []
    text = ""
    for p in paths[:3]:
        im = Image.open(p)
        for angle in (0, 90, 270):
            try:
                text += pytesseract.image_to_string(im.rotate(angle, expand=True), lang="kor")
            except Exception:
                pass
    return _from_text(text)


def _from_text(text):
    hits = []
    for kw, t in KEYWORDS.items():
        if kw in text and t not in hits:
            hits.append(t)
    return hits


def detect(paths, issue_text=""):
    """(유형 리스트, 사용한 방법) 반환"""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key and paths:
        try:
            t, model = _gemini(paths, key)
            if t:
                return t, "Gemini 사진 분석 (%s)" % model
            print("  ! Gemini가 유형을 못 골랐습니다 — 다음 방법으로")
        except Exception as e:
            print("  ! Gemini 실패:", e)
    elif key and not paths:
        print("  · 사진이 없어 Gemini를 건너뜁니다")
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key and paths:
        try:
            t = _claude(paths, key)
            if t:
                return t, "Claude 사진 분석"
        except Exception as e:
            print("  ! Claude 실패:", e)
    if paths:
        try:
            t = _ocr(paths)
            if t:
                return t, "OCR 키워드 인식"
        except Exception as e:
            print("  ! OCR 실패:", e)
    t = _from_text(issue_text or "")
    if t:
        return t, "이슈 글 키워드"
    return [], "랜덤 (분석 없음)"
