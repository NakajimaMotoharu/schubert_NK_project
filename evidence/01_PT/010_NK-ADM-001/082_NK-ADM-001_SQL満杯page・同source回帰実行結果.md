# 三照会・有効page/state投影の同source回帰結果

2026-10-26 09:26 JST、ADM081/QRY005、群2293/P013_QUERY_VALID_PAGE_STATE_BATCH_V1、開始1/3/8pp cap10。source `dd138e9def675f9278ae4b1bdb8c5ee3e34f2b77`/dev-foundation、Main最終21dは不変更。当52method/7suite全成功、failed/error/skipped/aborted/container異常各0。新4ID（ADM-SQL009/LOG-SQL009/QRY-SQL009010）＋関連48であり、新52IDではない。

## 各programの追加実績と独立oracle

Userは全17method（Core4/Boundary4/SQL9）、Log17（Plain8/SQL9）、質問通知18（Plain8/SQL10）。User満杯50rowはid1～50・username u101～u150のC順とid順が整合するvalid tuple、Log満杯100rowは同時刻/id100～1、質問満杯50rowはid50～1と一意受付IDを手組。各page/count/first/last/元page/typed全row・borrowed所有が独立期待値へ一致。fixtureの順序を保ったmapperの検証で、実DBのsort/lock等を実証していない。

通知のPROCESSING/CANCELLED/ERROR五codeは正常保存business rowの投影であり、SQL又はJava例外を起こす試験ではない。固定wire文字列→独立enum対応、型/全任意時刻mask/本文保持・answer不在/owner8/target3が期待値へ一致（QRY005/同Test.sql009）。sourceハッシュ付きTestをinput/expectedの正本とし、実XMLと全assertion成功をactual同値証拠とする。実wire/DB rawの出力を新規保存していない。

## 実command・環境・証跡

repoから `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/<工具>.py`。Linux amd64 7.0.0-38-generic、JDK25.0.4+7/Maven3.9.12/JUnit5.13.4-platform1.13.4/JaCoCo0.8.15-ASM9.10.1/PMD7.28-CS14.3。実子command/開始終了UTC/終了code/依存/input/class/exec/XML hashは公開manifest/stages/receiptに保持。既toolchain使用、新規install/料金/券/外部操作0。

共通公開prefix `../018_NK-OPS-001/evidence/provisional/`。

|run/工具profile|真正結果|manifest SHA256|
|---|---|---|
|PG10096-query-batch-precommit-static-v1 / pg10096_query_batch_precommit_static|原三Test hash、rawPMD8/CS0/processing0/exit1、PT0|6be9f24ad837cf125643ccc7e260b10bf9aae56cbcc6e5519cfb8259c3d4599a|
|PG10098-query-batch-precommit-static-v2 / pg10098_query_batch_precommit_static_v2|是正後三hash、rawPMD6/CS0/processing0/exit1、PT0|2d7a7a6d3e19809b001e25e268bdf731bc02541345b7d0efc1947567a1e664e4|
|PG10100-query-batch-six-compile-v1 / pg10100_query_batch_six_compile|正常六compile/package0/NullAway-Werror、PT0|a2a8eb62b574693a47e5ce82b830185a7db3fd41f4af61ba4341b598c5f8e3f3|
|PG10102-query-batch-preflight-v1 / pg10102_query_batch_preflight|closed52/7、Test physical13、Main physical7/六unit、source/hash0|28acacaad47d55acfbb698a206d79cb4d6d6e04a30fa332709b9ae0fd5fe2b19|
|PG10104-query-batch-host-v1 / pg10104_query_batch_host|一JUnit/一exec/session append=false・52全成功0|1636ab4dbc7822ded2675cda9820b5af1bec40f091bbdf717f9c0e301f79ac9a|
|PG10106-query-batch-post-v1 / pg10106_query_batch_post|全XML/CRC/session/七physical・禁止product probe0/実0|b83f269bd2f8573e5e9f10341ad4fc96d6b0a93589e98d0c11e66467c00f0b2d|
|PG10108-query-batch-quality-post-v1 / pg10108_query_batch_quality_post|全Main1843同byte・scope外Test1922同byte、当static/旧oracle token不変/実0|0e8f91b6eebb5f67081f9232b4fbb5dbb625cb92775458e5d171ad63b9e35360|

当Test SHA256: User `7c08ce9b15f707354b77a02537dafa95d3c21c2976d522ca9c8b436ea2492bb9`、Log `e364cbaac8b3438dd07fb904938b13bb70673ee43836da55d4c788208335eddf`、Question `091d86412f47c06d63eb91df04eabd1e1bab46ec5721cb0ebd7fafd333e8f576`。各caseの固定input/expectedはsource内新methodと元077/079/QRY003、実際は52 case XMLとassertion成功に一意対応。Synthetic dataのみ、秘密/実session/token/鍵/原本DBを保存なし。

## 当一source/runの完全unit coverage

|unit（CRCは10106に保持）|line covered/total|method|class|branch|全四100|
|---|---:|---:|---:|---:|---|
|UserQueryRequest|62/62|13/13|1/1|18/18|実測100%|
|LogRequest|46/46|12/12|1/1|6/6|実測100%|
|QuestionQueryRequest|102/102|16/16|1/1|32/32|実測100%|
|UserQueryRepository|125/134|17/18|1/1|33/52|未達|
|LogQueryRepository|107/113|18/18|1/1|23/38|未達|
|QuestionQueryRepository|158/170|30/30|1/1|49/64|未達|
|QuestionQueryRepository$RowMapper|0/0|0/0|0/0|0/0|Codeなしinterface/N/A、実測PASSではない|

旧source/run exec合成なし、今回だけで三Request四100を測定。Repo異常/不正DB行/例外graph及び実DB構文/plan/整合性/並行/lock/後条件は未実施、HOLD/未網羅を維持。全七physicalを含め、interfaceを除外して100にしない。

## 障害・静的/旧oracle保持・非影響

BUG1793/YKT1544を修正前起票し、Log/Question total列literal各四箇所を是正、User三箇所は同種予防集約、三Test-local COLUMN_TOTALの同値化のみ。旧raw8/1を保持、当raw6はstandalone proxy loader/serial private Mapを各source/行へ個別非該当として結合、抑制なし/CS0。Raw exit1を0へ偽装しない。

10108は新四method/新定数/Questionのenum import追加を取り除き定数参照を元literalへ戻したJava lexical token列と、9eac固定原source全文の全token同一を確認した。文字列/char literalも保持し、旧assertion/expected/fixture/制御構造の変更0。独立九metadata変造を拒否（製品PTではない）。正常全Main1843 raw同byte、全Test1931キー同一、選択九physical以外1922はraw同byte、選択九中raw差六は新四method/同Testのline変化を含み当source/hash/実52へ結合。選択九の全非debug同一とは主張しない。

自己normal51204/host15572/postは真正終端0、旧成功確認だけの再演なし。新三Test SHA/四IDのtrace更新は次工程。現Java1803/Main965/Test838、集約は9eac/1801-1803の旧SHAのまま（新source登録と区別）。正式1964PT/53scope・個別17/190・新受入0・工数null・QA051final/全安全HOLD不変。fresh used28残72/reset1793513544、群開始27→28共有丸め+1≠専有費、usage bd840beb/N-T配賦null。通常group/commit/報告で停止せず継続。
