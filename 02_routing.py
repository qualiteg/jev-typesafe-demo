# 02_routing.py
# 場面 1: 問い合わせの振り分け。日本語のチケット 30 件を 5 部署に分類し、正解率・confidence・所要時間を記録する。
# 正解ラベルは筆者が付けた。
import json
import statistics
from jev_common import call, Choice, RESULTS_DIR

CRITERIA = {
    "billing": "請求・支払い・領収書・二重課金・返金",
    "technical": "ログイン不可・エラー・動作不良・表示崩れなどの技術的な不具合",
    "account": "契約内容の変更・解約・プラン変更・利用者の追加や削除",
    "sales": "新規導入の相談・見積・デモの依頼・機能の問い合わせ",
    "other": "上のどれにも当てはまらない（挨拶・営業メール・無関係な内容）",
}

TICKETS = [
    ("先月分の請求書が二重に届いています。どちらが正しいのか教えてください。", "billing"),
    ("クレジットカードの有効期限が切れたので支払い方法を変更したいです。", "billing"),
    ("領収書の宛名を会社名に変えて再発行してもらえますか。", "billing"),
    ("年払いに切り替えた場合、月払いとの差額はどう精算されますか。", "billing"),
    ("今月の引き落とし額が先月より高いのですが、内訳を教えてください。", "billing"),
    ("解約したはずなのに今月も課金されています。返金をお願いします。", "billing"),
    ("ダッシュボードを開くと真っ白な画面のまま何も表示されません。Chrome です。", "technical"),
    ("API を呼ぶと 502 が返ってきます。昨日までは動いていました。", "technical"),
    ("CSV をアップロードすると『文字コードが不正です』と出て取り込めません。", "technical"),
    ("二段階認証のコードが届かないのでログインできません。", "technical"),
    ("レポートの合計値が明細の合計と一致していないようです。", "technical"),
    ("スマホのアプリが起動直後に落ちます。iOS 18 です。", "technical"),
    ("来月末で契約を終了したいのですが、手続きを教えてください。", "account"),
    ("スタンダードプランからエンタープライズプランに変更したいです。", "account"),
    ("退職した社員のアカウントを削除して、新しい担当者を追加してください。", "account"),
    ("契約者の会社名が変わったので登録情報を更新したいです。", "account"),
    ("利用人数を 10 名から 25 名に増やしたいのですが、契約はどう変わりますか。", "account"),
    ("トライアル期間が終わる前に本契約に移行するにはどうすればよいですか。", "account"),
    ("御社のサービスを部署で導入検討しています。デモをお願いできますか。", "sales"),
    ("100 名規模で使う場合の見積をいただけますか。", "sales"),
    ("オンプレミス環境でも動きますか。導入前に確認したいです。", "sales"),
    ("競合の製品と比べてどこが違うのか、資料があれば送ってください。", "sales"),
    ("SSO（SAML）に対応していますか。対応していれば導入したいです。", "sales"),
    ("来期の予算取りのために、機能一覧と価格表をください。", "sales"),
    ("いつもお世話になっております。本日は年末のご挨拶にて失礼いたします。", "other"),
    ("【広告】SEO 対策で御社サイトの順位を上げませんか。今なら初月無料です。", "other"),
    ("採用に応募したいのですが、募集要項はどこで見られますか。", "other"),
    ("先日のセミナー、とても勉強になりました。ありがとうございました。", "other"),
    ("間違えて送信しました。このメールは無視してください。", "other"),
    ("御社のオフィスの最寄り駅を教えてください。", "other"),
]


def main():
    hits, records = 0, []
    for i, (text, label) in enumerate(TICKETS):
        raw, elapsed = call(
            text,
            {"dept": Choice(instructions="この問い合わせを担当すべき部署はどれか", criteria=CRITERIA)},
            log_name="02_routing", tag={"i": i, "label": label, "text": text},
        )
        ans = raw["answers"]["dept"]
        ok = ans["choice"] == label
        hits += ok
        records.append({"i": i, "label": label, "pred": ans["choice"], "conf": ans["confidence"], "ok": ok,
                        "elapsed": elapsed, "tokens": raw["usage"]["input_tokens"]})
        mark = "o" if ok else "x"
        print(f"{mark} #{i:02d} {label:9s} -> {ans['choice']:9s} conf={ans['confidence']:.2f} {elapsed*1000:6.0f} ms | {text[:28]}")
    lat = [r["elapsed"] for r in records]
    print("-" * 60)
    print(f"accuracy: {hits}/{len(TICKETS)} = {hits/len(TICKETS):.1%}")
    print(f"latency  : median {statistics.median(lat)*1000:.0f} ms / min {min(lat)*1000:.0f} / max {max(lat)*1000:.0f}")
    print(f"tokens   : total input {sum(r['tokens'] for r in records)}")
    wrong = [r for r in records if not r["ok"]]
    print(f"wrong ({len(wrong)}):", [(r['i'], r['label'], r['pred'], r['conf']) for r in wrong])
    (RESULTS_DIR / "02_routing_summary.json").write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
