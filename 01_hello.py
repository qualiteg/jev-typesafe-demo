# 01_hello.py
# Jev の 3 つの質問型（Noul / Choice / Score）を日本語の問い合わせ 1 件に投げてみる。
import json
from jev_common import call, Noul, Choice, Score

state = "先週から管理画面にログインできません。パスワードを再設定しても『認証に失敗しました』と出ます。明日の朝までに直らないと顧客への納品が止まります。"

questions = {
    "is_technical": Noul(instructions="これは技術的な不具合の報告か"),
    "department": Choice(
        instructions="この問い合わせを担当すべき部署はどれか",
        criteria={
            "billing": "請求・支払い・領収書",
            "technical": "ログイン不可・エラー・動作不良などの技術的な不具合",
            "account": "契約内容の変更・解約・プラン変更",
            "sales": "新規導入の相談・見積・デモの依頼",
            "other": "上のどれにも当てはまらない",
        },
    ),
    "urgency": Score(
        instructions="緊急度はどのくらいか",
        criteria=["急がない", "数日以内に対応したい", "今日中に対応が必要", "業務が止まっており即時対応が必要"],
    ),
}

raw, elapsed = call(state, questions, log_name="01_hello")
print(json.dumps(raw, ensure_ascii=False, indent=2))
print(f"elapsed: {elapsed:.3f} s")
