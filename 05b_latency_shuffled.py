# 05b_latency_shuffled.py
# 05_latency.py の質問数の計測を、ウォームアップ 3 回のあとに質問数の順序をラウンドごとに入れ替えて 6 ラウンド測り直す。
# 接続の立ち上がりや時間帯の影響と、質問数の効果を切り分けるため。
import json
import random
import statistics
from jev_common import call, Noul, RESULTS_DIR

# 05_latency.py と同じ本文と質問プール
from importlib import import_module
m = import_module("05_latency")
STATE, POOL = m.STATE, m.POOL

NS = [1, 5, 10, 20, 40]
ROUNDS = 6
rng = random.Random(20260928)

# ウォームアップ（結果は記録しない）
for _ in range(3):
    call(STATE, {"q0": Noul(instructions=POOL[0])})

times = {n: [] for n in NS}
for r in range(ROUNDS):
    order = NS[:]
    rng.shuffle(order)
    for n in order:
        qs = {f"q{i}": Noul(instructions=POOL[i]) for i in range(n)}
        raw, el = call(STATE, qs, log_name="05b_latency_shuffled", tag={"n_questions": n, "round": r})
        times[n].append(el)
    print(f"round {r}: order {order}")

out = []
for n in NS:
    t = times[n]
    rec = {"n": n, "median_ms": statistics.median(t) * 1000, "min_ms": min(t) * 1000, "max_ms": max(t) * 1000, "runs": len(t)}
    out.append(rec)
    print(f"questions={n:2d}  median {rec['median_ms']:6.0f} ms  (min {rec['min_ms']:.0f} / max {rec['max_ms']:.0f})  n={len(t)}")
(RESULTS_DIR / "05b_latency_shuffled.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
