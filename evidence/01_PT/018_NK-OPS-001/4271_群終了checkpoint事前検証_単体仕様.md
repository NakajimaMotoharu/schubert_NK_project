# 群終了checkpoint入力事前検証・工具単体仕様

WBS-F03、BUG3006/YKT2535、451/487。対象tools/quality/pmo_stage_input.py validate_checkpoint_textと1100管理writerの呼出順。製品アプリのPTではなく管理工具単体試験、正式1964/53・app run件数へ加算しない。

|ID|事前fixture/入力/操作|独立期待値|
|---|---|---|
|PT-OPS-ENDINPUT001|end/日本語改行・前後空白のtext+別summary|原textをbyte同値で返しconfig不変|
|002|start/空object|None、end field不要|
|003|end/summaryだけ|ValueError固定nonblank message、補完しない|
|004|end/text null|同ValueError|
|005|end/text空|同ValueError|
|006|end/text ASCII/全角空白だけ|同ValueError|
|007|end/数値・bool・collection|同ValueError、文字列へcoerceしない|
|008|未知/大小文字/欠落mode|ValueError registered stage mode required|
|009|start/endでnull/非object config|ValueError stage config object required|
|010|今回元summaryだけのbad shape|拒否後config不変、repair/event/IOなし|
|011|startのget禁止dict|None、end値読取なし|
|012|1100 ASTで事前callと全mutationの順|呼出1、全append_start/metrics.append/writeより先、工具を実行しない|

正常期待は明示literal、例外型/message・元config完全同値・許容field読取有無を独立規定しproduction helperでexpectedを作らない。全12は通常unittest、skip/expectedFailure0。source moduleの全line/branch/関数実行をcoverage.pyで測定、除外pragmas追加0。scopeはこの新pure helperだけ、1100 whole-engine/外部event IOや451全工程はこのcoverageへ混ぜない。Python null/missing/empty/unknown/誤type負例、nonreturn並行/再送はこのpure無資源functionに非該当、既event5402や仕事を再発行しない。

実行は3435の固定source/hash/command/環境/終了code/XML相当unittest結果とcoverage JSON/manifestへ対応する。SDK/Java/class/DB/Root/VM/native/aruを呼ばず、実tokenは欠測null。既end5402/台帳26/ProductionCOPYsourceの試験成功を確認のため再演しない。

追加独立PT-OPS-ENDINPUT013: writer自身へ元summaryのみのshapeと存在しないquota pathを渡し、固定ValueError/child1、quota未読取、公開events/state三つhash不変を期待する。3437/PG33724、12単体と別scenario、coverage合算なし。
