# NK-BAT-001 run参照単体テスト仕様書

独立JDBC inventory確定: connection.getAutoCommit/isReadOnly/getTransactionIsolation/prepareStatement各1、statement.setQueryTimeout/executeQuery/close各1・setObject2（UUID/UTC OffsetDateTime）、row.next2/getObject4/close1＝全16呼出し。query5秒、固定SQL・UUID/cutoffのbindをassertし、各全位置SQLException・両close複合故障を注入してfixed診断/cause suppressed0・owned statement/row0・親未close/config不変を要求する。新2class/7method/37line/30branchは関連探索でmissed0、正式は別途。

PG159/SSC055、先行4c5dcb85、RunReferenceRepository.read/RunReferences、OPS-009/DAT-009/UI251/SS311/331 §3.12/332/343。実装前仕様、独立DB literal4boolean/手で数えたJDBC call、値からexpectedを生成する際Production readを使わない。

| Test ID | method | 入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-082 | referenceValueInvariants | 3flag全8組合せ・consistent true/false、不存在かつfalseだけ拒否、anyReference3OR、redacted、immutable equality |
| PT-BAT-083 | realReferenceRead | 実Flyway/専用batch、空/各table/全table/別runと不一致進捗、4値完全一致、cutoff不変 |
| PT-BAT-084 | transactionAndLockContracts | autoCommit/readOnly/隔離levelの各誤設定・lockなし/shared/別backend拒否、親接続設定/commit/rollback/close変更0 |
| PT-BAT-085 | projectionAndNullContracts | constructor/run null、statement/row/4column null、行欠落/複数/不整合、query5秒・bind固定UUID/time確認 |
| PT-BAT-086 | jdbcFailureMatrix | 独立call inventory全位置SQL失敗、result/statement両close複合もfixed error/cause suppressed0、owned0 |
| PT-BAT-087 | interruptionAndRuntime | 初期/最終割込flag保持・副作用非正常、未知runtime/NPEは成功化しない、借用connection保全 |
| PT-BAT-088 | rollbackAndFreshVisibility | 同runの変更/rollback/次TXでfresh観測、結果をcacheしない、step時刻から補完しない |
| PT-BAT-089 | independentConcurrentConnections | 共有しない別connectionの排他競合/引渡し/違うrun、同scopeとの所有境界、readonly観測後の履歴不変 |

全4coverage100%、NullAway/SpotBugs/formatと全reactor必須、失敗/skip等不算入。014・manifestへ正式source/日時/tool/command/exit/Test ID/expected/actual/coverage/BUG/hashを格納。SQL詳細8件は004/055と重複計上しない。GC marker/400日/親全区間OS・DBlock実結線は未完了のまま。
