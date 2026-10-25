# User要求plain正規化四・実行結果

2026-10-26 07:11 JST、2012仕様、WBS-P010-01、群2271/P010_PLAIN_CANONICAL_CORE_V1。Main最終21d7c3042、当Main/Test source70165b0768a1fabd13371cc25a55978fcf3452ba、branch dev-foundation。Production変更0。新Test四ID CORE001..004＋関連既VAL001..004の必要回帰四、単一run八/二suite（八新規ではない）。正式1964PT/53scope・17/190・工数null・QA051finalと全安全HOLD不変。

## 元結果・是正

初回source1ae3929bc/PG9964はactual1、8/2中7成功1失敗。公開manifest SHA256 a31b50c754a40db62980c9bd4c81b7f4e87ec6dd7e3b46f695dfb38037ee8045、元XML hashは同manifest、原本はWork PG379/pg9964-plain-core-host-v1/xml。core003がlogin layoutとpresent contextの不整合でheader構築時にLayoutValidationException、decodeへ未到達。BUG1783/YKT1534起票後、通常unknown ZZZREQ01へ一literal修正70165b076、Main/固定PermanentProtocolException期待値/上位仕様不変更。旧7成功を新8へ算術合算せず失敗を保持。

9972準備の旧normal public path残存はBUG1784/YKT1535修正前起票。元工具SHA3706ef72f8f41d0f9b1b6a6e16693a01ae36bc2bf383340d4863e3605fb0e937、immutable digest拒否1はSLOT/OUT/JUnit作成前。9970/72/74/76の旧参照検索は当一箇所だけ、正規9968へ修正後に初めて当八JUnit発行。9968初回import不足1・9970早期manifest未生成読取1も試験ではなく準備失敗として記録し、PT成功へ加算しない。

## 当source証跡

以下は evidence/provisional/配下、各directoryのmanifest.json。command/時刻/実終了/入力source・依存hash/XML/execは当manifestへ束縛。

|run|実結果|manifest SHA256|
|---|---|---|
|PG9968-plain-core-fixed-six-compile-v1|正常六module compile/package actual0、製品PT0、NullAway/Werror|277ca65ee5a596e94d9e222d919ed8acd4e3a7efe72883446b769db41e51363f|
|PG9970-plain-core-fixed-preflight-v1|実0、宣言8/2・当Test byte・Main1、null-only query/fixture限定確認|1e7d41bc27f086663ab78e20018172751eb186fb71f4b9f421eeed583756b7b3|
|PG9972-plain-core-fixed-host-v1|実0、found/started/succeeded各8、failed/skipped/aborted/containerFailed各0|b1418cab0a64990e600c40daeee584864bf6eda522187ac5adab9c846ac8f76e|
|PG9974-plain-core-fixed-post-v1|実0、全XML/一session/CRC照合、全UserQueryRequest unit部分coverage|7e37b3f71ef9716661798c908ec231c45a2883cbe0e97df55dbbee13c1a7fe5b|
|PG9976-plain-core-fixed-static-v1|実1のraw保持、PMD1/CS0/processing0、抑制追加0|f47eec5e91e68323593fc2cfce79cbacda71323a4738d441b01b1006042d04b9|
|PG9978-plain-core-quality-post-v1|実0、全Main1843同byte/旧Test1919同byte＋新1、当sourceとstatic hash一致|de9e91e5529a130892b3ec76b23cdc9e677ca08be6ef11c56490562552b97fc0|

旧9958/9960/9962/9964は旧source証跡として別保存。新Test SHA bff3bdd906735fc3b2b49d52f7a00ac7f1dad8a2ae515535eee09cb2660b42a1、現在Java1798/Main965/Test833。WBS集約traceは直前1795/1797測定のままで新Test登録を次回追記する（当source登録済みとしない）。各TestのRD/UI/SS/TestIDは2012/当classへ明示。

## Coverage・静的適用性

PG9972-PLAIN-QUERY-CORE、一execのみ、UserQueryRequest CRC f28d7f65ed5a0732、NoMatch0・全一physical class。LINE54covered/8miss（87.10%）、METHOD12/1（92.31%）、CLASS1/0（100%）、BRANCH16/2（88.89%）。全四100ではない。query通常dispatch/後続nonnull境界は未実行、DB/Graph9等へ拡張しない。validateResponse methodはL15/M1/B4各miss0、method CLASS0/0は非適用で100へ変換しない。旧exec/他source/nativeの合成0。

PG9976のPMD CloseResource一件（67行）は借用canonical.fields().get(index)で、外側try-with CanonicalRequestが全fieldをcloseする。9978で当source/line/親所有codeを確認、個別非該当、raw1は保持。鍵/close寿命試験ではなく通常plain値の所有契約、after-close/競合/provider/鍵物体を使用しない。Main byte不変なので旧SpotBugs等を新全体解析0と偽装しない。whole F03/451は未受入。

## 環境・保全・費用

Linux amd64 7.0.0-38-generic、JDK25.0.4+7-1-26.04-Ubuntu、Maven3.9.12、JUnit5.13.4/Platform1.13.4、JaCoCo0.8.15/ASM9.10.1、PMD7.28.0/Checkstyle14.3.0。PG9972安全stdoutにOS/JDK実測、他版/依存と実commandはmanifest hashへ束縛。host試験・新規専用出力のみ、DB/JMS/HTTP/Root/VM/鍵/私有raw/旧job/権限/配備操作0。

開始22→fresh23 used（同reset1793513544）共有丸め+1pp、PGPT専有費/実token/配賦工数は不明nullであって0ではない。開始見積1/3/8 cap10は維持、fixture手戻り/工具修正を追加品質実績と分離。usage cursor01567fb0/N-T null。元leaf新規受入0、追加独立Test ID四が当sourceで実証された成果。保留witness二fileは未読取/未実行/未push、全HOLD保持。
