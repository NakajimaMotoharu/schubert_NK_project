# 2536 MorningCompletionBoundary全13 通常PT仕様

2026-10-29 / PG-D833予定 / event2919 / F03主、canonical P01712費用参照のみ追加0。開始1/3/6cap10、source0061/normal13832/静的13838、Main/Test変更なし。

対象は元whole MorningCompletionChecksTest全203行の5、MorningBackupObservedCompletionTest全220行の2、MorningCompletionRetirementTest全300行の6（正確なline count/全SHAはnormal/manifest、行数を成功件数へ換算しない）。全bodyと実calleeを確認した。Checks.verify/ownerGuardは注入peerとDB callbackを実行し、SQL内でのowner再確認にDBを混ぜない。ObservedはfixedClock/手書Access.failBackup/Archive callbackだけ。Retirementは元TestのretireCompleted/CompletionProgress・CompletionPhaseをmemory gates/time/sinkで呼び、実unlink/intent/permit/配備/Root起動/権限操作は行わない。Main outerにeager static/native初期化なし。診断の失敗を抑えるのは元所有UNKNOWNへの制御復帰契約、製品PTの失敗/skipをPASSに変えない。

fixtureは前群の未変更MorningCompletionEvidenceTest.fixture/database・PrestartEvidenceTest.inputの手書値/proxy。StoppedBackupFixtureの全port/AtomicLong budget/ReceiptGateと、literal BackupStepFixture.manifestを使う。実DB fixtureはcompile/signatureだけ、MorningCompletedMainTestはstatic ACTIVATIONのみ。extraのPrestart5/Completion11/Main4は非選択で実行件数0、goldenを読むTest自体は非選択なのでfixture map空。前群20成功を当13へ合算0。

MorningCurrentInvalidation全206は末尾RootStartupContext.createへ到達するためwhole HOLD・最初のpure5だけ切出し0。元通知は現存せず再要求0。実VM/DB/鍵/原本/Root/native/Unit/intent/permitは全HOLDを維持。

|既Test ID|入力・操作と独立expected|
|---|---|
|TXOWNER001～004/COMP203001（Checks5）|Atomic autoCommit false中はpeerだけ、trueでpeer→DB→peer。手書event列/四TX calls・22peer/52retained回、同一IOException identity/expired budget/null。DBを同TX内で二重entryしない。|
|MMAIN009/010（Observed2）|固定開始/終了microseconds、SUCCESSではarchive1・DB0、FAILEDはDB1と固定FAILED/target1/success0/failure1/bytes0/COMMAND_FAILURE。reverse clock/欠落/IO/runtime/nullは元identity/記録なし。Productionからexpected生成0。|
|COMPLETION790001～004/326001～002（Retirement6）|固定12event列・八phase順・注入time差1～8。八境界×六原因×IO/runtime/fatalで後続なし/DONEなし、diagnosticは固定分類・秘密文字列不出力。clock/sinkが故障してもfailure診断は元ownerへ戻り、正常phaseは同一例外を送出する。loopは別JUnit数へ加算0。|

関連NK-OPS001/OPS009/UI251/SS341/342/343、SSC115/185/203/237/326、BUG325/693と既修正証跡。source/Test/helper完全SHAは13912 PINS/EXTRAS・normal inputHashes、canonical rowは13846に結合する。

command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13912_morning_completion_boundaries_whole_thirteen_pt.py`。固定JDK25/JUnit1.13.4/JaCoCo0.8.15・cleanENV/全六Jar、全三suite13/単一session/appendfalse。13914は元XML/全source・dependency/空fixture/CRC/八反例と、完全Checks source一class＋StartupLaunchOwnerのProgress/Phase二nested classを測る。親Source全physical inventoryは別保持、他executableは未測定のまま。ChecksのBRANCH自然0-0を100の分岐実測と呼ばず、missと適用性を記録する。Main outer/実Root/停止/nativeの完了は認定しない。

2537へ原時刻/command/退出/実actual/counter/hash・失敗を保存し、障害は修正前起票。正式1964/53・17/190・工数null/QA051final・予算/全HOLD不変。通常区切りで止めず、残10又は枠不明で保全。
