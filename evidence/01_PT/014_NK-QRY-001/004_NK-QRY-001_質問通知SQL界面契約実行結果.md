# NK-QRY-001/NK-NTF-001 質問通知SQL界面契約結果

2026-10-26 09:07 JST、仕様003、source `9eac6bffd8462aea5d0d0759cb14fdef5b1a1a3e`/dev-foundation。新PT-QRY-SQL001～008八method＋関連Plain八method=16/2suite、全成功、failed/error/skipped/aborted/container異常各0。五filter32mask/通知三filter八mask×二actorを一意Test ID八の内側で検証、反復数を新Test IDへ増やさない。

## 実行・証跡

commandはrepoで `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/<対応工具>.py`。固定source/snapshot/input/開始終了UTC/実子command/終了/OS/JDK/依存byte/exec/XMLは各manifestとreceipt。Linux amd647.0.0-38-generic、JDK25.0.4+7/Maven3.9.12/JUnit5.13.4-platform1.13.4/JaCoCo0.8.15-ASM9.10.1/PMD7.28-CS14.3、既toolchainのみ。

公開prefix `../018_NK-OPS-001/evidence/provisional/`（014からは実相対`../018_NK-OPS-001`）。

|run/工具profile|真正結果|manifest SHA256|
|---|---|---|
|PG10074-question-sql-precommit-static-v1 / pg10074_question_sql_precommit_static|Test-only base6cd、rawPMD2/CS0/processing0/exit1|29b6e3792a79debde2f1abcd224350d3e1292abedda4e927d1225d6badfe9f1f|
|PG10076-question-sql-six-compile-v1 / pg10076_question_sql_six_compile|正常六compile/package0/NullAway-Werror、PT0|9ba6f1fabcda3a665fd2222fd21a9c2c6095ae773ec1cb37b408374ae8bc287d|
|PG10078-question-sql-preflight-v1 / pg10078_question_sql_preflight|固定16method/2suite/完全二source unit・三physical Main照合0|a2c19b0e81ccaa703e8f11586442dcbae7eccc403dc92b8b4255c605c832ac73|
|PG10080-question-sql-host-v1 / pg10080_question_sql_host|一JUnit、一session append=false、全16/2成功0|975bd1bfb678dcbebbacf55ef9d5f127d5c009ad505ddaa3d9559425828e5b76|
|PG10082-question-sql-post-v1 / pg10082_question_sql_post|全XML/exec/CRC/session、禁止product probe0、全三physical/空interface保持0|c3c001763eb2794795447ea287333eea752b0fa1162d967a26ec9e54137eb907|
|PG10084-question-sql-quality-post-v1 / pg10084_question_sql_quality_post|static当source一致/全Main1843同byte/旧Test1928同byte＋新3class、実0|a920acc8dcd5a2ea71563ccdc22c957411ca5a6f3267ba53c41372e56ab9de57|

当新Test SHA256 `687ce34324c5f61c979dd4b2d4c2435ee3b8d1e528fa1870bd423f410297d4bd`。input/独立expectedは003/同Test、actualは全SQL001～008 assertion成功/XML。USER質問owner7とADMIN質問owner非限定、通知はADMIN8も本人、target bind、削除済みtext非復活、CodePoint100要約/全文保持/UTC ms/空結果・任意時刻・借用Connection不変更を確認。全正常JDBC三Connection call/prepare/execute各一・RS→PS各一close。実DB/key/secret/外部操作なし。

## 当source、一runの完全物理counter

|物理class/CRC64|line|method|class|branch|判定|
|---|---:|---:|---:|---:|---|
|QuestionQueryRequest / b452eff84f48d993|102/102|16/16|1/1|32/32|実測四100%|
|QuestionQueryRepository / 766eb30e6c84ea1d|156/170|29/30|1/1|45/64|全四100未達|
|QuestionQueryRepository$RowMapper / 43e34ef8a59fd945|0/0|0/0|0/0|0/0|Codeなしinterface/N/A・実測PASSではない|

interfaceをexcludeせず全物理集合・SourceFile・INTERFACE flag/全method CodeなしをJDK classfile APIで照合。target classをload/init/invokeせず、空counterを100へ変換しない。Repository SQL catch/不正row/ERROR code等未到達は残し、Graph9/鍵関連等禁止product probe0。実PostgreSQL構文/plan/lock/並行/整合性/後条件は本proxyでは未実証、既DB試験/HOLD維持。

rawPMD二はline366 UseProperClassLoader（standalone公開interface proxy/非JavaEE）とline374 UseConcurrentHashMap（method毎serial自己Map/parallel=false/自己threadなし）を10084で個別非該当と当static-byteへ結合。raw1/二指摘は保存、CS0/抑制追加0。新障害なし、BUG1792/YKT1543旧Log表示だけの是正は保存7ea/origin確認後に限定close、元qualified全文/原表示を保持。

現Java1803/Main965/Test838、新Log/Question二pathの集約traceは次batch。三Request四100はUser=dac/10047、Log=6cd/10068、Question=9eac/10082の別source/runで保持し、同一source全scope成果へ合成しない。正式1964PT/53scope、個別17/190、新受入0、工数null/QA051final/全安全HOLD不変。通常成功/commitで停止せず、次の独立作業へ継続。
