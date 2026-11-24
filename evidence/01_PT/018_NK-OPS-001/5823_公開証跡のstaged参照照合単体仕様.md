# 公開証跡のstage参照照合 単体テスト仕様

Program NK-OPS-001、WBS-G08、SS354・355、451、BUG-3768／YKT-2944の再発防止。対象は `tools/quality/verify_published_manifest_pins.py` の `audit` と引数選択。既公開のcommit区間と、同一の検証規則でcommit前のGit indexを確認する。

| Test ID | 入力と独立期待値 |
| --- | --- |
| PT-OPS-PIN-STAGED001 | stageした資産とmanifestを残し、作業ファイルだけ両方変更。現参照1、未解決0。stage全体が一tree、元のcommit比較はmanifest0。 |
| PT-OPS-PIN-STAGED002 | manifestが、同じhashのローカルだけに存在する資産を明示。未解決1で、公開に加算しない。 |
| PT-OPS-PIN-STAGED003 | stageに一致する資産はあるが、参照が指定したcommitには異なる内容だけがある。commit-sourceの参照は未解決1。 |

合成Gitで9既存＋3新規を同一選択し、正常、欠落、異常JSON、stageと未stage差を確認する。公開前の実差分は `python3 -B tools/quality/verify_published_manifest_pins.py --start "$base" --staged`、公開対象の確定commitは従来どおり `--start "$base" --end "$tip"`。公開外の入力は現pinsへ移さない。手順追加に伴う製品coverage・正式受入の加算は0。
