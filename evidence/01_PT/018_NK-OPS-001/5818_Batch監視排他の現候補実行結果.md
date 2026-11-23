# Batch監視排他の現候補実行結果

PG43690。NK-OPS-001、WBS-F03/2-2-b／P018-09、RD171／UI252／SS351。JDK 25.0.4、Maven 3.9.12、固定source `98a8f53578cab17d9b67b1a16218179d39d4bc8f`。許可済み同期規則の6 Mainを変更。新規Test IDはPT-OPS-MON-SNAP005。経過1秒→逆行0秒拒否→別workerの経過2秒で、独立固定結果と再進行を検証した。

| 対象 | 結果 |
|---|---|
| 通常選択PT | 72成功、失敗・error・skip・対象内未実行0 |
| 生四指標 | 行300、メソッド89、クラス17、分岐132。すべて同一execで未到達0 |
| 静的 | NullAwayを含む当compiler終了0。SpotBugs Max/Low 17物理指摘・エラー・不足型0。PMD 6 Main適用指摘0、抑制0。7 sourceのCheckstyle／GJF差0 |
| 通常Batch JAR | 660型。対象コードと関連38物理のbyte同一、17物理の公開descriptor同一 |

BUG-3727の初回書式失敗は試験未起動。別sourceの原67成功は生coverage不足があり、72へ合算しない。BUG-3726／3727／3728、YKT-2925の当変更範囲を確認。実監視・実DB、保留32／Root11と全451・正式判定は未成立。

[実行manifest](evidence/PG43690-batch-monitor-lock-final-72/manifest.json)に入力、command、原終端、実行名簿とSHA-256を記録。 [仕様](5817_Batch監視排他の単体テスト仕様追補.md)
