# User照会oracle分岐独立化・限定検証結果

2026-10-26、2003/2004、群2262/G13.07/.5-2-5cap10。現在Main-Test source4c94a7d4665e4f3c27a7d39fb2b427bec663d903、Production Main最終変更21d7c3042。**STATIC_ORACLE_AND_APPLICABILITY_REVIEW_COMPLETE_DYNAMIC_UNEXECUTED**。既ADM040..043と外部ADM048のoracle補助を是正し、既4＋7 method宣言は保持、新Test/実行PT件数0。正式1964PT/53scope・17/190・工数nullは不変。

## 修正と必要検証

- BUG1777：expected layout/name/typeをSUT detailRequestで選ぶ三箇所を廃止。USR/UDT input fixtureからexplicit expectedLayoutを渡し、detailRequestは独立expected boolに対するactualとしてのみ残す。元LP/HMAC/値/NULL/所有buffer/assertionは保持。
- BUG1778：外部共有caller一件の新引数更新漏れによる元569f/PG9900 compile1を保持。5f18で全五callerを一致させ、PG9904は全六compile0/PT0、PG9906はMain1843全byte同一・Test1918中変更3・七source反例/五callerを確認。外部callerの期待値も入力detail bool由来で、旧三引数互換helperは追加していない。
- BUG1779：二Testのwildcard20/複数宣言1を是正し、重複literal10/fixture ordinal5比較をTest内独立固定値へ集約（Production constant参照0）。4c94/PG9908は六compile/package0/PT0、PG9910はCS0・PMD raw15/processing0/真正exit1。元9902のPMD30/CS21/exit1は原証拠のまま残す。
- PG9912は全Main1843同byte、原source入力集合不変・変更Test二pathのみ、Test内13固定値の独立literal宣言・五caller・期待field/type/NULL frameを確認。元5f18と当4c94の両Test本体は、Test内定数を独立literalへ展開しformatterの隣接String結合/宣言分離を正規化したcore tokenが一致。九source metadata負例（元七＋誤literal二）と十literal metadata vectorを保存。metadata検査件数は製品PTへ加算しない。

## 静的指摘の個別適用性

PG9912/pmd-applicability.jsonは15行すべてのpath/source hash/line/rule/根拠を保持する。NULL faultリセット5は試験内の注入解除、catch Exception1はchecked Exception宣言のfixture setupをRunnable内でAssertionErrorへ翻訳、DoNotUseThreads6は非J2EEの自己所有host PT。CloseResource2はtry-with CanonicalRequestの借用fieldと、外側try-with receiverの借用JMSContext proxy。UseProperClassLoader1はinterface型同一性を保つTest proxyのdeclaring loaderで、managed J2EE実装ではない。各具体sourceと所有scopeを確認し、適用違反0と判定した。raw15/exit1を0へ書き換えず、抑制/全Test除外は追加0。資源の実終了や並行成功をこのレビューで実証したとはしない。全F03/451の認定は別残件。

## エビデンス

すべて018_NK-OPS-001/evidence/provisional/以下。実command/OS/JDK/branch/source/exit/各input・tool hashはmanifestのbegin/stages/invocationへ結合。

|run|真正結果/用途|manifest SHA-256|
|---|---|---|
|PG9900-user-query-oracle-six-compile-v1|569f、compile1/PT0・元更新漏れ|bae93b8a78229288a39519fb9e12a742e0aaa4dc665146faeb9518aee90ea65d|
|PG9904-user-query-oracle-six-compile-v1|5f18、六compile0/PT0|767ce10623ceee20a145331f0abe9f7d4cb6faf1cad10bcbb167532e140c0c13|
|PG9906-user-query-oracle-source-post-v1|5f18、source/byte/七metadata反例0|bc7bda23c8fdebb1189fea7d6bbec656a30223294d2b00891461fd89baf34b03|
|PG9902-user-query-oracle-static-v1|5f18、PMD30/CS21・raw1|b6d4894c6463853bf0954dd6722fd2556535d4a0d1be767fbd498e471ae666c1|
|PG9908-user-query-fixture-six-compile-v1|4c94、六compile0/PT0|82fa21a02cbd438e29d63a5260e206d71bf7c9df864448146866af5d73c91e34|
|PG9910-user-query-fixture-static-v1|4c94、PMD15/CS0・raw1|f4f99f2e1e6214b5b9854677992456670741b9d1c7fced71eb8da6e58363174a|
|PG9912-user-query-fixture-post-v1|4c94、独立source/同byte/15適用性レビュー0、動的0|4cc044a2095170ba4ff1484165180328ba1dc2c6e506d066cbefa61c6e656d04|

自己normal77224/49070/41641はそれぞれ元1/0/0、静的69640/74171はraw1/1、すべて終端回収済み。外部job/VM/processの現在所有はUNOBSERVED_HOLD、新しい外部操作0。

BUG1780/YKT1531：元9912はliteral分割の誤差で準備1、工具SHA80bad13476a2ec91af9f88f0ae1a3532ddd5be184ce893539d16268420408ec7、元copyをwork/pgpt-runs/PG379/pg9912-user-query-fixture-post-initial-source.pyへ保全。当bounded普通Java String metadata decoderは隣接literalのみ結合し、escape/octet境界六golden＋unknown/Unicode前処理/未閉鎖/textblock四拒否を確認。実Java/fixtureを評価・実行しない。元9906は長SQL本体比較を持たず、短いframe/signature検査を変更していない。元失敗を成功へ変更せず、工具scope確認済・保存commit待ち。

## 未完・計測・次工程

BUG1777/YKT1528はSTATIC_REPAIRED_DYNAMIC_PENDING（DB付き既PTは未実行）。BUG1778/YKT1529はcompile scope再試験済、BUG1779/YKT1530は当二Testのsource静的scope確認済、全動的/正式品質とは分離。2003で残したADM042の広いRuntimeException assertion候補は未是正。新sourceへ旧nonce9/2/coverageや旧nativeを合算0、Graph9/鍵close/Root/実VM等HOLD不変。

開始used20→終了fresh20/残80/reset1793513544、共有丸め0≠専有費0。usage fa86a4ab33bace041cf4632dc99f7235999bcedc615cf635b9205ee51db04a8a、実N/T/費用配賦/工数null。元見積/v3/v4/v5と旧失敗/成功/cursor保持。次は保存push後、変更二Testの現hash/証拠を既主担当P01001のtraceへ反映する。既1794/1796は旧21d測定で、当二Testのhash刷新前に当source登録数として転記しない。G13全監査HOLD/UNKNOWN二fileを隠さず、通常compile/レビュー/commitだけで停止しない。
