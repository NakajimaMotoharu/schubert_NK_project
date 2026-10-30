# Batch cleanup step原whole10・仕様

2026-10-30、source6b53/normal14216、主P017-07.02/関連P017-12.01追加0、着手前.5/3/6pp。NK-BAT-001/OPS-009/DAT-009/UI251/SS331§3.14/332/341、SSC057。元CleanupValueBoundaryTest全2とCleanupStepValuesTest全8・initializer/helper/依存Main全body確認済み。既819の再演なし。

対象全四Source=CleanupCounts/CleanupKind/CleanupStepChunk（Reason含む）/StepCleanupSummary、全五physical（実normal Jar確認）。BatchStepAttempt/BatchRun/BatchStepはfixture依存で、本群からそのSource全域資格へ拡張しない。

|Test ID/method|独立fixture・期待値|
|---|---|
|PT-BAT-CLEANVALUE001/countsAcceptExactBoundsAndRejectEachInconsistentComponent|六固定正常tupleと九異常tuple（負/差不整合/Long最小最大）、getter入力一致、異常IAE。production差分でexpected生成なし。|
|PT-BAT-CLEANVALUE002/cleanupMetadataMatchesIndependentDdlNamesAndChunkLimits|固定九名称/SQL function文字列/1000又は10000のtable（DDL V005/V012/V014/V026とSS341）、文字列確認のみでSQL非実行。|
|PT-BAT154/kindStepMapping|固定九step名、LOGS/skipped/異step拒否と他mapping正常。|
|PT-BAT155/successfulChunkContracts|delta2,total5→before3を手計算、zero完了/矛盾tupleのIAE。|
|PT-BAT156/rejectionAndDeferredContracts|理由四固定literal、拒否二理由はtotal absent/zero/未完、FKはQUESTIONSだけでtotal既知、各矛盾拒否、unknown enum拒否。|
|PT-BAT157/summaryCountsAndCompletion|before3/after5→call2、deferred false/trueとcomplete逆、OUTBOX deferred拒否。|
|PT-BAT158/counterOverflowAndBounds|Long最大、同値zero、逆転/skip有り/負tuple拒否。|
|PT-BAT159/nullAndRedaction|各nullはNPE、固定二redacted literal。|
|PT-BAT160/immutableValues|等値/非等値/同値hashはvalue semantics、生成hash全域とは区別。|
|PT-BAT161/concurrentValues|64 own virtual threadsの独立n/100→before100-nを手計算、5秒上限、実DB資源競合なし。|

実Gate/DB/SQL/Root/VM/鍵/原本/IO/バックアップ呼出0。command `PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14696_batch_cleanup_step_ten_pt.py`。原10/2suite/一fresh JVM、F/E/S/not-run0、全input・六Jar・原環境、14698独立post一exec/session/CRC/全closure/八metadata反例/四counterを照合、自然branch0はN/A/未達は保持。manifestでsource/hash/command/start/end/OS/JDK/exit/XML/exec/counter/ownerを記録、結果2748。正式・工数・全HOLD不変。
