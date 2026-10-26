# 2095 Query命名・順序定数是正と残三十四文脈再束縛結果

2026-10-26、2094仕様、BUG1852/1853、YKT1603/1604。source370fd74f6f170a18bc1bf959aa9fceced0def15a、Main21d不変更。UserのSYSTEM_ERROR_RESULTをIDEMPOTENT_RESULTへ宣言込み八identifier同値rename（0200不変）、Logのcommit ordinal1三/2一/3一を三Test-local定数で明示した。上位/外部仕様/独立expected値/元処理/条件の意味は変えていない。

|公開manifest|SHA-256|真正結果|
|---|---|---|
|PG10628-query-semantic-constant-plan-v1|e8a26780228c4ac1f7cb9e845ad1795087a66730a5cd61ac04fc9edf6b0cdeb0|0、六metadata反例・元全他token保持|
|PG10630-query-semantic-constant-static-v1|1c3a44d5d4cd9f42b5370c070565fd1a7438821bad75c1b57aac368b7fa0003c|1、元39→34・条件literal五消滅/CS0/処理0|
|PG10632-query-semantic-constant-compile-v1|8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87|0、六正常compile/package・PT0|
|PG10634-query-semantic-constant-post-v1|3458722df1737ddad4350e9a1206dc2dcd6c721d4c328792cc08bbd92e68989e|0、独立逆展開・Main1843/他Test1959 byte不変・当二SourceFileの三physical変更|
|PG10636-query-semantic-constant-trace-v1|5ac9c551e2169648ca247b6ef305f6f56c10759a13e71dd6c945668cb0af74bf|0、二最終SHAのみ・他981行全field保持|
|PG10638-query-semantic-constant-trace-post-v1|9602407b5a9b8a6b64d07cfb314e638c2d21c503ae9f05acac7f077bb6fc7997|0、八metadata反例・原941/943/予算/受入/未知二保持|

manifestは本018_NK-OPS-001の `evidence/provisional/<上記名>/manifest.json`。command/環境/OS/JDK25.0.4/Maven3.9.12/既固定PMD7.28.0/CS14.3・source/input/hash/真正exitは各manifest/正常begin/terminalに保存。全Test physical1962維持。Mainの静的型baseline c919/10558を勝手にcurrent PTへ変換せず、当六正常compileと全Main byte不変を別確認した。

残34は元10622/10624のsource958の判断をそのまま新sourceの成功として扱わず、当sourceのraw指摘34の順序/行位置以外全fieldと元判断を一意対応させ、二sourceの逆展開が元tokenと一致・残二Testと補助二fixtureのhash不変を確認した。10634のcurrent-contexts.jsonに元metadata ID/元source・current source/hash/当finding/理由/非動的資格を保存した。sourceOnlyの限定継続性であり、runtime移植ではない。

当明示四TestのPMD50は、実是正16件（duplicate十一＋ordinal五）、具体文脈非該当34件、未分類0・当範囲の未解消適用指摘0。ただしraw actual1/34を0へ塗り替えず抑制0、全F03/全451は未受入。別発見の0200誤命名一も是正済み。元DB/JMS/key/fault/graph TestはNOT_EXECUTED_HOLD、coverage null、executor停止livenessも未実証のまま。新実PT/個別受入0・正式1964-53/17-190/工数null/QA051final不変。

このPG群は前置check戻値を明示分岐、非0で本体を発行せず、工具新規失敗0。原1854の失敗を正常化せず、既修正は別限定scopeで管理する。開始1/3/7cap10/共有used11→11/reset1793599188、丸め差0≠専有費0、N/T/実配賦null。usage0a8f76514aed549668a326e37540d00be2c25c15729eae4f98fc092acdbf2e0e。

次は公開保存pushと各限定状態追補後、未完WBS・後続index/現sourceからDB/鍵/Rootに依存しない通常PG/PTの具体対象を選定する。旧common44/八pure query/十Trace等の再確認だけの実行はしない。必要な変更後のPTは実施し、元保留操作を別fixtureで迂回しない。通常小受入/commit/報告で停止しない。
