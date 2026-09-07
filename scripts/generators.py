# -*- coding: utf-8 -*-
"""사고력 수학 문제 생성기.

각 생성기는 매번 다른 숫자로 문제를 만들고, **정답이 유일한지 완전탐색으로 검증**한다.
검증에 실패하면 다시 뽑는다. 따라서 답이 두 개이거나 없는 문제는 나오지 않는다.
"""
from itertools import permutations, product

# ───────────────────────── SVG 도우미 (양피지 스타일)

def S(inner, w=420, h=380):
    return ('<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">%s</svg>' % (w, h, inner))

def PAPER(w, h):
    return ('<rect width="%d" height="%d" fill="#f3e6cb"/>'
            '<rect width="%d" height="%d" fill="none" stroke="#b58a45" stroke-width="6"/>' % (w, h, w, h))

def T(s, x, y, sz, col="#3b2a10", w=400, anchor="middle"):
    return ('<text x="%s" y="%s" font-size="%s" text-anchor="%s" font-weight="%s" fill="%s">%s</text>'
            % (x, y, sz, anchor, w, col, s))

def CLUE(lines, x, y, w, lh=32, fs=17):
    g = ('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="#fff8e6" '
         'stroke="#b58a45" stroke-width="3"/>' % (x, y, w, len(lines) * lh + 20))
    for i, l in enumerate(lines):
        g += T(l, x + 16, y + 30 + i * lh, fs, anchor="start")
    return g

