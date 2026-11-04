# NK-MSG-001 eventport 単体テスト結果

003/649650、Main Source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、Test source11044560bc478ae6fe7dfeaa6afbcb4fc7881f45/dev-foundation。Test sourceを固定してPG18586を一回実行し8b1581 actual0。四method/一Test class・七vector、failure/error/skipped/aborted0。元broker/Readiness試験は再実行していない。

|Test ID|結果|確認|
|---|---|---|
|PT-JMS-PORT001|PASS/2vector|count1/4の公開合成metadataでも元eventをSAMへ一回|
|PT-JMS-PORT002|PASS|fixtureをassert前に構築、null eventでNPE/delegate0|
|PT-JMS-PORT003|PASS|null deliveryでNPE/delegate0|
|PT-JMS-PORT004|PASS/3vector|未知Runtime/NPE/Error同一性・callback各一回・再試行なし|

PG18580原compile0・未実行を保持。BUG2255/YKT2000のassert対象へfixture生成が混在する問題を651へ先行起票/全文保全してから修正、PG18582/58334/b5f318はcompile/PMD/Checkstyle全exit0・指摘0。今回新規四Test source全16@Testの範囲を確認し、他三FixtureTransactionTestはconnection生成がassert外、beginTransaction(null)自体はSUTという非該当根拠を記録した。

PG18586のactual commandはmanifest begin.command、固定標準JUnit Console1.13.4の四explicit selector/--fail-if-no-tests/自動extension・並列false、JDK25.0.4、JaCoCo0.8.15。API/protocol normal14216二Jar＋新Testclassのみで、SDK/Root/broker/DB/VMを起動しない。class-init実測はAPIのInternalEventProcessor/DeliveryMetadata二classと必要なprotocol六classだけ、他業務module0。

Source全physical一interface、実行Codeはdefault一method。単一session PG18586-InternalEventPort、実execと独立classinfoのCRC77e2bf41e8c1025d一致、3/3probe。line4/method1/class1全miss0、branch0/0はSource内条件命令が無い自然N/A。abstract SAMはCodeなし、手動除外0、private constructor/getter埋め0、旧exec合算0。DeliveryMetadataは入力に使うが既PG14244の実績を増加/再実行していない。

独立post652/1a82eeは全四ID・Git/Test/Main/Jar byte・単一CRC/session・Source全counter・API初期化閉包を確認。原post048229のcase schema誤認はBUG2256/YKT2001/653へ保存後、既3008case objectと新4/既12selector stringを区別して修正。全schema件数/重複/同名異classと八metadata反例を確認、製品試験再演0。

既Current集計3008/451/650Sourceに今回のclass/caseは存在しない。新四PT/一Source全適用counterの証拠をsidecarとして保存し、旧18474原OS終端未回収/aggregate登録・G13依存は保持。未検証のregistryへ算術追加せず、正式1964/53・個別WBS受入0・工数nullを維持する。既2980参照不足のbroker methodを消化済みへ変換しない。代表Vの成功/費用較正へ差替え0。

環境・input publicsynthetic model・OS/JDK/branch/Testsource・実command/start/end/exit・XML/coverage hashはmanifestへ収録。raw XMLはown host slotに保持、Gitは実case class/name/timeだけへ正規化し不要properties/streamsを省く。これは実broker再送/業務payload/Question delivery-aware override/所有・全451/CHR合格の証明ではない。
