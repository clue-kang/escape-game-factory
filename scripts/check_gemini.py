# -*- coding: utf-8 -*-
"""GEMINI_API_KEY 가 제대로 들어갔는지 점검한다.

  python scripts/check_gemini.py [사진경로]

키가 없거나 잘못돼도 게임 생성은 계속 동작한다(OCR로 내려감).
이 스크립트는 '키가 살아 있는지'만 확인한다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze import PROMPT, _parse                      # noqa: E402
import gemini                                            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(ROOT, "samples", "sample-problem.png")


def out(k, v):
    p = os.environ.get("GITHUB_OUTPUT")
    if p:
        with open(p, "a", encoding="utf-8") as f:
            f.write("%s=%s\n" % (k, v))


def main():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print("❌ GEMINI_API_KEY 가 비어 있습니다.")
        print("   저장소 Settings → Secrets and variables → Actions → New repository secret")
        print("   이름을 정확히 GEMINI_API_KEY 로 만들어 주세요.")
        out("result", "키 없음")
        return 1

    print("· 키 길이: %d자 (앞 4자리 %s…)" % (len(key), key[:4]))

    print("\n[1] 쓸 수 있는 모델 확인")
    try:
        models = gemini.list_models(key)
    except Exception as e:
        print("❌ 모델 목록을 못 받았습니다:", e)
        out("result", "모델 목록 실패")
        return 1
    if not models:
        print("❌ generateContent 가능한 모델이 없습니다.")
        out("result", "모델 없음")
        return 1
    print("   후보 %d개 — 우선순위: %s" % (len(models), ", ".join(models[:5])))

    img = sys.argv[1] if len(sys.argv) > 1 else SAMPLE
    if not os.path.exists(img):
        print("\n⚠️ 시험용 사진이 없어 글자만으로 시험합니다.")
        img_paths = []
    else:
        img_paths = [img]
        print("\n[2] 사진으로 실제 분석 시험 — %s" % os.path.basename(img))

    try:
        text, model = gemini.ask(key, PROMPT if img_paths else "OK 라고만 답하세요.", img_paths)
    except Exception as e:
        print("❌ 호출 실패:", e)
        print("   키가 틀렸거나, 사용량 한도이거나, 결제 설정이 필요할 수 있습니다.")
        out("result", "호출 실패")
        return 1

    print("   사용 모델: %s" % model)
    print("   응답: %s" % text.strip().replace("\n", " ")[:160])

    if img_paths:
        types = _parse(text)
        if types:
            print("\n✅ 성공 — 사진에서 찾아낸 문제 유형: %s" % ", ".join(types))
            out("result", "성공 (%s) → %s" % (model, ", ".join(types)))
        else:
            print("\n⚠️ 호출은 됐지만 유형을 못 골랐습니다. (사진이 흐리거나 문제집이 아닐 수 있어요)")
            out("result", "호출은 성공, 유형 인식 실패 (%s)" % model)
    else:
        print("\n✅ 키는 살아 있습니다 (%s)" % model)
        out("result", "키 정상 (%s)" % model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
