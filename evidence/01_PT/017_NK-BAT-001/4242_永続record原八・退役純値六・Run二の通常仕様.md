# 永続record 原八・退役純値六・Run二の通常単体仕様

NK-BAT-001、P00403/P01702/P01712、OPS009/UI251/SS343§6.13/6.16/SS354、BUG2858/YKT2387。追加資格費 .5/1.5/3pp（うち試験製造/有限worker .15/.45/.9、全通常資格 .35/1.05/2.1）、cap4。既費用/原S/V/元190認定は不変更。

原MaintenanceRecordsTest全8は72/109/140/141 byte手書きgolden、全magic/区切り変造、UTF8/CRLF/alias/歴史年µs/NULL、配列独立所有、64並行完了値を保持する。BUG2858のworker終了だけfinally shutdownNow→awaitTermination10秒→未終端AssertionErrorへ変更し、無期限closeを使用しない。traceは新Unit専用cwdのtarget配下synthetic byteだけ、既原本/外部FSへアクセスしない。

新MaintenanceRetirementValueCodecTest全6は既HOLDのRetirementRecordsTestの抽出・代替ではなく、public不変値と純codecの独立通常試験。

|Test ID|独立期待値|
|---|---|
|PT-BAT-RETVAL-001|NKRET1の8行ASCII/LF順序・27byteUTC時刻・36byteUUID・count・64lowerhex。固定195/204byteを文字定数から作り、全accessor/encode/decode/配列非共有。|
|002|400日ちょうど/直前は拒否、400日+1µsを許容。latest<cutoff/年10000/latest又はpreparedのnano不整合、count0/負、digest大小文字/長さ/非hexを拒否。正1とint最大を許容。|
|003|run/latest/prepared/digestとcodec入出力NULLを拒否、固定redaction。constructor IAE固定診断、codec IOException固定/cause無し/suppressed無し。|
|004|literalを元に長さ、magic、各LF、追加行、CRLF、BOM、非ASCII、欠落terminalLFを変造して拒否。canonicalな別UUIDは値として許容し所有を推定しない。|
|005|UUID/time/count/digestのalias・overflow・date不正/年0・nanosを独立に変造。再encode一致による拒否、0padding/+count/uppercaseUUID/hex禁止を確認。|
|006|原byte所有・二回encode非共有、等価性と固定redaction・全accessor、400日超とUTC年上限を固定入力で確認。GC/DB参照/実原本削除の許可にはしない。|

必要補助回帰BatchRunValueBoundaryTest原2は新5Main全scopeでRun/Activationの年/µs/null/JST契約を担う。旧2成功の再確認単独ではない。Main: MaintenanceRecords, MaintenanceRetirement, BatchRun, MaintenanceActivation, MaintenanceCompletion＋Outcome enum（物理6）。JDK/JSpecify/JUnitのみ。全source/物理は対象から除外せず未網羅を保持。新Test6はproduction methodからexpectedを生成しない。通常prestyle→RootNullAway/lintWerror→PMD/CS/SB全physical→preflight→Git source固定→一whole16→独立postの終了/全XML/FES0/一exec/6CRC/初期化/四counterを確認。失敗/未実行/coverage未達をPASSへ算入0。

実Root/VM/native/原本/DB/Backup/鍵/intent/permit/部署・Unit/退役・cleanup操作0。既GC実環境TestはwholeHOLDのまま、合成能力を発行しない。工数完成率null、正式1964PT/53scopeを更新しない。
