# PG3244 Backup完了再観測・handoff境界PT仕様

NK-OPS-001、MorningBackupUnitCycle.executeObserved/recheckCompletedBackup/retainUnresolvedOwner/executeHandoff、SS341§5-6/343§6.15/SSC134136/451。WBS-P017-06、event0823の着手前群見積.5/1.5/4週次共有pp。Main a9/3694資格f00d901/native28/現611L117M0C481Bを保持し、Testだけ追加予定。VM/DB原本/Backup/新Root/配備/署名は不変更。

## PT-OPS-BUCYCLE3244001 完了再観測とpublication不確実性

fixture=既同package試験port、typed receiptは手書きUnit属性literal由来の既ExpiryReceiptFixture.backupReceipt(0)で用意する。これは入力objectの製造であり、subjectの出力からexpectedを作らない。expected=SSの同一receipt/同一baseline/全Unit静止が揃った完了だけ再認証でき、再観測はstart/stop/retirementを再発行しない。

条件=完了前、正常完了、完了後の別INV receipt、全Unit非静止、typed有りだが非observed APIでbaseline欠落、observed APIのtyped欠落。正常はSUCCESS/同object identity・再観測0例外/start-stop-retire各1・completion1、異INV/非静止/基準欠落はIOExceptionとstart-stop-retire不増、typed欠落はretention sentinel・completion/retire0、正常完了後publication不確実性の公開retainUnresolvedOwnerも同retentionへ入る。単に例外だけをassertせず発行回数/順/回収有無を併記する。

## PT-OPS-BUCYCLE3244002 phaseとhandoff callbackの所有

fixture=BACKUP/CLEANUP/EXPIRY/INSPECTORの閉phase、各typed receipt/codeは独立literal、handoff借用中flagとcompletion後flagで親再取得順を別検査。expected=非Backupへexecute禁止、BACKUP/INSPECTORへgeneric Cleanup-Expiry handoff禁止、非InspectorへInspector handoff禁止、全てstart0。Cleanup/Expiryの承認済みexit30はtyped FAILEDとして受け入れ、親再取得後にcompletion→original proof→retire1、明示Backup/Inspector stopの発行0。callbackがnull/別receipt/未実行/二重の場合は保留・start最大1・completion/retire0、成功へ読み替えない。

未実装first-redは障害ではない。実装済みMainの期待値違反なら915/916へ先行起票。既executeBackupの不変target重複guardをcoverage目的だけで消去/人工到達せず、残枝として保留し別実装判断へ分離する。native indefinite-retainの実process検証とsynthetic sentinelは別で、今回port試験を実Unit成功と主張しない。

## PT-OPS-IUC3246001 Inspector内側の同handoff依存

既InspectorUnitCycleTestの手書きUnit十八属性/genuine typed gate fixtureを使用し、code0/10とstart-client UNKNOWN→reap0、stop-client UNKNOWN→reap0/非0の六tupleを追加する。expectedはSSのstart一回/stop一回、UNKNOWN中のwait一回、start-reap前stop0、stop-reap前親再取得0、親再取得後だけDB-END→env-owner→intent-retire。非0は保留・親再取得/DB-END/retire0・completedReceiptなし。Production結果をexpectedへ生成せず、独立event順/回数/固定codeを検査する。同じMorningBackupUnitCycleのprivate stopAndVerify境界へ到達する必要依存で、0823群の範囲・開始予算内に含める。Main/外部仕様/VM変更なし。

## 実行・受入

Test変更をformatter1.36.1で整形、現在3694の同Main jar/同依存へTestだけ別領域compile、SelectedClassContractLauncherで全MorningBackupUnitCycleTestと新二methodの存在/全成功/FES-aborted-notrun0を確認する。line/method/class/branchは独立XML実測し、未実行やscope外を合格へ加算しない。限定成功後、変更Test群の必要一wholeと同28stream再資格まで未統合として記録。command/source/run/UTC/終了code/XML/coverage/hash/BUGは実結果へ後記。正式1964/53/effortnull/QA051final不変。

3244限定実結果=59392680c/exec62647 actual0、全十二（新二含む）/FES-aborted-notrun0、manifestd2d7ea2c/XML399333b0、Main再compile/VM/native輸入0。限定hostのみのtarget残41L13M0C16Bはnative28合成前なので旧合成611L117M0C481Bから直接差分計上しない。次=3246全Inspector四（新一含む）→三新method/二Testfileを一whole3697へ統合→同28stream/全Main-byte資格。旧限定成功を別sourceの全scopeへ流用しない。
