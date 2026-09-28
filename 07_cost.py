# 07_cost.py
# results/*.jsonl に残った usage を集計し、この記事の実験でいくら使ったかを出す。
import glob
import json
from collections import OrderedDict
from jev_common import RESULTS_DIR, cost_usd

total_req, total_in, total_out = 0, 0, 0
by_file = OrderedDict()
for path in sorted(glob.glob(str(RESULTS_DIR / "*.jsonl"))):
    n, tin, tout = 0, 0, 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            n += 1
            tin += rec["usage"]["input_tokens"]
            tout += rec["usage"]["output_tokens"]
    by_file[path.split("\\")[-1].split("/")[-1]] = (n, tin, tout)
    total_req += n
    total_in += tin
    total_out += tout

print(f"{'file':28s} {'requests':>8s} {'input_tok':>10s} {'output_tok':>10s} {'USD':>10s}")
for name, (n, tin, tout) in by_file.items():
    print(f"{name:28s} {n:8d} {tin:10,d} {tout:10,d} {cost_usd(tin):10.5f}")
print("-" * 70)
print(f"{'total':28s} {total_req:8d} {total_in:10,d} {total_out:10,d} {cost_usd(total_in):10.5f}")
print(f"(input $0.042 / 1M tokens, output free. 05_latency のスループット計測分は別集計)")
