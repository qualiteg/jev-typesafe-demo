# jev_common.py
# Jev（TypeSafe AI）を呼ぶときの共通処理。API キーは環境変数 TYPESAFE_API_KEY から読む。
# 記事のスクリプトはすべてこのファイルの call() を使い、応答と所要時間を results/ に残す。
import json
import os
import time
from pathlib import Path

from typesafe_sdk import TypeSafeClient, Noul, Choice, Score  # noqa: F401  (再エクスポート)

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

PRICE_PER_MTOK_INPUT = 0.042  # USD。docs.typesafe.ai/models の記載（出力は無料）

_client = None


def client() -> TypeSafeClient:
    global _client
    if _client is None:
        if not os.environ.get("TYPESAFE_API_KEY"):
            raise SystemExit("環境変数 TYPESAFE_API_KEY を設定してください")
        _client = TypeSafeClient()
    return _client


def call(state, questions: dict, log_name: str | None = None, tag: dict | None = None):
    """Jev を 1 回呼ぶ。戻り値は (生の応答 dict, 所要秒)。log_name を渡すと results/<log_name>.jsonl に追記する。"""
    t0 = time.perf_counter()
    res = client().system_one(state, questions)
    elapsed = time.perf_counter() - t0
    raw = res.raw_http_response.json()
    if log_name:
        rec = {"elapsed_s": round(elapsed, 4), "usage": raw.get("usage"), "model": raw.get("model"),
               "answers": raw.get("answers"), "request_id": res.request_id}
        if tag:
            rec.update(tag)
        with open(RESULTS_DIR / f"{log_name}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return raw, elapsed


def cost_usd(input_tokens: int) -> float:
    return input_tokens / 1_000_000 * PRICE_PER_MTOK_INPUT
