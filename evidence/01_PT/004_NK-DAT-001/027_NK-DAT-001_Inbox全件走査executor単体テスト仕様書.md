# NK-DAT-001 Inbox全件走査executor単体テスト仕様書

対象InspectionRunExecutor.run/InspectionExecution constructor・exitCode・toString/Status、RD DAT-009/OPS-009/MQ-008、UI251 §6.1、SS324 §12.7/341 §7.3/343鍵寿命、QA-046/UIC-006/SSC-049、PG-D-130。既存独立JCE/手組wireと実PG18/限定role fixtureを再使用する。期待件数はliteral SQL後条件、時間は単調clockの固定列、鍵はtest時生成し保存しない。

| Test ID | Method/目的・操作 | 期待値と根拠 |
|---|---|---|
| PT-DB-INBOX-097 | emptyAndCompletedRunsSucceed | 空END、既完了再読はSUCCESS/0・確認済0件/complete、SQL候補を再処理しない |
| PT-DB-INBOX-098 | protectedRowsEndWithWarning | unknown/不正rowは保持、END時だけWARNING/10、literal件数・SQL残存一致 |
| PT-DB-INBOX-099 | moreThanOneChunkCompletes | 1001不正rowで1000上限を跨ぎEND、全件保持・累積1001、固定run/cutoff維持 |
| PT-DB-INBOX-100 | deadlineAndClockBoundaries | 30分未満/一致/超過・時計後退・nanoTime wrapを固定clockで試験、開始前停止は未確認Optional空、終了後超過もTIME_LIMIT/50 |
| PT-DB-INBOX-101 | interruptionRemainsVisible | 開始前/SQL直後interruptでINTERRUPTED/50、flagを消去せずDB確認済値だけ返す、test終了時に自身のflagを清掃 |
| PT-DB-INBOX-102 | storageFailurePreservesLastConfirmedOnly | 最初/次chunk故障を実JDBC providerで注入、STORAGE_FAILURE/50、失敗chunkの途中結果を推測せず同run再読で再開 |
| PT-DB-INBOX-103 | resultAndNullContracts | null依存/run/Optional/status、成功と未完了・保護count不一致拒否、failureはcomplete進捗も最後確認点として可、全status exit/表示 |
| PT-DB-INBOX-104 | failuresDoNotLeakOrBecomeSuccess | cause-freeDB失敗、ID/cutoff/cursor/秘密非表示、予期しないprogram例外を成功catchしない、時間切れ後同run再開正常 |

全null/正常/境界/異常/例外、割込・1001件・再実行を実行し、failed/flaky/skipped/not-runを成功へ算入しない。既存100並行所有TX試験は正式rootの回帰で維持する。executorはprivate process一worker用、複数run共有instanceの並行性は局所変数だけで保証し、key rotationは外側OS lockで禁止する。

探索・正式commandは028で実施後確定。正式root clean verifyと8collector/20scope（新executor含む）のhash/trace/負canary、line/method/class/branch100%、静的解析0、旧V001～013/Current baseline不変、秘密scanを要求する。source/branch/日時/OS/tool/command/exit/Test ID/期待・実際/coverage/BUG・SSC/path/hashをevidence/inbox-run-executor/manifestへ記録。PG/PTのみ、process/OS/key wiring・実NK CHR/IT/STは未完了。
