# Batch標準SDK依存oracle 是正結果

2026-10-28、2331/PG-D740/BUG1970～1973/YKT1718～1721。最終source1be156b6ebb139713db31a561b8b024972975471/dev-foundation、中間oracle92941a174c9dc82289addcc20ef6d95f5f53314eを保持。Production Main/POM/上位仕様は不変更。旧期待八座標が既承認SDK二座標を欠くsource-level不整合を是正したもので、未実行旧caseを実測失敗とは記録しない。

原BAT283/B283B＋新BAT283Cの **3件/1suite全成功**、F/E/S/aborted/container失敗0。新TestIDはPT-BAT-283C一件で、正式受入の新規一件ではない。標準SDK二座標だけ期待集合へ追加、固定版1.17.1・compile既定/明示・jar既定/明示を受理し、各欠落/重複・旧版・空/誤scope・空/pom type・二重scope/type・foreign classifier/group/nullを独立literalで拒否した。旧全oracleは二新座標/明示SDK検証呼出/新private helper/新case/二同値共用定数以外をtoken逆で保持。その後の既知五String/33参照は中間source全tokenへ逆変換できる。

|証拠（evidence/provisional）|結果・SHA256|
|---|---|
|PG12402-batch-runtime-oracle-discrepancy-v1|0/source不整合差二/正本hash / a3a5e425e082e01a0a5835ac25a48dd19b4439d725f89e54ecc2f9fe5c044df8|
|PG12404-batch-runtime-oracle-source-post-v1|0/六異常 / 252f1348b9bfc70035cfb52c0c4fb464383e81e07a9c1de9bfdff64e3849f905|
|PG12405-batch-runtime-literal-source-post-v2|0/五定数33参照/15異常 / 3ff685e47422a09a15eb51f067e675b715a8854d6d14406e5d9e327326ea435d|
|PG12406-batch-runtime-six-compile-v1|0/六module PT0/session8714真正0 / f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3|
|PG12408-batch-runtime-host-v1|0/3件/session5339真正0 / 35387e38bb66de3240eb74086666fc6dd91cd8b68a5ee511b364dc9fc2d9d006|
|PG12410-batch-runtime-static-v1|0/PMD-CS-processing0/session96160真正0 / bb56b5c564bea635bea8d9cd167330f249dc53996b4c7892432bad9e98f43d93|
|PG12412-batch-runtime-post-v1|0/XML一exec/CRC/全Main・物理差/session82058真正0 / 490c60f253fb284855962bd4832a7ad3dc1cbedb6f3b52457f9fdd4d5fd9d6d0|
|PG12418-batch-runtime-trace-v1|0/983一SHA / e216153b1e7151ef811c19aa839e1d3aa6f4b0f74bd0ea929d199bed94bbc85f|
|PG12421-batch-runtime-trace-post-v2|0/六非同値異常・post参照限定補正 / db6689a2b8a4f4d062017e7bc7b4b2647b6f75ebfad52ac48f46e176ce34772f|
|PG12424-current-batch-runtime-delta-v1|0/五原IDだけ消去 / 466a2d8c537975bfee8de7c83633f38ce33dffb319c9fd326f82d8e248362268|
|PG12426-current-batch-runtime-delta-post-v1|0/八異常 / f2cf2bfb976182027f93fd5b320e12da9334abf47cb9671c0f53fed0ad3cccf5|

各checked command/実argv・OS/JDK/時刻/branch/source/試験method・input/hash/期待・実際・XML/exec/CRCはmanifestへ記録。JDK25.0.4/Maven3.9.12/JUnit5.13.4・Platform1.13.4/JaCoCo0.8.15/PMD7.28 record1298/CS14.3/GJF1.36.1、Enforcer/Spotless/NullAway-JSpecify/-Xlint-Werror維持。frozen snapshotのPOM一fileを正規propertyで読むだけで前後hash一致、own空CWD/原一回exec PG12408-BATCHORACLE-JP。DB/JMS/network/VM/Root/native/実鍵・Product Main呼出0。原成功確認再演や保留fixture部分抽出0。

独立Main probe whitelistは当Test rootだけで許可以外probe0、全1843 Main byte同一、変更Test物理1/他1961同一。完全Batch645（解析644/package注釈1）の実coveredはL/M/C/B全0、missed18416/3205/413/8458。Java Mainを実行しないPOM契約のcoverage資格はN/Aであり0/0を100又は全Main coverage100%へ変換しない。Test probeをMainへ移植せず、標準filter/自然非実行分母を保持する。

横展開1718：WebRuntimeDependencyTest全文はPostgreSQL一依存の版/scope検査だけで非test閉鎖集合を持たず当SDK追加に非該当。API bootstrapに同名runtime依存Testは無く、三module Test内のassertStartupDependencies/RuntimePostgresDriverAndScopeCanaries/exactly-one-JDBC検索ではBatch/Webだけを確認。API側の全依存保証や新PT成功を捏造しない。1719全五literalの同値化と全三case/静的0、既oracle版を維持する。trace元owner/cost F02・changeOwner F02/F03副担当費0、原logical join一UNKNOWNと元registry既根拠を区別し、983一SHA以外982不変/全WBS監査前後同HOLD1。

工具1972は旧12405不要Path/先行AST1を呼出側で無視→checked lint1/bodyfalse/OUT無し。旧entrya1a14d65は不変、新v2 entrybf798a4dでimportだけ除去/15異常0、以後preflight非0throwを適用。新12424 draftのASTが不要importを検出した時は実際に後続entry発行を止め、初回bind前だけ修正してから初回checked0を得た（既bind工具の書換えではない）。工具1973は旧12420 body1/entry0ce5497f/OUT無し、owner全体置換で負例costが正例F02と同じになった不備。旧writer成功を保持し新12421v2でbad != referenceを全六件先行確認、誤costF03等を拒否し485二post参照と486inventorySHAだけ補正。1972/1973は製品試験の失敗やplatform拒否ではなく工具不備二件。

現行集合9409−864是正＋追加8保持=8553（Main1512/Test7041）、refs3135/pending720/未参照5418。全体静的の実再発行値ではなくsource差分の追跡集合、追加8を消さない。正式1964PT/53scope・17/190・工数null/QA051final/全F03-451/HOLD/原見積は不変。元群1/3/5cap10、五styleは追加発見として分離し二重予算無し。共有62→63の差は専有費でなくN/T不明null。完成manifest/最終cursor/保存commit/pushは2333/456へ。通常小群で止めず許可済み後続PG/PTへ進む。