def CELLS(vals, x0, y0, cw, ch, cols, hi=None):
    """숫자 격자. vals: 리스트(문자열), hi: 강조할 인덱스 집합"""
    hi = hi or set()
    g = ""
    for i, v in enumerate(vals):
        x = x0 + (i % cols) * cw
        y = y0 + (i // cols) * ch
        fill = "#fee2e2" if i in hi else "#fff8e6"
        stroke = "#c0392b" if i in hi else "#8a6a30"
        g += ('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="3"/>'
              % (x, y, cw, ch, fill, stroke))
        g += T(v, x + cw // 2, y + ch // 2 + 12, min(34, int(ch * .5)),
               "#c0392b" if i in hi else "#3b2a10", 800)
    return g


# ───────────────────────── 1. 조건에 맞는 두 자리 수

def g_cond2(rng):
    for _ in range(400):
        t = rng.randint(2, 9)
        u = rng.randint(1, 9)
        if t == u:
            continue
        n = t * 10 + u
        s, d = t + u, abs(t - u)
        big = "십의 자리" if t > u else "일의 자리"
        lo = (n // 10) * 10 - rng.choice([10, 20])
        hi = lo + rng.choice([20, 30])
        if not (lo < n < hi):
            continue
        odd = n % 2 == 1
        cands = [x for x in range(10, 100)
                 if (x // 10) + (x % 10) == s
                 and abs(x // 10 - x % 10) == d
                 and ((x % 2 == 1) == odd)
                 and lo < x < hi]
        if len(cands) != 1:
            continue
        lines = [
            "① 두 자리 수입니다.",
            "② %s입니다." % ("홀수" if odd else "짝수"),
            "③ %s 숫자가 %s 숫자보다" % (big, "일의 자리" if t > u else "십의 자리"),
            "     %d 큽니다." % d,
            "④ 각 자리 숫자의 합은 %d입니다." % s,
            "⑤ %d보다 크고 %d보다 작습니다." % (lo, hi),
        ]
        fig = S(PAPER(420, 320) + T("🪧 벽에 걸린 표지판", 210, 46, 20, w=800) +
                CLUE(lines, 24, 62, 372, 30, 16) +
                T("조건을 모두 만족하는 수는?", 210, 302, 18, w=700), 420, 320)
        return dict(type="cond2", title="표지판의 두 자리 수", ic="🪧",
                    story="표지판에는 조건만 잔뜩 적혀 있다.",
                    prompt="조건을 모두 만족하는 수는?", kind="num", digits=2, ans=str(n), fig=fig,
                    hints=["③번과 ④번을 같이 보자. 두 숫자의 <b>차는 %d</b>, <b>합은 %d</b>야." % (d, s),
                           "합이 %d이고 차가 %d인 두 수는 %d과 %d이야." % (s, d, max(t, u), min(t, u)),
                           "%s가 더 크니까 %d. 나머지 조건도 맞는지 확인 → 정답은 %d!" % (big, n, n)])
    return None


# ───────────────────────── 2. 조건에 맞는 세 자리 수

def g_cond3(rng):
    for _ in range(400):
        h = rng.randint(2, 8)
        d = rng.choice([1, 2, 3])
        u = rng.randint(1, 6)
        t = u + d
        if t > 9:
            continue
        n = h * 100 + t * 10 + u
        s = h + t + u
        if len({h, t, u}) != 3:
            continue
        cands = [x for x in range(100, 1000)
                 if x // 100 == h
                 and len({x // 100, (x // 10) % 10, x % 10}) == 3
                 and sum([x // 100, (x // 10) % 10, x % 10]) == s
                 and (x // 10) % 10 - x % 10 == d]
        if len(cands) != 1:
            continue
        lines = ["① %d00보다 크고 %d00보다 작습니다." % (h, h + 1),
                 "② 각 자리 숫자가 모두 다릅니다.",
                 "③ 각 자리 숫자의 합은 %d입니다." % s,
                 "④ 십의 자리 숫자가 일의 자리",
                 "     숫자보다 %d 큽니다." % d]
        fig = S(PAPER(420, 330) + T("🔒 세 자리 자물쇠", 210, 46, 20, w=800) +
                CLUE(lines, 24, 62, 372, 32, 17) +
                CELLS(["?", "?", "?"], 126, 240, 58, 58, 3, {0, 1, 2}) +
                T("조건에 맞는 세 자리 수는?", 210, 322, 18, w=700), 420, 330)
        return dict(type="cond3", title="세 자리 자물쇠", ic="🔒",
                    story="자물쇠에 세 칸이 비어 있다.",
                    prompt="조건에 맞는 세 자리 수는?", kind="num", digits=3, ans=str(n), fig=fig,
                    hints=["①번으로 백의 자리는 바로 정해져. %d00대니까 백의 자리는 %d!" % (h, h),
                           "합이 %d인데 백의 자리가 %d니까 십의 자리 + 일의 자리 = %d이야." % (s, h, t + u),
                           "합이 %d이고 차가 %d인 두 수는 %d과 %d. 정답은 %d!" % (t + u, d, t, u, n)])
    return None


# ───────────────────────── 3. 수 카드로 만든 수

def g_cards(rng):
    for _ in range(200):
        k = rng.choice([3, 3, 4])
        ds = rng.sample(range(1, 10), k)
        nums = sorted({a * 10 + b for a, b in permutations(ds, 2)}, reverse=True)
        big = rng.choice([True, False])
        rank = rng.randint(2, min(4, len(nums)))
        ans = nums[rank - 1] if big else sorted(nums)[rank - 1]
        if ans < 10:
            continue
        order = "큰" if big else "작은"
        cards = ""
        for i, d in enumerate(sorted(ds)):
            x = 40 + i * (340 // k)
            cards += ('<rect x="%d" y="120" width="72" height="100" rx="9" fill="#fffdf5" '
                      'stroke="#3b2a10" stroke-width="4"/>' % x) + T(str(d), x + 36, 188, 52, w=800)
        fig = S(PAPER(420, 340) + T("🃏 흩어진 수 카드", 210, 52, 20, w=800) + cards +
                T("카드 두 장을 골라 두 자리 수를 만들어요", 210, 266, 17, "#6b5430") +
                T("(같은 카드를 두 번 쓸 수 없어요)", 210, 294, 16, "#6b5430") +
                T("%d번째로 %s 수는?" % (rank, order), 210, 324, 18, w=700), 420, 340)
        top = ", ".join(str(x) for x in (nums if big else sorted(nums))[:4])
        return dict(type="cards", title="수 카드로 만든 수", ic="🃏",
                    story="바닥에 수 카드가 흩어져 있다.",
                    prompt="%d번째로 %s 두 자리 수는?" % (rank, order),
                    kind="num", digits=2, ans=str(ans), fig=fig,
                    hints=["만들 수 있는 수를 <b>전부 적어</b> 보자. 몇 개나 될까?",
                           "모두 %d개야. 이제 %s 것부터 줄을 세워 봐." % (len(nums), order),
                           "%s … 이 순서니까 %d번째는 %d!" % (top, rank, ans)])
    return None


# ───────────────────────── 4. 저울 무게 비교

def g_balance(rng, objects):
    items = rng.sample(objects, 4)                 # [(이름, 사진id), ...]
    order = items[:]                               # 무거운 순
    rng.shuffle(order)
    pairs = [(order[i][0], order[i + 1][0]) for i in range(3)]   # 왼쪽이 더 무거움
    shown = pairs[:]
    rng.shuffle(shown)
    rank = rng.choice([2, 3])
    ans = order[rank - 1][0]
    return dict(type="balance", title="무게를 재 보자", ic="⚖️",
                story="저울 세 개가 매달려 있다.",
                prompt="%d번째로 무거운 물건은?" % rank,
                kind="choice", ans=ans,
                ch=[i[0] for i in items], chImg=[i[1] for i in items],
                balance=shown, fig=None,
                hints=["저울에서 <b>아래로 내려간 쪽</b>이 더 무거워. 하나씩 순서를 적어 보자.",
                       " , ".join("%s &gt; %s" % p for p in shown) + " 를 한 줄로 이어 봐.",
                       " &gt; ".join(i[0] for i in order) + " 순서야. %d번째는 %s!" % (rank, ans)])


# ───────────────────────── 5. 4×4 미니 스도쿠

def _sudoku_solutions(g):
    """빈칸(0)을 채우는 해의 개수"""
    def ok(g, r, c, v):
        for i in range(4):
            if g[r][i] == v or g[i][c] == v:
                return False
        br, bc = (r // 2) * 2, (c // 2) * 2
        for i in range(2):
            for j in range(2):
                if g[br + i][bc + j] == v:
                    return False
        return True
    for r in range(4):
        for c in range(4):
            if g[r][c] == 0:
                n = 0
                for v in range(1, 5):
                    if ok(g, r, c, v):
                        g[r][c] = v
                        n += _sudoku_solutions(g)
                        g[r][c] = 0
                        if n > 1:
                            return n
                return n
    return 1

def g_sudoku4(rng):
    base = [[1, 2, 3, 4], [3, 4, 1, 2], [2, 1, 4, 3], [4, 3, 2, 1]]
    perm = rng.sample(range(1, 5), 4)
    sol = [[perm[v - 1] for v in row] for row in base]
    if rng.random() < .5:
        sol = [list(r) for r in zip(*sol)]
    if rng.random() < .5:
        sol[0], sol[1] = sol[1], sol[0]
        sol[2], sol[3] = sol[3], sol[2]
    for _ in range(200):
        blanks = rng.sample([(r, c) for r in range(4) for c in range(4)], 3)
        g = [row[:] for row in sol]
        for r, c in blanks:
            g[r][c] = 0
        if _sudoku_solutions([row[:] for row in g]) != 1:
            continue
        qr, qc = blanks[0]
        ans = sol[qr][qc]
        cells = ""
        for r in range(4):
            for c in range(4):
                x, y = 52 + c * 74, 90 + r * 74
                v = g[r][c]
                isq = (r, c) == (qr, qc)
                cells += ('<rect x="%d" y="%d" width="74" height="74" fill="%s" stroke="#c7c2d6" '
                          'stroke-width="2"/>' % (x, y, "#fee2e2" if isq else "#fff8e6"))
                if isq:
                    cells += T("?", x + 37, y + 52, 38, "#c0392b", 800)
                elif v:
                    cells += T(str(v), x + 37, y + 52, 38, w=800)
        fig = S(PAPER(420, 400) + T("🔢 잠금판 (미니 스도쿠)", 210, 40, 19, w=800) +
                T("가로줄·세로줄·굵은 네모 안에 1~4가 한 번씩", 210, 64, 15, "#6b5430") + cells +
                '<g stroke="#8a6a30" stroke-width="5" fill="none"><rect x="52" y="90" width="296" height="296"/>'
                '<line x1="200" y1="90" x2="200" y2="386"/><line x1="52" y1="238" x2="348" y2="238"/></g>',
                420, 400)
        return dict(type="sudoku4", title="미니 스도쿠 잠금판", ic="🔢",
                    story="문에 이상한 숫자판이 달려 있다.",
                    prompt="빨간 ? 칸에 들어갈 수는?", kind="num", digits=1, ans=str(ans), fig=fig,
                    hints=["빈칸이 세 개야. 숫자가 세 개 들어 있는 <b>줄</b>부터 찾아보자.",
                           "그 줄에서 빠진 수를 먼저 채우면, 다른 줄도 하나씩 정해져.",
                           "차례대로 채우면 빨간 칸은 %d!" % ans])
    return None


# ───────────────────────── 6. 3×3 마방진

def g_magic3(rng):
    m = [[8, 1, 6], [3, 5, 7], [4, 9, 2]]
    for _ in range(rng.randint(0, 3)):
        m = [list(r) for r in zip(*m[::-1])]
    if rng.random() < .5:
        m = [r[::-1] for r in m]
    for _ in range(120):
        blanks = rng.sample([(r, c) for r in range(3) for c in range(3)], 2)
        used = {m[r][c] for r in range(3) for c in range(3)} - {m[r][c] for r, c in blanks}
        rest = [v for v in range(1, 10) if v not in used]
        sols = []
        for p in permutations(rest, 2):
            g = [row[:] for row in m]
            for (r, c), v in zip(blanks, p):
                g[r][c] = v
            lines = [sum(g[i]) for i in range(3)] + [sum(g[i][j] for i in range(3)) for j in range(3)]
            lines += [g[0][0] + g[1][1] + g[2][2], g[0][2] + g[1][1] + g[2][0]]
            if all(x == 15 for x in lines):
                sols.append(p)
        if len(sols) != 1:
            continue
        qr, qc = blanks[0]
        ans = m[qr][qc]
        cells = ""
        for r in range(3):
            for c in range(3):
                x, y = 76 + c * 84, 104 + r * 84
                isq = (r, c) == (qr, qc)
                blank = (r, c) in blanks
                cells += ('<rect x="%d" y="%d" width="84" height="84" fill="%s" stroke="#8a6a30" '
                          'stroke-width="3"/>' % (x, y, "#fee2e2" if isq else ("#efe2c4" if blank else "#fff8e6")))
                if isq:
                    cells += T("?", x + 42, y + 58, 40, "#c0392b", 800)
                elif not blank:
                    cells += T(str(m[r][c]), x + 42, y + 58, 40, w=800)
        fig = S(PAPER(420, 400) + T("🔯 바닥의 마방진", 210, 42, 20, w=800) +
                T("가로·세로·대각선 세 수의 합이 모두 같아요", 210, 72, 16, "#6b5430") + cells +
                T("빨간 ? 칸의 수는?", 210, 386, 18, w=700), 420, 400)
        return dict(type="magic3", title="바닥의 마방진", ic="🔯",
                    story="바닥에 숫자판이 새겨져 있다.",
                    prompt="빨간 ? 칸에 들어갈 수는?", kind="num", digits=1, ans=str(ans), fig=fig,
                    hints=["세 칸이 모두 채워진 줄을 먼저 찾아보자. 그 줄의 합이 모든 줄의 합이야.",
                           "합은 15야. 이제 빈칸이 하나뿐인 줄을 찾아 채워 봐.",
                           "차례로 채우면 빨간 칸은 %d!" % ans])
    return None


# ───────────────────────── 7. 격자 최대 경로

def g_maxpath(rng):
    for _ in range(200):
        n = 4
        g = [[rng.randint(1, 7) for _ in range(n)] for _ in range(n)]
        dp = [[0] * n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                best = 0
                if r:
                    best = max(best, dp[r - 1][c])
                if c:
                    best = max(best, dp[r][c - 1])
                dp[r][c] = best + g[r][c]
        ans = dp[n - 1][n - 1]
        if not (10 <= ans <= 99):
            continue
        cells = ""
        for r in range(n):
            for c in range(n):
                x, y = 58 + c * 76, 84 + r * 66
                st, en = (r == 0 and c == 0), (r == n - 1 and c == n - 1)
                fill = "#d9f2c9" if st else ("#fde2e2" if en else "#fff8e6")
                cells += ('<rect x="%d" y="%d" width="76" height="66" fill="%s" stroke="#8a6a30" '
                          'stroke-width="2.5"/>' % (x, y, fill)) + T(str(g[r][c]), x + 38, y + 46, 30, w=800)
        fig = S(PAPER(420, 420) + T("🗺️ 보석을 최대로 모으는 길", 210, 40, 19, w=800) +
                T("초록(출발) → 빨강(도착) · 오른쪽·아래로만 이동", 210, 68, 15, "#6b5430") + cells +
                '<g stroke="#8a6a30" stroke-width="5" fill="none"><rect x="58" y="84" width="304" height="264"/></g>' +
                T("🚩 출발", 82, 378, 15, "#3b7a2a", 700) + T("🏁 도착", 336, 378, 15, "#c0392b", 700) +
                T("지나온 칸의 수를 모두 더한 값 중 가장 큰 값은?", 210, 406, 16, w=700), 420, 420)
        return dict(type="maxpath", title="보석을 최대로 모으는 길", ic="🗺️",
                    story="칸마다 보석이 숨어 있다. 한 번만 지나갈 수 있다.",
                    prompt="모을 수 있는 가장 큰 합은?", kind="num", digits=2, ans=str(ans), fig=fig,
                    hints=["오른쪽과 아래로만 갈 수 있어. 먼저 아무 길이나 하나 골라 더해 보자.",
                           "길을 하나씩 시험하는 대신, <b>각 칸까지 올 수 있는 가장 큰 합</b>을 왼쪽 위부터 차례로 적어 봐.",
                           "그렇게 끝까지 적으면 도착 칸에 %d이 나와. 정답은 %d!" % (ans, ans)])
    return None


# ───────────────────────── 8. 새로운 연산 기호

_OPS = [
    ("mul_plus_diff", lambda a, b: a * b + (a - b), "(앞×뒤) + (앞−뒤)"),
    ("mul_plus_sum",  lambda a, b: a * b + a + b,   "(앞×뒤) + 앞 + 뒤"),
    ("mul_minus_diff", lambda a, b: a * b - (a - b), "(앞×뒤) − (앞−뒤)"),
    ("sum2_minus_b",  lambda a, b: (a + b) * 2 - b, "(앞+뒤)×2 − 뒤"),
    ("sq_plus_b",     lambda a, b: a * a + b,       "(앞×앞) + 뒤"),
]

def g_newop(rng):
    for _ in range(400):
        name, f, desc = rng.choice(_OPS)
        ex, seen = [], set()
        while len(ex) < 3:
            a, b = rng.randint(2, 9), rng.randint(1, 6)
            if (a, b) in seen or a <= b:
                continue
            seen.add((a, b))
            v = f(a, b)
            if 5 <= v <= 99:
                ex.append((a, b, v))
        qa, qb = rng.randint(2, 9), rng.randint(1, 6)
        if (qa, qb) in seen or qa <= qb:
            continue
        ans = f(qa, qb)
        if not (10 <= ans <= 99):
            continue
        # 다른 규칙도 예시를 만족하면서 답이 다르면 모호 → 버림
        amb = False
        for n2, f2, _ in _OPS:
            if n2 == name:
                continue
            if all(f2(a, b) == v for a, b, v in ex) and f2(qa, qb) != ans:
                amb = True
                break
        if amb:
            continue
        rows = "".join(T("%d ★ %d = %d" % (a, b, v), 210, 104 + i * 46, 30, w=800)
                       for i, (a, b, v) in enumerate(ex))
        fig = S(PAPER(420, 330) + T("⚙️ 낯선 기호  ★", 210, 46, 20, w=800) +
                '<rect x="30" y="64" width="360" height="150" rx="12" fill="#fff8e6" stroke="#b58a45" stroke-width="3"/>' +
                rows + T("그렇다면", 210, 248, 18, "#6b5430") +
                T("%d ★ %d = ?" % (qa, qb), 210, 292, 34, "#c0392b", 800), 420, 330)
        a0, b0, v0 = ex[0]
        return dict(type="newop", title="낯선 기호의 규칙", ic="⚙️",
                    story="벽에 ★ 라는 기호가 새겨져 있다.",
                    prompt="%d ★ %d 는 얼마일까요?" % (qa, qb),
                    kind="num", digits=2, ans=str(ans), fig=fig,
                    hints=["★ 는 우리가 아는 기호가 아니야. <b>규칙을 새로 찾아야</b> 해.",
                           "첫 줄을 보자. %d와 %d로 %d을 만들려면 어떻게 해야 할까? 곱해 보고, 더해 보고, 빼 봐." % (a0, b0, v0),
                           "규칙은 %s 야. %d ★ %d = %d!" % (desc, qa, qb, ans)])
    return None


# ───────────────────────── 9. 스무고개 두 자리 수

def g_twenty(rng):
    for _ in range(400):
        n = rng.randint(12, 98)
        t, u = n // 10, n % 10
        if t == u:
            continue
        lo = (n // 10) * 10 - 10
        hi = lo + 20
        s = t + u
        big = "십의 자리" if t > u else "일의 자리"
        cands = [x for x in range(10, 100)
                 if lo < x < hi and (x // 10) + (x % 10) == s
                 and ((x // 10 > x % 10) == (t > u))
                 and ((x % 2 == 1) == (n % 2 == 1))]
        if len(cands) != 1:
            continue
        lines = ["Q. %d보다 큽니까?              → 예" % lo,
                 "Q. %d보다 작습니까?            → 예" % hi,
                 "Q. 십의 자리와 일의 자리 중",
                 "     어느 쪽이 큽니까?   → %s" % big,
                 "Q. 두 숫자를 더하면?          → %d" % s,
                 "Q. 짝수입니까?                  → %s" % ("아니요" if n % 2 else "예")]
        fig = S(PAPER(420, 352) + T("🗿 다섯 가지 질문과 대답", 210, 44, 19, w=800) +
                CLUE(lines, 20, 60, 380, 33, 16) +
                T("감춰진 두 자리 수는?", 210, 336, 18, w=700), 420, 352)
        return dict(type="twenty", title="스무고개 수 맞히기", ic="🗿",
                    story="질문 다섯 개의 대답만 남아 있다.",
                    prompt="감춰진 두 자리 수는?", kind="num", digits=2, ans=str(n), fig=fig,
                    hints=["첫 두 답으로 범위를 좁히자. %d보다 크고 %d보다 작아." % (lo, hi),
                           "그 범위에서 두 숫자의 합이 %d인 수를 모두 적어 봐." % s,
                           "%s가 더 크고 %s니까 정답은 %d!" % (big, "홀수" if n % 2 else "짝수", n)])
    return None


# ───────────────────────── 10. A·B·C 관계 추리

_NAMES = ["가은", "나래", "다온", "라온", "미르", "하람", "새롬", "지호"]

def g_abc(rng):
    for _ in range(300):
        a, b, c = rng.sample(_NAMES, 3)
        x = rng.randint(4, 14)          # b가 가장 적음
        d1 = rng.randint(3, 9)          # a = b + d1
        d2 = rng.randint(1, d1 - 1)     # c = a - d2
        A, B, C = x + d1, x, x + d1 - d2
        tot = A + B + C
        if not (10 <= A <= 99):
            continue
        lines = ["① %s는 %s보다 %d개 많습니다." % (a, b, d1),
                 "② %s는 %s보다 %d개 적습니다." % (c, a, d2),
                 "③ 셋이 모은 것은 모두 %d개입니다." % tot]
        boxes = "".join(('<rect x="%d" y="196" width="100" height="62" rx="10" fill="#fff8e6" '
                         'stroke="#b58a45" stroke-width="3"/>' % (38 + i * 118)) +
                        T(nm, 88 + i * 118, 236, 24, w=800)
                        for i, nm in enumerate([a, b, c]))
        fig = S(PAPER(420, 320) + T("💎 셋이 모은 보석", 210, 46, 20, w=800) +
                CLUE(lines, 26, 64, 368, 34, 17) + boxes +
                T("%s는 몇 개를 모았을까요?" % a, 210, 300, 18, w=700), 420, 320)
        return dict(type="abc", title="세 사람의 보석", ic="💎",
                    story="셋이 나눠 가진 개수를 알아내야 한다.",
                    prompt="%s는 몇 개를 모았을까요?" % a,
                    kind="num", digits=2, ans=str(A), fig=fig,
                    hints=["가장 적게 가진 사람이 누구일지 생각해 보자. %s가 제일 적어." % b,
                           "%s를 □라고 하면 %s = □+%d, %s = □+%d 야. 셋을 더하면 □+□+□+%d."
                           % (b, a, d1, c, d1 - d2, d1 + d1 - d2),
                           "□×3 + %d = %d → □ = %d. %s = %d+%d = %d!"
                           % (d1 + d1 - d2, tot, x, a, x, d1, A)])
    return None


# ───────────────────────── 11. 수 배열 규칙

def g_seq(rng):
    for _ in range(300):
        kind = rng.choice(["add", "mul", "diff", "fib", "zig"])
        if kind == "add":
            a, d = rng.randint(2, 9), rng.randint(2, 7)
            seq = [a + d * i for i in range(6)]
            tip = "%d씩 커져" % d
        elif kind == "mul":
            a, r = rng.choice([1, 2, 3]), rng.choice([2, 3])
            seq = [a * r ** i for i in range(6)]
            tip = "앞의 수를 %d배 해" % r
        elif kind == "diff":
            a = rng.randint(1, 4)
            seq, cur, step = [a], a, rng.randint(1, 2)
            for i in range(5):
                cur += step
                step += 1
                seq.append(cur)
            tip = "커지는 양이 1씩 늘어나"
        elif kind == "fib":
            a, b = rng.randint(1, 3), rng.randint(2, 4)
            seq = [a, b]
            for _ in range(4):
                seq.append(seq[-1] + seq[-2])
            tip = "앞의 두 수를 더하면 다음 수야"
        else:
            a, b = rng.randint(1, 4), rng.randint(5, 8)
            d1, d2 = rng.randint(1, 3), rng.randint(1, 3)
            seq = []
            for i in range(3):
                seq += [a + d1 * i, b + d2 * i]
            tip = "한 칸씩 <b>건너뛰며</b> 봐"
        qi = rng.choice([3, 4, 5])
        ans = seq[qi]
        if not (10 <= ans <= 99) or any(v > 99 or v < 0 for v in seq):
            continue
        vals = [str(v) for v in seq]
        vals[qi] = "?"
        fig = S(PAPER(420, 340) + T("🪨 새겨진 수의 규칙", 210, 50, 20, w=800) +
                CELLS(vals, 24, 90, 124, 100, 3, {qi}) +
                T("규칙을 찾아 빨간 ? 를 채우세요", 210, 322, 18, w=700), 420, 340)
        return dict(type="seq", title="수의 규칙 찾기", ic="🪨",
                    story="돌마다 수가 새겨져 있다. 규칙이 있다.",
                    prompt="빨간 ? 자리의 수는?", kind="num", digits=2, ans=str(ans), fig=fig,
                    hints=["옆에 있는 수끼리 어떻게 변하는지 화살표 위에 적어 보자.",
                           "%s." % tip,
                           "규칙대로 채우면 %d!" % ans])
    return None


# ───────────────────────── 12. 고대의 수 (기호 해독)

_SYM = [("✋", 5), ("👁", 2), ("🦶", 10), ("🦷", 1), ("👂", 3), ("👃", 4)]

def g_ancient(rng):
    for _ in range(200):
        tab = rng.sample(_SYM, 4)
        pick = rng.sample(tab, 3)
        ans = sum(v for _, v in pick)
        if not (10 <= ans <= 99):
            continue
        cards = ""
        for i, (s, v) in enumerate(tab):
            x = 34 + i * 94
            cards += ('<rect x="%d" y="72" width="80" height="94" rx="10" fill="#fff8e6" '
                      'stroke="#b58a45" stroke-width="3"/>' % x)
            cards += '<text x="%d" y="112" font-size="34" text-anchor="middle">%s</text>' % (x + 40, s)
            cards += T("= %d" % v, x + 40, 152, 20, w=800)
        expr = " ".join(s for s, _ in pick)
        fig = S(PAPER(420, 340) + T("🏛️ 벽에 새겨진 고대의 수", 210, 46, 20, w=800) + cards +
                '<rect x="60" y="196" width="300" height="82" rx="12" fill="#efe0bd" stroke="#8a6a30" stroke-width="4"/>' +
                '<text x="210" y="252" font-size="42" text-anchor="middle">%s</text>' % expr +
                T("벽화가 나타내는 수는?", 210, 312, 18, w=700), 420, 340)
        return dict(type="ancient", title="벽에 새겨진 고대의 수", ic="🏛️",
                    story="옛사람들은 몸으로 수를 나타냈다고 한다.",
                    prompt="벽화가 나타내는 수는?", kind="num", digits=2, ans=str(ans), fig=fig,
                    hints=["위쪽 표에서 그림마다 얼마인지 먼저 찾아보자.",
                           " , ".join("%s는 %d" % (s, v) for s, v in pick) + " 야. 세 개를 <b>더하면</b> 돼.",
                           " + ".join(str(v) for _, v in pick) + " = %d!" % ans])
    return None


# ───────────────────────── 등록

# key: (함수, 난이도, 담당)
REGISTRY = {
    "seq":      (g_seq,      1, "👶 7살 담당"),
    "cards":    (g_cards,    1, "👶 7살 담당"),
    "ancient":  (g_ancient,  1, "👶 7살 담당"),
    "balance":  (g_balance,  1, "👶 7살 담당"),
    "sudoku4":  (g_sudoku4,  2, "🧒 초2 담당"),
    "magic3":   (g_magic3,   2, "🧒 초2 담당"),
    "cond2":    (g_cond2,    2, "🧒 초2 담당"),
    "abc":      (g_abc,      2, "🧒 초2 담당"),
    "cond3":    (g_cond3,    3, "🧒 초2 담당"),
    "newop":    (g_newop,    3, "👫 둘이 함께"),
    "twenty":   (g_twenty,   3, "👫 둘이 함께"),
    "maxpath":  (g_maxpath,  3, "👫 둘이 함께"),
}

ALL_TYPES = list(REGISTRY.keys())

# 문제집 사진에서 뽑아낸 키워드 → 문제 유형
KEYWORDS = {
    "저울": "balance", "무게": "balance", "무겁": "balance",
    "스도쿠": "sudoku4", "가로줄": "sudoku4",
    "마방진": "magic3", "대각선": "magic3",
    "카드": "cards", "몇 번째": "cards", "번째로 큰": "cards",
    "조건": "cond2", "각 자리": "cond2", "두 자리 수": "cond2", "세 자리 수": "cond3",
    "규칙": "seq", "배열": "seq", "수열": "seq",
    "약속": "newop", "기호": "newop", "연산": "newop",
    "질문": "twenty", "대답": "twenty", "스무고개": "twenty",
    "고대": "ancient", "몸": "ancient",
    "길": "maxpath", "경로": "maxpath", "바둑돌": "maxpath", "지나간": "maxpath",
    "권": "abc", "많습니다": "abc", "적습니다": "abc",
}


def make(rng, types, objects):
    """types 순서대로 문제를 만든다. 실패하면 다른 유형으로 대체."""
    out, used = [], set()
    pool = [t for t in ALL_TYPES]
    rng.shuffle(pool)
    queue = list(types) + pool
    for t in queue:
        if len(out) >= 10:
            break
        if t in used or t not in REGISTRY:
            continue
        fn, lvl, role = REGISTRY[t]
        q = fn(rng, objects) if t == "balance" else fn(rng)
        if not q:
            continue
        used.add(t)
        q["role"] = role
        q["level"] = lvl
        out.append(q)
    out.sort(key=lambda q: q["level"])
    for i, q in enumerate(out, 1):
        q["id"] = i
    return out
