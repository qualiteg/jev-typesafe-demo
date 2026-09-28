# 06_weak_spots.py
# 公式ドキュメント（Jev 1.13 jaggedness）が「苦手」と書いている数の大小比較と日付の前後を、
# 日本語の文でどれだけ当てられるか試す。乱数は固定シード。各 30 問。
import json
import random
from datetime import date, timedelta
from jev_common import call, Noul, RESULTS_DIR

rng = random.Random(20260928)


def number_cases(n=30):
    cases = []
    for _ in range(n):
        a = rng.randint(1, 99999)
        b = rng.randint(1, 99999)
        while b == a:
            b = rng.randint(1, 99999)
        cases.append((f"A は {a:,} 円、B は {b:,} 円です。", "A のほうが B より金額が大きいか", int(a > b)))
    return cases


def date_cases(n=30):
    cases = []
    base = date(2024, 1, 1)
    for _ in range(n):
        d1 = base + timedelta(days=rng.randint(0, 1000))
        d2 = base + timedelta(days=rng.randint(0, 1000))
        while d2 == d1:
            d2 = base + timedelta(days=rng.randint(0, 1000))
        s1 = f"{d1.year}年{d1.month}月{d1.day}日"
        s2 = f"{d2.year}年{d2.month}月{d2.day}日"
        cases.append((f"納品日は {s1}、支払期日は {s2} です。", "支払期日は納品日より後か", int(d2 > d1)))
    return cases


def run(name, cases):
    hits, recs = 0, []
    for i, (state, q, label) in enumerate(cases):
        raw, el = call(state, {"ans": Noul(instructions=q)}, log_name=f"06_{name}", tag={"i": i, "label": label, "state": state})
        p = raw["answers"]["ans"]["noul"]
        ok = (p >= 0.5) == bool(label)
        hits += ok
        recs.append({"i": i, "state": state, "label": label, "p": p, "ok": ok, "tokens": raw["usage"]["input_tokens"]})
        if not ok:
            print(f"  x #{i:02d} label={label} p={p:.2f} | {state}")
    print(f"{name}: {hits}/{len(cases)} correct")
    (RESULTS_DIR / f"06_{name}_summary.json").write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    run("numbers", number_cases())
    run("dates", date_cases())
