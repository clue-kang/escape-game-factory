# 🎮 방탈출 게임 공장

**문제집 사진을 GitHub 이슈에 올리면 → 방탈출 게임이 자동으로 만들어집니다.**
7살 & 초2 남매가 같이 푸는 협동 방탈출이고, 사고력 수학 문제 10개가 들어갑니다.

## 쓰는 법

1. **[Issues](../../issues/new/choose) → 🎮 방탈출 게임 만들기**
2. 칸에 **문제집 사진을 붙여넣고** 제출
3. 1~2분 뒤 이슈에 **게임 링크**가 댓글로 달립니다
4. 폰·태블릿에서 링크를 눌러 바로 플레이

만들어진 게임 목록 → **[게임 목록 페이지](https://clue-kang.github.io/escape-game-factory/)**

사진 없이 그냥 이슈만 열어도 랜덤 문제로 게임이 만들어집니다.
Actions 탭 → **방탈출 게임 만들기 → Run workflow** 로도 돌릴 수 있어요.

---

## 어떻게 돌아가나

```
이슈에 사진 업로드
      ↓
① 사진에서 "어떤 유형의 문제인지"만 판별      ← analyze.py
      ↓
② 그 유형으로 새 문제 10개를 코드가 생성       ← generators.py
   (정답이 유일한지 완전탐색으로 검증)
      ↓
③ 랜덤 테마 + Pexels 실사 사진 내려받기        ← themes.py / photos.py
      ↓
④ 게임 HTML 한 개로 조립 (사진은 파일에 내장)  ← template.html
      ↓
⑤ docs/ 에 커밋 → GitHub Pages 링크를 댓글로
```

**핵심: 문제와 정답은 AI가 아니라 코드가 만듭니다.**
AI는 "이 페이지엔 저울·마방진 유형이 있다"는 판별만 하고, 실제 문제는 생성기가 만들면서
가능한 모든 답을 완전탐색해 **정답이 하나뿐인지 검증**합니다. 답이 두 개거나 틀린 문제는 나오지 않습니다.

### 사진 분석은 이 순서로 시도합니다

| 순서 | 방법 | 필요한 것 | 없으면 |
|---|---|---|---|
| 1 | Gemini 비전 | `GEMINI_API_KEY` 시크릿 | 다음으로 |
| 2 | Claude 비전 | `ANTHROPIC_API_KEY` 시크릿 | 다음으로 |
| 3 | 한국어 OCR + 키워드 | 없음 (자동 설치) | 다음으로 |
| 4 | 이슈 글의 키워드 | 없음 | 다음으로 |
| 5 | 랜덤 유형 | 없음 | — |

**키를 하나도 넣지 않아도 게임은 항상 만들어집니다.** 3~5단계로 자동으로 내려갑니다.
사진을 제대로 읽게 하고 싶으면 [Google AI Studio](https://aistudio.google.com/apikey)에서
무료 키를 받아 `Settings → Secrets and variables → Actions` 에 `GEMINI_API_KEY` 로 넣으세요.

---

## 들어가는 문제 유형 12가지

문제집(팩토 영재교육원 대비 / 소마 사고력수학 PREMIER) 유형을 그대로 옮겼습니다.

| 키 | 유형 | 난이도 |
|---|---|---|
| `seq` | 수 배열 규칙 (등차·등비·계차·피보나치·교차) | 👶 |
| `cards` | 수 카드로 만든 수 — N번째로 큰/작은 수 | 👶 |
| `ancient` | 기호로 나타낸 고대의 수 해독 | 👶 |
| `balance` | 저울 무게 비교 (삼단논법) | 👶 |
| `sudoku4` | 4×4 미니 스도쿠 | 🧒 |
| `magic3` | 3×3 마방진 | 🧒 |
| `cond2` | 조건에 맞는 두 자리 수 | 🧒 |
| `abc` | 세 사람의 개수 관계 추리 | 🧒 |
| `cond3` | 조건에 맞는 세 자리 수 | 🧒 |
| `newop` | 새로운 연산 기호 약속 | 👫 |
| `twenty` | 스무고개로 수 맞히기 | 👫 |
| `maxpath` | 격자에서 최대 경로 찾기 | 👫 |

👶 7살 담당 / 🧒 초2 담당 / 👫 둘이 함께 — 문제마다 담당이 표시됩니다.

## 테마 6가지

🌴 잃어버린 정글 · 🚀 우주 정거장 X · 🌊 심해 잠수함 · 🏰 마법의 성 · 🌋 불의 협곡 · 🍭 사탕 공장

테마마다 사진·색·구역 이름·배경음이 전부 다릅니다.
사진은 [Pexels](https://www.pexels.com) 무료 라이선스, 소리는 Web Audio로 합성(파일 없음)합니다.

---

## 로컬에서 만들어 보기

```bash
pip install pillow
python scripts/build_game.py --demo --seed 42
# docs/games/demo-*.html 생성
```

## 폴더

```
scripts/
  build_game.py    이슈 → 게임 (전체 흐름)
  generators.py    문제 생성기 12종 + 정답 유일성 검증
  themes.py        테마 6종 + Pexels 사진 ID
  photos.py        사진 내려받기 · 자르기 · base64 내장
  analyze.py       사진 → 문제 유형 (Gemini/Claude/OCR/랜덤)
  template.html    게임 템플릿 (색·데이터만 갈아끼움)
docs/
  index.html       게임 목록 (자동 갱신)
  games/*.html     완성된 게임 (파일 하나로 오프라인 실행 가능)
  meta/*.json      생성 기록 (정답 포함)
```

## 설정

- **GitHub Pages**: `Settings → Pages → Source: main / docs`
- **Actions 쓰기 권한**: `Settings → Actions → General → Workflow permissions → Read and write`
