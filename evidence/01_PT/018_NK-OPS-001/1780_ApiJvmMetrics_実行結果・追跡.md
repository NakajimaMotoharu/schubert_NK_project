# API non-resource standard JVM 実行結果・追跡

NK-OPS-001/RD171/UI252/SS311351/411/451、1779/PG-D605/group2006。候補source **fe91dc6898c2f5b679c8fe14c70a490bed770c73**（未配備）、API標準四binder（ClassLoader/Memory/Thread/Uptime、それぞれ複数metric）の限定品質閉鎖。固定service=API、借用registryへ登録するpure wiringで、GC listener/CPU/FD/標準text/実endpoint/ownerは別未完。

|元証拠|真正結果|公開manifest SHA256|
|---|---|---|
|PG8474-api-jvm-six-compile-v1|初稿a92ecのtestCompile warning/-Werror、exit1、PT0 UNRUN|8da752f99d57d9ad1d749c8b0b1189e97c196d098983d8e60884035cd1d3745d|
|PG8475-api-jvm-preflight-v1|元失敗保全＋新Main PMD literal4一件、診断のみ/未資格|dc7e0f84e96817d7f37daa7c08df11e61045bfe8b437607b5fa54e6cb63801d1|
|PG8482-api-jvm-fixed-six-compile-v1|960756正常six/NullAway/Spotless、PT0 UNRUN|7dba64895e7ecb4e3bf244818fd2d2f7de2c5140edb1c1f719505fca7e6b6ae6|
|PG8484-api-jvm-host-v1|960756の14中12成功/F2、誤型fixture、成功化しない|13cc4d1aebca90aca8e3b994b90369d00e3a029f86ccbf93a533d6867f36d435|
|PG8492-api-jvm-oracle-fixed-six-compile-v1|fe91dc正常six/NullAway/format、PT0 UNRUN|b6c9978bf0c71e1b76314c81557ffe7113911c27ed172e01c7eaf66ad52ac884|
|PG8493-api-jvm-sdk-type-proof-v1|固定SDKの公開bytecode名/type/MS、metadataだけ/app実行0|692661761d930f6aa6a3a44ca5bb0ae6b2ceec5222e2a1c78b911b2307ea6d50|
|PG8494-api-jvm-oracle-fixed-host-v1|当source新14/1全成功/F-E-S0、一exec/session|aaabb5abc69157fcccb592a663609435009b4b1a53c5fd5024cc7b28dae20d1a|
|PG8496-api-jvm-post-v1|実新Main1四100、L18/M4/C1/B11 missed0/CRC0/session1/全static0/七反例|18d5c758086ebcf5727db17b7b99c8c01a3f93384b6c5a2d33f09bd380cedf08|
|PG8498-api-jvm-six-trace-v1|全1812physical/181owner、新1/旧1811debug同byte/原1669同byte/五edge0/三role・四field反例|292710c7d4dd584c5efe6fb118445cfadf82d3b1a742795536b3b97f35fd91f0|

pathは本folderの `evidence/provisional/<PG名>/manifest.json`。元command/環境/OS-JDK/時刻/branch/source/archive/input/XML/exec/CRC/session/static/元log/hashを結合。own session20643（失敗1）/98031（診断回収）/70838/95244（F2/exit1）/66942/66436/80867/78619/47882は全真正終端/回収済み、own稼働jobなし/二重発行0。未発行8476/8478/8480/8486/8488はUNRUNで加算なし。

## 独立14と標準SDK観測

固定core1.17.1 SHA9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56。公開SDKの四MeterBinderだけを固定API tagで構成し、自身の新host JVMのstandard sourceだけを観測。literal名/型/tag、固定process startは独立RuntimeMXBean、uptimeは独立前後ms範囲、動的class/memory/threadは存在・非負のSDK境界を検証。動的実測をIT/ST性能値/運用gateの合格へ流用しない。factory順1-2-3-4/一回/借用・STD未読・null/未知mode/closed・list null/要素null/count不一致・入力listを最初のbindでclearしてもcopyされた四portを完走・元Runtime/Error/partial registry caller所有・二owner/有限64並行を独立port記録で確認。

Main classはcompile-time BINDER_COUNT=4だけ、instance fields0を物理descriptorで照合（定数のcoverage除外設定なし）。source/handle保持・registry close・GC listener/他process/VM/Root/DB/鍵/Backup/permission/network/service操作0。旧全Main/Unit/API以外のrole/六POM/SS不変更、旧14や旧source coverageの合算0。標準FunctionCounterはcustom NK scalar Counterとは異なり、後続標準text接続でも型/命名を独立確認する必要がある。

## BUG1704/1705・YKT1455/1456限定close

BUG1704: 修正前起票→8475で元warning/PT0とliteral4診断を保全→9607562237e7f827c8ff07f3b8299307cc3f3ddfで途中close fixtureは明示finally所有、四binder invariantをnamed constantへ。各関連fixtureのTWR外所有/他新Mainの既静的・同byte非該当根拠を915/916へ。新normal全warning0/当Main全raw static0/新14・field/byte-ownerへ結合、解析抑制/期待値変更なし。

BUG1705: 元8484のF2を保持→公開SDK ClassLoaderMetricsと固定Micrometer conventionのbytecodeがcurrentClassCountConvention→jvm.classes.loaded→Gauge、loadedConvention→jvm.classes.loaded.count→FunctionCounter、unloadedConvention→jvm.classes.unloaded→FunctionCounterと示すことを8493で独立確定。fixtureのみfe91dc689で是正、Production Mainは960と同byte。Memory used/Thread states Gauge、Uptime二TimeGauge/msも型と新実ownJVM試験を結合し、上位/コード都合でoracleを変えない。各全対象/非該当/元失敗/修正commit/新14/四100/static/全physical-ownerを結合し、両BUG/YKTは当限定CLOSED、完了日2026-10-24。formal/actualHOLD維持。

開始fresh31残69/1-3-6pp/cap10→終了fresh32残68/reset1793382075。同窓共有差1ppは専有費/tokenでない。usagec7813916/17:57:33JST 明示0/完全性未証明、N/T/専有費/工数null、原-v4-v5/旧窓欠測不変更。1759以降新技術208Test/Main11は異sourceでcoverage/正式runへ合算0。formal1964/53/原190新受入0/QA051final/PTALT0/whole451/CHR/F03Root11/actual VM-Root-DB-native-Backup-鍵-intent-permit-配備/拒否未特定HOLD維持。次公開scan/保存/push後、他roleの標準JVM wiringや独立に実施可能な残監視依存を一群ずつ限定してPG/PT継続する。

