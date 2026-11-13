# InspectionAttempt原八件・有限worker単体仕様

NK-DAT-001（primary WBS-P004-04）、関連NK-BAT-001/P01702のデータ型は再費用計上しない。RD DAT-009/OPS-009、UI251、origin/main SS331 3.13/341 7.3（SSC049/PG162）、PT-BAT122..129。公開whole73行・元Test whole213行・関連BatchRun/CleanupCounts/InspectionSummary/MaintenanceCompletion/MaintenanceActivationの全sourceを審査。すべてJDKのimmutable値であり、Root/子/DB/Backupの成功証明を生成しない。Main6/physical7（Outcome nested enum含む）を正規compilerと全静的へ渡す。whole元8件、新定義0。追加価格 .3/.9/1.8pp、上限3pp。一回だけ計上。

|Test ID|目的・入力|独立期待値|
|---|---|---|
|BAT122|累積(7,7,0)/(7,3,4)、before無し、receipt0/10|累積/attemptは同固定値、SUCCESS0/WARNING10|
|BAT123|zero、before(5,2,3)→after(9,5,4)、未完→同値完了|zero、差分(4,3,1)、累積(9,5,4)、同値差分zeroでもWARNING10|
|BAT124|before既完了→同値/件数変化/未END|同値だけattemptzero、変更は固定IAE、cause/suppressed無し|
|BAT125|target/deleted/skipped減少、attempt>cumulative、Long.MAX境界|減少/過大は拒否、(MAX-1,MAX-1,0)→(MAX,MAX-1,1)差分(1,0,1)、加算でoverflowさせない|
|BAT126|異runUUID/µs cutoff/after未完、同値別record|不一致/未完拒否、同値別recordは許容|
|BAT127|receipt -1/1/20/30/50/70/MIN/MAX、null7口|通常0/保護10のみ。nullはcontract違反として拒否、catch NPEによる正常化無し|
|BAT128|同値/違attempt/異outcome/toString|value equality/hash整合、固定redacted文、累積保護とoutcome一致必須|
|BAT129|64独立run、before(5,2,3)→after(i+9,i+5,4)|各UUID(0,i+1)、attempt(i+4,i+3,1)、累積(i+9,i+5,4)、WARNING。全Future10秒、finally shutdownNow/await10秒の終端assert。|

BUG2833/YKT2387：元TWR executor.closeはFutureタイムアウト後に無期限待ちとなり得る。元8件・固定入力/期待値・submit/getを保持して、finally shutdownNow＋有限awaitTerminationと終端assertを追加する。旧whole sourceを保存し逆変換一致を確認。構造negative controlsは製品PTへ加算しない。Failed/flaky/skipped/未実行を成功へ補わない。

期待値はSS341のafter−beforeを上表の固定整数で独立計算する。production reconcileをexpected算出に呼ばない。正常、拒否、null、最大値、並行を元whole8で確認し、coverageは対象全InspectionAttemptと全物理scopeを別々に記録、関連未網羅を除外・旧run合算しない。実DB/advisory/子unit/原本/鍵/native/actual4.class/VM/権限操作0。同source/run、JDK/OS、全XML/FES、終了command、CRC/class-init/coverage/hashは各manifestへ保存。F02/F03/451/元190の受入は別条件。
