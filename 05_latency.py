# 05_latency.py
# 質問の数を 1 → 40 に増やしたとき応答時間がどう変わるかを測る（同じ state に対して 5 回ずつ）。
# つづけて 8 並列で 80 リクエストを投げ、スループットを測る。
import asyncio
import json
import statistics
import time
from jev_common import call, Noul, Choice, Score, RESULTS_DIR
from typesafe_sdk import AsyncTypeSafeClient

STATE = (
    "件名: 管理画面にログインできない\n"
    "本文: 先週の金曜日から管理画面にログインできません。パスワードを再設定しても『認証に失敗しました』と表示されます。"
    "二段階認証のコードは届いています。Chrome と Edge の両方で試しました。社内の他のメンバーは問題なくログインできています。"
    "明日の朝までに直らないと顧客への月次レポートの納品が止まります。契約はエンタープライズプランで、担当は甲野です。"
    "至急ご対応をお願いします。"
)

POOL = [
    "ログインに関する問い合わせか", "パスワードの再設定を試したと書かれているか", "二段階認証に触れているか", "複数のブラウザで試したか",
    "他のメンバーにも同じ症状が出ているか", "納期や期限に触れているか", "契約プランに触れているか", "担当者の名前が書かれているか",
    "至急の対応を求めているか", "顧客への影響が書かれているか", "エラーメッセージの原文が含まれているか", "発生日が書かれているか",
    "スマホアプリの話か", "請求に関する内容か", "解約の相談か", "新規導入の相談か", "感謝の言葉が含まれているか", "怒りの表現が含まれているか",
    "月次レポートに触れているか", "金曜日という曜日が出てくるか", "Chrome という単語が出てくるか", "Edge という単語が出てくるか",
    "件名と本文の両方があるか", "英語で書かれているか", "丁寧な文体か", "箇条書きが使われているか", "URL が含まれているか",
    "電話番号が含まれているか", "メールアドレスが含まれているか", "アカウントの削除を求めているか", "返金を求めているか",
    "セキュリティ侵害の疑いに触れているか", "特定の機能名（管理画面）が出てくるか", "再現手順が書かれているか", "スクリーンショットの添付に触れているか",
    "社内の誰かにすでに相談したと書かれているか", "問い合わせ番号が書かれているか", "曜日または日付が 2 つ以上あるか", "質問文で終わっているか", "1 段落だけか",
]


def latency_by_question_count():
    out = []
    for n in [1, 5, 10, 20, 40]:
        qs = {f"q{i}": Noul(instructions=POOL[i]) for i in range(n)}
        times, tokens = [], None
        for r in range(5):
            raw, el = call(STATE, qs, log_name="05_latency", tag={"n_questions": n, "run": r})
            times.append(el)
            tokens = raw["usage"]["input_tokens"]
        rec = {"n": n, "median_ms": statistics.median(times) * 1000, "min_ms": min(times) * 1000, "max_ms": max(times) * 1000, "input_tokens": tokens}
        out.append(rec)
        print(f"questions={n:2d}  median {rec['median_ms']:6.0f} ms  (min {rec['min_ms']:.0f} / max {rec['max_ms']:.0f})  input_tokens={tokens}")
    (RESULTS_DIR / "05_latency_by_questions.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


async def throughput(total=80, concurrency=8):
    qs = {
        "is_technical": Noul(instructions="技術的な不具合の報告か"),
        "dept": Choice(instructions="担当部署はどれか", criteria={"billing": None, "technical": None, "account": None, "sales": None, "other": None}),
        "urgency": Score(instructions="緊急度は", criteria=["低", "中", "高"]),
    }
    sem = asyncio.Semaphore(concurrency)
    lat, tokens = [], 0

    async with AsyncTypeSafeClient() as ac:
        async def one():
            nonlocal tokens
            async with sem:
                t0 = time.perf_counter()
                res = await ac.system_one(STATE, qs)
                lat.append(time.perf_counter() - t0)
                tokens += res.raw_http_response.json()["usage"]["input_tokens"]

        t0 = time.perf_counter()
        await asyncio.gather(*[one() for _ in range(total)])
        wall = time.perf_counter() - t0
    lat.sort()
    rec = {"total": total, "concurrency": concurrency, "wall_s": wall, "req_per_s": total / wall,
           "p50_ms": lat[len(lat) // 2] * 1000, "p95_ms": lat[int(len(lat) * 0.95) - 1] * 1000, "max_ms": lat[-1] * 1000, "input_tokens": tokens}
    print(f"throughput: {total} req / {wall:.2f} s = {rec['req_per_s']:.1f} req/s at concurrency {concurrency}; p50 {rec['p50_ms']:.0f} ms, p95 {rec['p95_ms']:.0f} ms, max {rec['max_ms']:.0f} ms, input_tokens {tokens}")
    (RESULTS_DIR / "05_throughput.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")


if __name__ == "__main__":
    latency_by_question_count()
    asyncio.run(throughput())
