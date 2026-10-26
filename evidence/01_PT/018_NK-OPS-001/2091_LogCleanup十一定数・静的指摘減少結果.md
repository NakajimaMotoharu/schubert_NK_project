# 2091 Log/Cleanup十一定数・静的指摘減少結果

2026-10-26、2090仕様/BUG1850/YKT1601。source95894757e2bd7f392262497ea620873430ccc5f1、Main21d不変。Test二fileに同値十一定数（Log七/Cleanup四）を追加し、全64参照（48/16）を置換した。Production enum/DB出力をexpected生成へ使わず、独立fixture literalの元値を保持した。

|公開manifest|SHA-256|真正結果|
|---|---|---|
|PG10608-log-cleanup-literal-plan-v1|806f49d93184aca7d460c885d15d877bdd2531615b2bdcb57a28589e00cec6ab|0、逆展開全token/同値String連結保持、十metadata反例|
|PG10610-log-cleanup-literal-static-v1|ece9dc5461f5cd2dd24a1a62c7a4bd3c9d236d8bec737fed23791401f4ceb8b5|1、PMD50→39、duplicate十一消滅/Checkstyle0/処理0|
|PG10612-log-cleanup-literal-compile-v1|7e484e3e66d5f8b678c933a8628d40e4ecb7d145d1f426d8372c9e22d411fcf1|0、六module正常compile/package・PT0|
|PG10614-log-cleanup-literal-post-v1|d52b92859b889cbae3d5cfaeafb3933d194cb4a4d74ae2f7443c156c3a0b8075|0、独立declaration/token照合・SQL改変二反例、Main1843/他Test1959 byte不変|
|PG10616-log-cleanup-literal-trace-v1|3cca89557df11386447aea107314888e523202d5e977cc7b3c2822c6fcbc7a57|0、最終SHA二行のみ・他981行不変|
|PG10618-log-cleanup-literal-trace-post-v1|0888f30052fca28b0fc14d02445a7083d66d00d13cd085f6ee82d3c57fc31290|0、八metadata反例・原941/943/予算/受入/unknown二保持|

manifest相対pathは本018_NK-OPS-001の `evidence/provisional/<上記名>/manifest.json`。command/OS/JDK25.0.4/Maven3.9.12/固定PMD7.28.0/CS14.3・入力/source/真正exitは各manifest/正常begin/terminalへ保存。PMD型baselineは再演なしのc919/10558 Main、095/10598及び当958/10612の全1843 Main byte不変を別照合した。current Testのhash一致と正常compileを保持し、type baselineの古いPTを当sourceへ転用しない。

変化したphysical Testは三（当二sourceに属するouter/nestedのみ、SourceFileも独立確認）、総1962維持。残39は元50から十一duplicateを除いた全指摘と行/列位置以外の全fieldが一致。内訳thread18/null代入10/条件内literal5/generic catch2/借用資源2/classloader2、適用性は未完でありraw1をPASSへ変更しない。十一除去は当50件範囲の22%であり、全F03/PGPTの22%ではない。

工具手戻りBUG1851/YKT1602：formatterが既長文SQLを同値Stringの連結へ分割し、初回raw token比較がactual1/OUT前停止。原工具SHA e397f13081c5dd7971a8e1270ee46c86c901c9b326d9f9f8fe19fe7c5b5d0eedと失敗を保持。限定String連結foldだけを許可、numeric演算変更/SQL改変/未知定数/誤literal/他assert変更を拒否した。元試験や正常compileの再演を失敗補完に使わない。

原owner/cost P01004/P01707・既983row/1810-1808/UNKNOWN二・全予算/正式数/工数null不変。所定WBS前後監査は真正actual1/同HOLD、旧固定診断proof/Trace十PT/他旧runtimeを全て元sourceのまま保持。元DB/JMS/鍵/故障graph動的PTはNOT_EXECUTED_HOLD・coverage null・実PT増0/新個別受入0、正式1964-53/17-190/QA051final不変。

共有used10→11/reset1793599188の+1ppは共有観測であり専有費ではない。実token/専有費null、cursor adce55fe3f8da92fdfe83bb765adf0cb3159bd601d00da28472f3887401d6e35。全own compile/post終端0、外部所有未観測HOLD・新VM/DB等操作0。次は公開保存push後、残39のsource文脈と既後続成果を限定点検し、元fault PTを起動せず独立PG/PTへ継続する。
