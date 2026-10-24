# API GC owner-before-activation 実行結果・追跡

NK-OPS-001/RD171/UI252/SS311351/411451、1785/PG-D607/group2012、主WBS-P018-09/C07参照0加算。修正source **20075e7f66c3ba8fcf9c52139e77de646abbc7c2**（未配備）。public既存core1.17.1を使用、POM/全旧Main/Unit/上位資料不変更、新Main1/新Unit1のみ。

|元証拠（本folder evidence/provisional配下）|真正結果|manifest SHA256|
|---|---|---|
|PG8524-api-gc-six-compile-v1|旧source7c6正常six/compileのみPT0 UNRUN|3b8391d5a7a6a11cea8fb3e6a5e9e3cc815bea720c7bf85f025162d6053fbbc1|
|PG8526-api-gc-host-v1|旧14/1成功、新source資格へ転用0|274a4517544977abb67212dd0294dd6c951aa141343d4af42003e2e64959680b|
|PG8529-api-gc-static-stop-v1|旧8528 PMD CloseResource一件/exit4・post1、CS/SB未実行を保全|f08e9bd1091bde226c77ca8c6f3445c4a88f3f0542d5ff3ff69bc0250e22ac3b|
|PG8534-api-gc-owned-six-compile-v1|新source正常six/NullAway/format、exit0、PT0 UNRUN|889dff45e9791631d80c81431741a1d8134fbaa7d41b1a74813bb3d2954d8d19|
|PG8536-api-gc-owned-host-v1|新APIGC001～014の14/1、F/E/S0、一exec|989bc7adc9ddb94fddb773986e9426e161fc1c365ef5af55f1596ee983c18a50|
|PG8538-api-gc-owned-post-v1|実1四100/CRC0/session1/PMD-CS-SB-missing0/七metadata反例|81bcbb71e93028f15e1c0d518c26eca8df37c317b70b9550939fcea948cd833a|
|PG8540-api-gc-owned-six-trace-v1|全1815/187owner・新1/旧1814debug同byte/原1669同byte/五edge0/三role・三field反例/SDK metadata|a50ecec93317318380b9ab6c992ba978d0cc86019563f2ee06405f49d5025150|

元command/環境/OS-JDK/branch/source/時刻/exit/archive/全input/deps/tool/実JUnitXML/exec/logのhashは各manifestに結合、再PTやsynthetic PASS生成なし。own54709/31264/28910/74226/27645/29199/54144は全真正終端回収済み。旧8530/8532予定は未発行UNRUN。全coverageは **LINE18/18、METHOD5/5、CLASS1/1、BRANCH9/9**、除外追加/別exec・別source counter合算0。

BUG1706/YKT1457：元local resourceを、生成後即activateOwnedのborrowed parameterへ明示移譲するsource20075e7f6で是正。ownerの保持true→bind順、retain後false/throw・bind Runtime/Error時同handle保持、helperの暗黙close/retry0を新14で検証。SDK型/動作変更やSuppressWarnings/静的除外/期待値変更0。横展開はcandidateの直return、既API/Web/Batch四non-resource binder（AutoCloseableでない、元source同byte）を非該当根拠とし、新GC owner/factory/activation各境界は新14と実Main四100/全raw静的0へ結合。検索だけcloseせず、当限定BUG/YKT CLOSED/完了2026-10-24。

固定SDK SHA9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56の公開javapを8540で保存・hash固定、constructorは自己JMX metadataだけ/listener登録なし、bindToはNotificationEmitter.addNotificationListener/cleanup登録、close経路は同listener解除。metadata readerはSDKを初期化しない。実default SDK一件はown fresh JUnit内で生成・owner保持後bindし、そのownerが借用registryより先にclose。強制GC/外部process/VM/旧handle/DB/鍵/Backup/Root/service/network操作0。残る実runtime assembly/実停止/GC event stream/standard text/endpoint/whole451は未受入。

工具手戻り：初回8524 wrapperはpyflakes import環境欠落でjob発行前終了、PYTHONPATH修正のみ。8529 preservation wrapper初回は誤写pinを拒否して出力前終了、元hash照合で修正し製品再試験0。製品障害の再試行とは分離、原失敗成功化0。

開始fresh34残66/2-4-8pp/cap10→終了fresh35残65/reset1793382075、同窓共有差1ppはPGPT専有費やtoken数ではない。usage006e87ee/19:09:01JST、明示0/完全性未証明・N/T/専有費/工数null。1759以降新技術256Test/Main14は異sourceの技術値で正式やcoverageへ合算0。formal1964-53/原190新受入0/QA051final/PTALT0/whole451/CHR/F03Root11/全actualHOLD/元-v4-v5/欠測保持。

次はWeb/Batch role固有の同GC owner-before-bindを各既mode診断/固定WEB-BATCHで新PG/PTへ。新群開始値を固定し、API14の確認再演なし。通常小区切りで停止しない。
