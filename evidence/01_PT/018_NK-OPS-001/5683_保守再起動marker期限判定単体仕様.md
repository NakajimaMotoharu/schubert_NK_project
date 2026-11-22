# NK-OPS-001 外部監視の再起動marker期限判定

WBS-G13.06、C02、BUG-3577／YKT-2812、SS341 §4.2、UI251 §2、AVL-001／OPS-003。対象はBatchの `MaintenanceRebootWatch`。外部監視から受け取る観測値だけを扱う。

| Test ID | 合成入力 | 独立期待値 |
|---|---|---|
| PT-OPS-MAINT-PREBOOT004-W01 | 開始時点と59分59.999999999秒、更新なし | `WAITING` |
| PT-OPS-MAINT-PREBOOT004-W02 | 開始から60分ちょうどとその1ns後、更新なし | どちらも `CRITICAL` |
| PT-OPS-MAINT-PREBOOT004-W03 | 同run、異boot、期限ちょうどに更新。ちょうどと後日の観測 | どちらも `COMPLETE` |
| PT-OPS-MAINT-PREBOOT004-W04 | 別runまたは旧bootの更新 | 期限前は待機、期限に達した観測はcritical。 |
| PT-OPS-MAINT-PREBOOT004-W05 | 開始と同時、観測時点より後、期限より後のmarker | 期限時の成立証拠にならずcritical。 |
| PT-OPS-MAINT-PREBOOT004-W06 | 観測時刻が保守開始より前 | `INVALID_OBSERVATION` |
| PT-OPS-MAINT-PREBOOT004-W07 | 欠落、数違い、null要素、短縮UUID、解析不能時刻。markerのnull | CLI引数は `INVALID_OBSERVATION`、内部marker構築の契約違反は即座に拒否。 |
| PT-OPS-MAINT-PREBOOT004-W08 | 4引数と7引数で実main入口を呼ぶ | `CRITICAL`／`COMPLETE` の固定行、全引数の再出力なし。 |

実入口は `dev.codex.schubert.nk.batch.monitoring.MaintenanceRebootWatch`。引数はrun ID、開始前boot ID、開始時刻、観測時刻と、任意でmarkerのrun ID／boot ID／時刻の三項目。時刻はJavaのUTC Instant、識別子は正規UUID。監視側は出力の閉集合を判定に使用し、プロセス終了だけを正常の根拠としない。遅延更新は60分以内の完了を証明できない。実markerの作成・信頼性、外部監視への接続、実アラートと後続Linux試験は親仕様5677に残る。
