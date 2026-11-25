# 公開証跡のstage参照照合 単体テスト仕様

Program NK-OPS-001、WBS-G08、SS354・355、451、BUG-3768／YKT-2944の再発防止。対象は `tools/quality/verify_published_manifest_pins.py` の `audit` と引数選択。既公開のcommit区間と、同一の検証規則でcommit前のGit indexを確認する。

| Test ID | 入力と独立期待値 |
| --- | --- |
| PT-OPS-PIN-STAGED001 | stageした資産とmanifestを残し、作業ファイルだけ両方変更。現参照1、未解決0。stage全体が一tree、元のcommit比較はmanifest0。 |
| PT-OPS-PIN-STAGED002 | manifestが、同じhashのローカルだけに存在する資産を明示。未解決1で、公開に加算しない。 |
| PT-OPS-PIN-STAGED003 | stageに一致する資産はあるが、参照が指定したcommitには異なる内容だけがある。commit-sourceの参照は未解決1。 |

合成Gitで9既存＋3新規を同一選択し、正常、欠落、異常JSON、stageと未stage差を確認する。公開前の実差分は `python3 -B tools/quality/verify_published_manifest_pins.py --start "$base" --staged`、公開対象の確定commitは従来どおり `--start "$base" --end "$tip"`。公開外の入力は現pinsへ移さない。手順追加に伴う製品coverage・正式受入の加算は0。

## 明示pathの負例

PT-OPS-PINPATH001、BUG-3814／YKT-2972。合成Gitに置く固定1ファイルのSHA-256を独立算出する。pathを空・空白・null・整数・配列にした証拠主張は公開proofの不正pathと診断し、秘密入力・候補path値を診断に含めない。同じ不正参照の診断は重複排除する。pathとSHAがともにnullの場合は未観測。正規ローカルと明示外部をそれぞれ1件として保持する。stagedと確定commitを別入口で照合する。実公開・業務処理は行わない。
