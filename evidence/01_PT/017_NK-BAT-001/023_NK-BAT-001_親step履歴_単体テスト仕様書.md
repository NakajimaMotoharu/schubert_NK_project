# NK-BAT-001 親step履歴単体テスト仕様書

PT-BAT-150の独立JDBC計数（source未適用時にSS331 §8.3とSQL/資源順序から確定）: RunReferenceの前後各16call＝32。history0行はprepare/timeout/bind2/executeQuery/next/close2＝8、INSERT RETURNINGはprepare/timeout/bind9/executeQuery/next2/getObject/close2＝17。したがってbegin0行57、history1行は12列＋next1で13増えて通常/skip70、明示abandonはprepare/timeout/bind6/executeUpdate/close＝10増えて80。finish UPDATEはprepare/timeout/bind14/executeUpdate/close＝18で合計50。0件後の同値replay SELECTはprepare/timeout/bind14/executeQuery/next2/getObject/close2＝22追加で72。各loopは既登録関数内/自前SQLを含むmethod別固定mapと全発火数を照合し、実観測mapをexpectedへ流用しない。新規設計に沿ってsourceが変わる場合は再計数理由を記録する。

begin0行57の固定map: connection.getAutoCommit/isReadOnly/getTransactionIsolation各2、prepareStatement4、statement.setQueryTimeout4/setObject9/setString5/setInt1/executeQuery4/close4、row.next7/getObject9/close4。history1行はrow.next+1/getObject+10/getString+2。abandon1行はprepareStatement+1/setQueryTimeout+1/setObject+3/setString+2/setLong+1/executeUpdate+1/statement.close+1。finish新規50は前後参照32にprepareStatement1/setQueryTimeout1/setObject4/setString4/setLong5/setInt1/executeUpdate1/statement.close1を加える。replay追加22はprepareStatement1/setQueryTimeout1/setObject4/setString4/setLong5/setInt1/executeQuery1/row.next2/row.getObject1/row.close1/statement.close1。故障経路は失敗した時点から本来の後続callが実行されないため、同じ成功mapとの完全一致を要求するのでなく指定位置発火・資源0・rollback後条件を照合する。

PG163/SSC055、先行898cc267、OPS009/DAT009/UI251 §11・12/SS311・331 §8.3・332・341 §3/11。実装前仕様。原本/fresh子全終端/OS排他/実backup/親全工程は未完了。PG162正式06中はsource/collectorを変更しない。

| Test ID | class/method | 目的・fixture/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-138 | BatchRunRepositoryTest.firstAttemptAndTerminalStates | 実PG/全10stepの初回RUNNING・各許可terminal finish、12列SQL後条件、診断は固定literalのみ |
| PT-BAT-139 | BatchRunRepositoryTest.ordinarySuccessSkipsByBusinessDate | 通常step同日SUCCESS→別attempt SKIPPED/0件、同日別runも日単位、前日成功は当日skipにしない |
| PT-BAT-140 | BatchRunRepositoryTest.backupAlwaysRunsAndAttemptLimit | backup2stepは複数SUCCESS保存、attempt99と次100拒否・旧行全保全、holesでもmax+1 |
| PT-BAT-141 | BatchRunRepositoryTest.explicitAbandonedRecovery | 同run RUNNINGはfalse拒否/trueだけFAILED ABANDONED、旧counts保全、他terminal不変、再beginの新attempt |
| PT-BAT-142 | BatchRunRepositoryTest.foreignRunningAndRootIdentity | 別run RUNNING拒否、同runprogress/cutoff/JST日付矛盾拒否、root不明を補完しない |
| PT-BAT-143 | BatchRunRepositoryTest.exactFinishReplay | 未commit/commit後同じterminal値のfinishは同値だけ冪等、異なるtime/status/count/reasonは既値保全拒否 |
| PT-BAT-144 | BatchRunRepositoryTest.handleIdentityAndMissingRows | id/run/date/step/attempt/started各不一致・不存在・skiphandle・0/複数update結果、他行を変更しない |
| PT-BAT-145 | BatchRunRepositoryTest.rollbackAndUnknownCommit | begin/abandon/finish rollback後条件、commit後応答不明の同値retry、新begin成功skip、途中更新を確定扱いしない |
| PT-BAT-146 | BatchRunRepositoryTest.historicalUtcAndFixedRunDay | 手書SQL0001/1582/1900/1970/UTC-JST境界/9999、JDBC4.2両方向、翌日nowでも原本business_date保持 |
| PT-BAT-147 | BatchRunRepositoryTest.clockRegressionPreservesRows | now<run.cutoff/既started/既ended、finish<started、NULL/nonµs/範囲外を拒否しDB無変更 |
| PT-BAT-148 | BatchRunRepositoryTest.parentTransactionAndLock | autoCommit/readOnly/isolation/no/shared/two-int/別backend拒否、自己exclusiveだけ、borrowed設定・所有不変 |
| PT-BAT-149 | BatchRunRepositoryTest.historyProjectionAndNulls | 12列各null（endedのRUNNINGだけ可）、unknownstatus/異date・step/件数負/重複id・attempt/順序/100行、row/statement null、有限境界 |
| PT-BAT-150 | BatchRunRepositoryTest.jdbcFailurePositions | begin0/既履歴/回復/skip・finish新規/replayの独立call表をSS順序から計数し全SQL故障位置/複合close・owned0・rollback後条件 |
| PT-BAT-151 | BatchRunRepositoryTest.interruptionAndRuntime | 開始/最終割込flag保持、unknownRuntime/NPE/Error非成功、各取得済資源解放、raw provider診断を持出さない |
| PT-BAT-152 | BatchRunRepositoryTest.concurrentOwnersAndRowLocks | 実別connection/transaction/threadのadvisory競合・rowlock、割当の一意性、partial観測禁止・再開、wait上限とrollback |
| PT-BAT-153 | BatchRunRepositoryTest.independentSqlInventoryAndGrants | V001～019不変/既grantのみ、SQLはclosed allowlist/timeout5/型bind、legacy診断をprojectionしない、全変更・非変更の固定DB後条件 |

Fixtureは隔離PostgreSQL18.6/Flyway V001～019/JDBC42.7.13、時刻/UUID/step/countは明示public literal。期待値はSS順序・固定SQL後条件・手計算のattempt/件数/固定文から算出し、Production methodの出力や観測件数から生成しない。null/未知/空/境界/異常/例外/並行/再試行を網羅。JDBC fault位置の表は実装後・fault期待値設定前に別途SQL/資源順序から独立計数し、全発火・close・rollbackを検証する。

実行commandは421 JDK/M2指定offline Maven -pl src/schubert-nk-batch -am test/verify、4coverage100/NullAway/SpotBugs/Spotlessを要求。failed/flaky/skipped/not-runは合格にしない。障害は修正前915、共通原因は916、上位修正は所定台帳へ先行する。branch/source commit/環境・日時・command/exit/input/期待/実際/coverage/BUG・SSC/evidence path・hashは024とmanifestへ実行後に記録する。現時点未実装/未実行、認定0。
