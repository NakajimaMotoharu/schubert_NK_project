# Web/Batch GC owner-before-bind 実行結果・追跡

1787/PG-D608/group2014、NK-OPS-001/RD171/UI252/SS311351/411451。Production source **623be8eeaf078f85cfa5682dced7a3b2e21a2b49**（未配備）、新2Main/Unit2、他全source/POM/上位不変更。実装は既Web/Batch mode診断を保持し、固定WEB/BATCH・fresh候補owner保持true後だけbind・helper暗黙close/retryなし。API14/原4222確認再演なし。

|元証拠（evidence/provisional配下のmanifest.json）|真正結果|SHA256|
|---|---|---|
|PG8546-web-batch-gc-six-compile-v1|正常six/NullAway/format・exit0、PT0 UNRUN|cac5a32fa54aad3854c3f843a2289fd04ec26a70765c4da45a36ebe31b2fd8cb|
|PG8549-web-batch-gc-selection-stop-v1|旧8548 foreign選択/selected exit1/found0、28 UNRUN保全|59da5fda0e9993e9fb327bbf46401bdc1c8deb148344d325dceadf30e7b154da|
|PG8555-web-batch-gc-selection-preflight-v1|正規二FQCNとfixture一致/foreign-missing-duplicate三metadata反例、製品PT0|6c67990114939d1e74295691260cc1a6b76a611dc9a3bf328308d97207040a90|
|PG8556-web-batch-gc-fixed-host-v1|新WEBGC/BATCHGC各14、28/2 F-E-S0・一exec|2c7aa21cdb9dc434e6b03d3a61f590d6364dd678e77b376e6542e88232a8f174|
|PG8558-web-batch-gc-post-v1|実2四100/CRC0/session1/PMD-CS-SB-missing0/七metadata反例|9e813bf3fd2a25fa86463e8bbea2a33022113b1e21a90d676c00cf0bf031f2f3|
|PG8560-web-batch-gc-six-trace-v1|全1817/191owner、新2/旧1815debug同byte/原1669同byte/五edge0/六role-六field反例/同SDK|a7d6b0c8a178b61139a9862c63d671f70be0db93f8d0823781740ded4db25b45|

元command/環境/OS-JDK/時刻/branch/source/全input・deps・tool/XML/exec/log hashは各manifestに固定。正常sourceは工具修正8b6d2fbab後も全src/POM同byteで再build0。実coverage **LINE30/30、METHOD10/10、CLASS2/2、BRANCH12/12**、除外/別source・別exec union0。own96521/38845/78014/76350/31679は全真正終端回収、旧予定8550/8552/8554は未発行UNRUN。

BUG1707/YKT1458は起票後8549で旧launcher本文/全元begin-command-exit/XML/execを保存。旧選択APIのfound0/containerFailed1をPASSにしない。修正8b6d2fbabは二class選択と実fixtureの起動前照合/三metadata反例を追加、新28・同Main四100/全raw静的0/全byte-ownerへ結合して工具範囲CLOSED、完了2026-10-24。API GC launcherは正規API選択・元14/同byte、既WebBatch JVMは正規二選択・元28/同byteで非該当、確認再演なし。Production/期待/上位変更0、検索だけclose0。群開始append CLI初稿は構文誤りで書込前終了、2014一件のみを固定し工具費に分類。

SDK GC metadataは8540原a50ecec9と同core SHA9ca47dfaを照合して再読取0。constructorはnotification未登録、owner ack後bindToだけ登録、callerが同handleでclose。real各001はown fresh JUnitだけ、他は公開SDK subclass記録port、GC強制/外部旧handle/実VM/Root/DB/Backup/鍵/network/service操作0。API/他roleのpartial sourceを横取り/closeせず、同installerの二scope/64独立並行とfalse/例外でもactivation0を確認。

開始35残65/2-4-8pp/cap10→観測36残64/reset1793382075、共有差1はPGPT専有費でない。usagef34ec0b9/19:18:21JST/明示0/完全性未証明・N/T/工数null、元-v4-v5/欠測保持。1759以降新技術284Test/Main16は異sourceの技術値のみ。formal1964-53/原190新受入0/QA051final/PTALT0/whole451/CHR/F03Root11/全actualHOLD不変更。

実runtime assembly/owned停止/GC event stream/standardtext/endpointは未受入。次はSS351標準process/host metricの必要依存を現SDK/current sourceで限定照合し、安全なrole内Processor/FileDescriptor binding等のPG/PTへ。単なる分類/報告/commitで停止しない。
