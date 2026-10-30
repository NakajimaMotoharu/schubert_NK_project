# 2819 Batch meter四whole38仕様

P01809/source6b53/normal14216、着手見積2/5/8pp/cap8。原四whole38全Test1361行・Main318行と必要enum/fixtureの全body/initializerを確認、NORMAL_PT。own SDK registry/有限pool・固定Tag/Count/Instantだけ、実Batch/DB/Root/VM/OS/process restart/integrity probe/repair/retirement/鍵/network0。既1171からcase/suite/完全Source非重複を事前照合した。

|原suite/TestID|件数|独立oracle・正常/境界/null/異常/並行/例外|
|---|---:|---|
|BatchMetricLabelPolicyTest/BATCHLABEL001～014|14|固定6family/types/key、40runs/10success/4transfer/30integrity/24restart全tuple、未知/欠落/追加/重複/null/immutable detached copy/provider読取各一回・失敗同一性/並行64|
|BatchMetricRecorderTest/BATCHREC001～008|8|50series=40counter+10gauge、固定40tuple/10.25と11.5/max保持・非success非更新、UTC0001/9999・micro精度/invalid副作用0/NaN≠0/borrowed registry/partial失敗再送0・並行64|
|IntegrityFailureMetricRecorderTest/INTEGRITYMET001～008|8|固定30tuple、4×30+1=121増分、AreaとBatchStep全enum/factory/null/未知、STANDARD0・DEBUG30、失敗前後0/1・補償再送0/partial prefix/64事前入力集計/foreign gauge所有|
|ProcessRestartMetricRecorderTest/RESTARTMET001～008|8|固定24tuple、4×24+1=97増分、Reason4/service6全domain、null/未知/STANDARD/DEBUG/partial登録/失敗前後/独立64入力集計/foreign gauge所有|

Exception fixtureのgetMessage/toStringはAssertionErrorだが製品は文字列化/graph探索せず同じobjectを伝播。OOME一個はsynthetic-test-only-no-allocationの通常objectで実OOM/負荷/制御0。SimpleMeterRegistryのみ・外部export0、pool/registryはfinally/try-with-resources、JVM180秒。BatchMetricContractTestは既読のSTEPS/STATUSES定数のcompile-only依存、今回suiteには選択せず旧method再演0。

四Main完全Source六Code：LabelPolicy1、Recorder1、Integrity+Area2、Restart+Reason2。全class/Jar/Source pin、同一new exec/session/CRC、非空四counterとB0 N/Aを測定して保存。公式generated filter不変更/manual除外0、全手書きlogicを対象、別run counter合算0。SS351/RD171/UI252の閉domainと独立literalから期待値を作成、製品値からexpected生成0。起動前後input固定、JDK25.0.4/JUnit/JaCoCo0.8.15/fresh javac proc:none/Werror、checked entry pg15000_batch_meter_contracts_thirty_eight_pt.py。元ENV/時刻/command/exit/fixture/結果/全counter・反例・ownerは2820と各manifestへ。旧全証拠/原本/Currentbaseline/stash7/二held、正式1964/53/17-190/工数null/QA051final/全HOLD保持。
