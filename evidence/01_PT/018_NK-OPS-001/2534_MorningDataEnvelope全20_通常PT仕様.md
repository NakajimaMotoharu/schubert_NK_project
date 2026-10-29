# 2534 MorningDataEnvelope全20 通常PT仕様

2026-10-29 / PG-D832予定 / event2917 / 主WBS-F03、canonical P01712は費用参照のみ追加0。開始低1/標準4/高8pp、cap10を固定。source0061d178cda80c2ce3926290619c64db125dbcfc、normal13832/静的13838。Main/Test変更なし。正式1964PT/53scope、17/190、工数null、QA051 finalは不変。

## PT_DEFAULT・全既存クラスと独立性

MorningPrestartEvidenceTest全697行/5、MorningCompletionEvidenceTest全671/11、StoppedBackupCompletionTest全158/4を変更せずクラス単位で選択する。Main MorningPrestartEvidence全297/MorningCompletionEvidence全201と、呼ばれるGate.header、MorningProcessMain.archive/completeObservedBackup、BackupCompletion.complete、BackupCycleの注入constructor/executeObserved/recheck/capture/stop後condition、ReceiptGate、Cleanup.Completion値constructor、Guard、StartupPermitRecords.Epochを確認した。Guard/DB Access/clock/start/stop/kernel/ownerは既存手書memory port。親budgetはpackage constructorへAtomicLong supplierを注入し、create/borrow/LinuxMonotonicClockには到達しない。retain/waitはfixtureがAssertionErrorとし正常復帰へ置換しない。Unit名やstopという文字列・fake callbackは実systemctl/停止ではない。

BackupStepFixture.manifestは既存literal recordだけ。その他DB/Files/trace methodは呼ばない。BatchDatabaseFixtureは未変更sourceをjavacの型/signature解決用に置くのみ、static初期化なし・constructor/DB/pg_ctl/設定読取は一切呼ばない。MorningCompletedMainTestは既存ACTIVATIONのliteral static値だけを既存参照のまま使用し、当4 Testは非選択HOLD。compile依存をPASSへ算入しない。ExpiryReceiptFixtureは固定ASCIIから手書receiptを作るだけでSnapshotTestへの依存なし。MorningCleanupExecutionのnative executeは非選択、nested Completionは値整合だけ。

実Root/native/DB/VM/Backup原本/鍵/permit発行/intent退役/権限/拒否処理の再演0。既HOLD wholeからのmethod抽出や新mockによる代替0。元通知は現存せず、再要求しない。

## Test ID・独立oracle

NK-OPS001/BAK001、RD OPS009、UI251、SS341/343、SSC126/134/135/203。完全Test名/class/methodを原XMLに保存する。以下prefixは検索用で、唯一の実行IDはFQCN#method。

|既ID/対象|入力・操作と独立期待|
|---|---|
|WIRE200002、ISSSTEP007/004/005/006（Prestart5）|固定十行・五gate byte、new/failed/reusedの三公開golden全byte、13-field cross-run参照。foreign run/changed binding/欠落/null/digest既知・未知失敗/可変byte clone。expectedは承認済SS343の独立golden・固定header/手書値。Productionからexpected生成0。|
|PARENT455001/002/004、COMP203002、PARENT539001～003、PARENT540001～004（Completion11）|固定Clock/DB-shaped手書proxy、actual pair/status/reason/run/time/target/reference・全行前後read/八boundary故障。同owner値と完全row一致のみ通す。Backup FAILEDはWARNINGで起動の絶対禁止にはしない。IO/runtime/fatal/nullと同一例外identity、foreign/mutable入力を拒否。|
|STOPCOMP001/002/003-CYCLE/003-ROW（Stopped4）|既存memory stopped cycle/receiptを作り、activeとcold、世代/owner/kernel/deadline、receipt identity、全row/referenceの変化を比較する。stopcomp003は既存prefix重複のためCYCLE=CompletedCycleAndExactReceiptCannotBeSubstituted、ROW=FullRowAndOriginalReferenceChangesStillRejectの完全method名で一意化（Test source/ID増設0）。|

全既Test/source/helper SHAは13904の固定PINS/EXTRASとnormal inputHashesに保存。goldenは`src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-{new,failed,reused}-v2-golden.txt`、それぞれ842b41b0/eda4285f/f5877b39（完全SHAは工具とmanifest）。git source/live/新classes copyを一致させる。並行・実再送・実永続化・真正Root/停止はこのmemory群では未認定HOLD。

command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13904_morning_data_envelopes_whole_twenty_pt.py`。JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15、固定六Main Jar/SDK/clean ENV/新javac-Werror、Map三suite20、単一session/appendfalse。新13906独立postで原XML/退出/FES-abort-container/全source/Jar/三fixture六path/一exec CRC・型付き反例を照合する。二data-envelope完全sourceの三physical（Readは自然abstract metadata）全counterを測り、未達を保持する。実行していない依存sourceのcoverageを含めず、旧exec/sourceの合算・除外による100化をしない。

2535に元command/時刻/HEAD/source/退出/期待actual/counter/manifest path/hashとBUGを保存。障害は修正前起票、未実行/失敗/skip/unknownはPASSへ算入しない。普通の小区切りで停止せず、fresh残10又は取得不能で保全する。
