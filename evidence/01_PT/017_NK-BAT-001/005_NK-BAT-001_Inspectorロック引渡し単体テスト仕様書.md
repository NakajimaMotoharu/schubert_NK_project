# NK-BAT-001 Inspectorロック引渡し単体テスト仕様書

PG-D-150/SSC-049、RD OPS-009、UI251、SS311/341 §7.3。InspectorLockHandoff.execute/scalar/ready/held、同期Operation、固定Failure。実PG18/Flyway/V001～017の隔離DB、schubert_batch/専用Inspector roleと公開JDBC faultを使用。PG/PT同時実施。OS lock/子process起動/credential/backup/同run progressは別未完了gate。

| Test ID | method | 事前条件・入力・操作・独立期待値 |
|---|---|---|
| PT-BAT-030 | actualTransactionHandoff | 親session lock保持→子専用roleの別transactionが同key取得・独立observerは競合→child commit/close→親再取得。2回実行後も親の1回unlockで完全解放。借用connection生存・自動commit状態不変 |
| PT-BAT-031 | preconditionsAndReentrantLock | lockなし/autocommit false/readOnly true/shared別mode/two-int別namespace/同key2回取得を拒否し子0回。再入残留を勝手に全unlockしない |
| PT-BAT-032 | callbackFailuresAndNull | callback IOException固定化、未知Runtime/Error同一例外・null結果NPE、すべて親再取得確認後の非成功。null引数はSQL前拒否 |
| PT-BAT-033 | reacquisitionConflict | callback中に別connectionがsession lock保持したまま復帰すると再取得拒否、値を返さず相手lockを解除/待機しない |
| PT-BAT-034 | jdbcFailureMatrix | 正常経路で観測した全JDBC method/回数の各位置へ故障。prepare/timeout/query/next/getObject/resultClose/statementClose/状態照会を網羅。cause/suppressed0、取得済資源close試行、借用commit/rollback/closeなし、失敗後caller破棄 |
| PT-BAT-035 | invalidResultMatrix | 5固定SELECTごとに欠落/多重/NULL/真偽逆転を注入。結果Booleanだけ/row1必須。初期/解放確認不成立は子0回。cleanup SQLなし |
| PT-BAT-036 | stateChangesAndInterrupts | 開始割込でSQL0/flag維持。callback後autoCommit/readOnly破壊・途中割込は値なし・接続破棄、未知Runtimeを正常にしない |
| PT-BAT-037 | concurrentGapCompetition | 同期callbackをlatchで保持し別thread/connectionが引渡しgapで取得。親再取得は失敗、他者lockは維持。有限waitで終了し偽成功なし |

Expectedは固定SQLの後条件（外部connectionのtrue/false、1回unlock、transaction commitで子lock解放）とliteral call inventoryから作る。Production query/methodからexpectedを生成しない。queryTimeoutは5秒設定を実adapter境界でassertし、ネットワーク断の厳密最大時間は後続Linuxの接続/socket timeoutと併せて確認する。単独所有connection契約、全null境界/negative、4coverage100%/静的解析、実行command/OS/tool/branch/source/日時/exit/Test ID/hashを006・evidenceへ保存する。Failed/flaky/skipped/not-runは合格にしない。

BUG146/YKT114（先行702b64ac）: Statement/ResultSetを直接TWRで所有してからnonnull aliasを確立する。034/035のnull resourceは既存のAPI境界契約試験であり、coverage用の無意味な生成分岐試験ではない。全close/SQL/null行・二重close故障と型付き固定診断を維持し、静的抑止/除外なしで再試験する。探索1失敗と探索2成功、他13境界の根拠はlogs/BUG-146-YKT-114.mdを参照。
