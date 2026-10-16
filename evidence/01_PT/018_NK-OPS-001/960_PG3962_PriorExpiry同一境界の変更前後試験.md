# PG3962/3964 PriorExpiry同一境界の変更前後試験

NK-BAT-001、SS331/343/SSC117/PG-D421、主担当WBS-P017-07.02（親07・.01/.03参照費0）。新規Test ID **PT-OPS-EREQ3962-001** / ExpiryWorkerRequestTest#ereq3962001ImmutableStepAdmissionDefinesIdentityAndStartBounds。公開constructorの独立境界/原本identityを確認する限定PTであり、cleanup SQL/全例外・全child条件の完了ではない。

fixtureは固定UUID/cutoff2026-09-30T00:00Z、id外側-1/0/1000000000000/Long.MAX、attempt外側-1/0/100/Integer.MAX、start cutoff-1µs/1ns精度違反/西暦10000。期待Iaeの固定message identity又はtime・cause nullは独立literal。正例id1/999999999999・attempt1/99・start=cutoff又は+1µsは全fieldを入力値へ照合。invalid id＋null endは元先行null契約を維持。既6件のend時刻/µs/NULL/固定NKEXPIRY golden/未知・欠落・erasureも同じsuiteで実行、Production methodからexpectedを生成しない。

| Test ID | source/実行 | 実結果 |
|---|---|---|
| PT-EREQ-3962-BEFORE | Main6b63111ae、Test snapshot536e1832d845287f24f5cc44605a8db1448647b2。新only3962で当Main fileを再compile | 全7件actual0/FESAbortedNotRun0、PriorExpiry line13/method2/class1全miss0、branch16中5miss |
| PT-EREQ-3964-AFTER | Main/Test snapshot7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e。Test byte不変・src差分はMain一fileだけ、new-only3964 | 全7件actual0/FESAbortedNotRun0、PriorExpiry line11/method2/class1/branch6全miss0 |

1Main familyをfresh再compileし同byte main-imageだけをJaCoCo分析、NoMatchを拒否。old7fff全六jarは公開ABI/immutable依存の補助classpathに限定し、BatchRun/BatchStepAttempt/BatchStepのsource同byteを確認。入力Main/Test/helper・全補助jar前後hash不変。JDK25.0.4/lintWerror、JUnit1.13.4/JaCoCo0.8.15、Linux。新Main全体のNullAway/SpotBugs/coverageはこの7件で完了にしない。

公開**PG3965** manifest **898681fc45521604fcf6dbd531da22e1caa23aafbc52162ae04c4f5cd8f8137c**、前後原XML/匿名化Main-family coverage・実command/時刻/compiled Main SHA/元server SHAを保持。元PG379/3962・3964入力/ログ/execはprivate保全、raw session/native/DB/key公開0。変更前後14件と新規JUnit1件を合算しない。新source全体3717は未実行/未認定、正式1964/53・工数null・QA051final保留は不変更。
