# 2522 Inspector状態解析 全program閉鎖PT仕様

2026-10-29、PG-D826、event2903で開始見積2/5/8週次共有pp・cap10を凍結。主WBS-F03、既artifact主担当・費用参照WBS-P004-04、追加親予算0。原見積/受入/費用nullを保持する。

## 対象・独立oracle

NK-OPS-001/OPS009/UI251/SS341 §7.4・SS343/SSC060。Main `InspectorUnitSnapshot` と全nested Target（二physical）を一source unitとして測る。既whole `InspectorUnitSnapshotTest` 九、`InspectorHeldStateContractTest` 九、`ArtemisUnitSnapshotTest` 四を同一source・同一execで実行し、次の一Testを追加する。旧九run/旧sourceのcounterは合算しない。

|Test ID / method|事前条件・入力・操作|独立期待値・根拠|
|---|---|---|
|PT-SNAPSHOT-NORMAL-EXIT-001 / normalExitCodeIsLiteralOnlyAfterNormalMainCode|手書18field GOLDEN、ExecMainCode=1。statusを0/1/10/30/70/143/255のliteralへ変更しparse後normalExitCode呼出し|正常終了種別1のstatusは入力整数そのもの。0や10へ正規化しない。これはmanager状態データの型契約であり成功receipt/真正所有ではない。|
|同ID 異常終了種別|同goldenのExecMainCodeのみ0/2/3/4/5/6へ変更|StopGateException・reason=MALFORMED_STATE、causeなし/suppressed0。signal/core/未実行を正常終了へ読み替えない。expectedは手書定数でProduction関数から生成しない。|
|既Snapshot九|2520の全入力/fixture/境界/null/例外/並行を維持|373byte ASCII固定golden/SHA2170fc2e…、既assertを変更しない。自己pool8/Future10秒・自己CWD scalar三行だけ。|
|既HeldState九|612のheld/inactive/normalstop/receipt/clock/status/enum全literal・独立60state組合せ、全wholeを選択|保持dataの全field一致・不一致/worker code0/inspector code10/異世代を手書期待値と比較。実Root/owner/停止資格へ換算しない。|
|既Artemis四|手書LIVE/property単一差分/worker差・明示memory Reader、凍結snapshot内の公開artemis.serviceだけ読取|daemonはworker receiptでない。Unit Type=simple/Restart=on-failure。readProcesses callbackは呼ばれればfail。default NativeReader/実systemctlを使わない。|

新規method1・計23method/3suite。loop/vectorは別PT件数に数えない。null/欠落/空/未知・例外・並行は既wholeを維持し、再送・DB・native・実サービスは本data-only契約の適用外/未受入。実動作HOLDを解除しない。

## PT_DEFAULTとsource固定

全3Test/416行Main/明示Probe constructor/read bodyの到達性を読取確認済み。Map/String/UUID/BigInteger・明示memory Readerのみ。MorningBackupUnitCycle.Outcomeはnested enum定数だけで外側Root cycleを起動しない。Artemis004のnk.pt.repositoryは新normalの凍結公開snapshotへ小launcherで固定し、当公開artemis.serviceのhashを実行前後で照合する。変更許可/credential/実Unitへの代替経路は追加しない。

新Testsourceをcommit後に固定し、新しい六module compile/testCompile・format/null/Werrorと完全1843MainのSpotBugs Max/Low/MissingClass/Error/集合照合、Main/Test物理byte差の独立postを行う。compile-onlyはPT0/未実行であってPASS件数に算入しない。通常PTは23を一exec/一session/append=falseで取得し、元XML・found/started/success・FES/abort/container0・全source/Jar/fixture/hash・CRCを独立postで照合する。四counterのmissはそのまま保持し、除外/reflection/旧exec union/人工成功を使わない。

既公知3行traceはpost初hashの限界を維持。秘密/実credential/私有raw/VM/DB/鍵/保持原本/Graph9/二held工具はアクセス0。元jobは全owned真正終端・外部UNOBSERVED_HOLD、新操作/二重起動0。正式1964PT/53scope・個別17/190・工数null・QA051finalを不変更。障害を発見すれば修正前915/916へ起票する。

実command/環境/対象commit・coverage/実際値/終了/BUG/証跡path/hashは2523と新専用manifestへ記録する。event2903のappend自体は成功、直後の表示で戻り値strをdict扱いしたTypeError1は管理表示のみ・再append0、製品/試験は未起動。既成功確認の再演ではなく、変更後の全program単一exec閉鎖に必要な再検証として区別する。

### 事前静的実測と修正前起票（同群・予算不変更）

初候補23582/13812は六compile0/PT0、13814は選択三Test raw3（新AvoidDuplicateLiterals1/既有限pool DoNotUseThreads2）、六Main13816/18は全1843/Low/Max指摘・MissingClass/Error0。13820のunused importはlint1/body未開始で原fileを保持、別13821でMain全byte不変/1978Test中当outer一physicalだけ変更/旧九assertと全source完全復元を真正0確認（manifest56f647d8…）。旧PTは起動しない。BUG2080/YKT1828修正前起票後、ExecMainCodeの四回の同一literalをprivate定数へ整理した。独立逆変換で23582の全tokenを復元し、新Test ID/expected/元九は不変。修正後は別sourceをfreezeし、13832以降の新compile・静的を当新sourceへ結合してから、未開始の全23を初回実行する。旧成功を新sourceへ移さず、未実行全23を再実行件数に数えない。専有消費/残工数はnull、actual source修正1と管理lint1を分離する。
