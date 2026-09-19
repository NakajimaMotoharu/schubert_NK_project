# NK-BAT-001 backup検証確定caller単体テスト仕様書

PG184/SSC067、RD BAK001～008/BKO001～008/OPS009、UI251、SS341§6.11/332/343。Program NK-BAT-001、予定class file.BackupBundleCompletion（constructor/complete/guard）。Production変更前。8 PT予定、未実装・未実行。

親がadmitted backup root、真正な完全DB/CONFIG handle、連続OS排他・停止/生成子終端、単独借用parent Connectionを保持する前提。public入力はConnection/directoryName/2handleのみで任意BackupManifestを受領しない。root Readerと全4file Verifierの成功・全owned close後にwall clockを取得しµsへ切下げ、既存BackupCommitServiceへ同一manifest/時刻を渡す。全phaseのmonotonic開始tickを共有し30分/割込を確認、後commitの期限・割込も非成功。callerは全失敗でConnection破棄、再試行は再度file検証と既存保存end読取を行う。

| Test ID | method | fixture/入力/操作・独立期待 |
|---|---|---|
| PT-BAT-274 | verifiedCommitAndReplay | 既存独立964byte golden・26/35/32byte公開file＋実PG18の90000/90001 RUNNING、固定endを渡すclock。両SUCCESS/common end/DB1file26byte・CONFIG2file67byte、再走の後時刻で保存end不変、file不変。SQL literal後条件で検証 |
| PT-BAT-275 | invalidFilesAndHandleBinding | name/part、別run・完全handle、root manifest改変/実3file hash不一致/余分file/owner/ACLを拒否しDB呼出0。真正fileでもDB側の別handle/片成功/不正countsは原子的拒否。旧Reader/Verifier/Repository oracleを弱めない |
| PT-BAT-276 | allReadAndDatabaseFailures | 既存Reader38＋Verifier123＝161 IO観測を独立inventoryと照合し各位置で失敗、DB呼出0・root/全file保全/資源解放。DB側は開始・最初/二番目更新・commit・rollback/restoreを公開JDBCで注入し既存serviceの全部rollback/不明commitを確認。投影expectedをProduction生成しない |
| PT-BAT-277 | sharedDeadlineAndInterrupt | 全clock位置と30分直前/同値/超過・負差/wrap、全境界割込を確認。Reader/Verifierのphaseで予算resetしない。後commit期限/割込では値を返さず、再走時のみ保存済結果へ到達可能。実blocking call即時停止の保証ではない |
| PT-BAT-278 | completionClockAndCommitUncertainty | wall clockは実file検証後だけ1回、ns→µs切下げliteral、contentFinished未満/範囲外/null/unknownを非正常化。commit実行後の応答故障は今回失敗、両SUCCESSを独立SQLで確認し再走は同一保存end、file再検証なしのshortcut禁止 |
| PT-BAT-279 | nullOwnershipAndFactory | public各null/owner範囲、package内clock/engine null、closed root、実public constructor入場を確認。borrowed root/Connectionをcloseしない。Production root実配布の成功をsynthetic UID PTへ代用しない |
| PT-BAT-280 | unknownFailuresAndResourceOwnership | 公開IO/clock/JDBCの未知Runtime/NPE/Errorを成功にしない、engineの同一unknown/固定secondary契約維持、全buffer消去・取得済close・未取得0・原本file不変。失敗後Connection破棄はcallerが実施 |
| PT-BAT-281 | concurrentAndIndependentTrace | 同一callerを異なるConnectionから競合、自己DB lock所有者だけ成功し非所有者は失敗、private同期でfile処理を交錯させない。固定manifest SHA/SQL成功値/借用所有/検証→wall→DBの順序を公開traceで残す |

Fixtureは既存BackupArtifactFixtureのread-only禁止mutationを維持し、実DB seedはfixture goldenに対応する独立SQL literalを新規用意する。実pg_dump/tar/age出力・運用secretは使わずGitへ保存しない。合成root UIDでreal Linux inode/FDを検証し、実root deployment/子終端/OS排他は別の前提である。

既定JDK25.0.4/Maven3.9.12/PG18.6、select ResourceScopeTest,BackupBundleCompletionTest（実装時に必要な既存回帰も併用）、test/JaCoCo report/SpotBugs。新class全line/method/class/branch100%、NullAway/Enforcer/Spotless/SpotBugs、正常/境界/異常/NULL/例外/並行/再送、failed/flaky/skipped/not-run0。実行command・OS/tool・source/branch・日時・exit・coverage・BUG/SSC・input/期待/実際・hashを071と正式evidence/manifestへ記録する。

全reactor/38scope/46負canary・source固定後のみ8PT/1部分成果を加算予定。期待Batch367/全1463（現在1455＋8）。これは実archive生成・directory公開・最新bundle選択/7世代・親全体・基盤/PGPT/IT/ST完了ではない。
