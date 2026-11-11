# JMS二guard provider故障分類の通常PT

Program NK-MSG-001／NK-WEB-001。対象 `JmsMessageGuard.read`／`JmsReplyDecoder.decode` と純UUID/Layout検査。RD MQ-003/004/005/008/040..045、UI231/232、SS321§7/8・SS322§5・SSC332、411§5・451。BUG-2659／YKT-2339。上位仕様の変更は行わない。

| Test ID | 全class／method | 入力・操作 | 独立した期待値・根拠 |
|---|---|---|---|
| PT-JMS-PROVIDER-WEB-001 | Web JmsReplyDecoderTest.providerFailuresRetainExactIdentityAndEarlierValidationStopsLaterReads | 正常の手組み280byte LOGRSP01 fixtureに対し、16 getter/property位置×IAE/NPE/AssertionError/JMSExceptionをProxyから送出 | 返却値が存在しないprovider故障はwire不正の根拠にならない。元型・同一instanceを伝播する。SS321/SSC332・411§5。expectedはproductionを呼んで生成しない。 |
| PT-JMS-PROVIDER-API-001 | API JmsMessageGuardTest.providerFailuresRetainExactIdentityAndEarlierValidationStopsLaterReads | literal3byte bodyとSS321の明示JMS metadataに同じ16×4を注入 | 同じく元instance。業務処理・DB・broker ACKは実行しない。 |
| 上記各IDの早期検査2入力 | 同method | correlation=`bad`／layout=`bad`、後続getterにはAssertionError | 後続getterに達さずPPE、既存の固定診断文字列、cause IAE。取得/検査の順序を変えない。 |
| PT-JMS-005/006原7+7 | 両Test全method | null/type/body長/clone/宛先/ReplyTo/欠落/blank/不正UUID/canonical alias/負expiry/不正layout/wire差 | 原fixture・原assertを保持。API DTOとWeb DTOのnull拒否・防御copy・redactionも全classで実行。 |
| JMSCLIENT原8+追加2／Registry7 | JmsRequestReplyClientTest／ReplyCorrelationRegistryTest全class | 同sourceの経路に必要な所有・timeout・再利用・並行・未知例外 | 別sourceの旧execを合算せず、同一sessionのactual結果だけを記録する。 |
| Protocol130 | 既存全27fixture・28source | 共通codec／64layout／NFC／strict UTF-16、独立golden vector | 原130は真正PG26304 compileとPG26310/26312資格に結合。今回は変更されたguardが参照する閉包の100%検証のため同runへ含め、確認目的の別全回帰を発行しない。 |

新JUnit定義は2、matrixは各64provider入力＋早期2入力、合計132入力を予定。既存161件と合わせ163件の必要接続試験。初回redはPG26476で新2だけ旧Mainに実行、真正終了1・2fail。各methodは最初のmetadata IAEで停止したため未到達matrixを実行済みに数えない。

Null/欠落/空/未知は原14およびprovider負入力で確認する。NPEを正常化せず元NPEを保持する。JMS API ProxyとArtemis宛先の値オブジェクトだけを使用し、factory/broker接続・embedded server・VM・DB・原本FS・鍵・Root・held四classを許可閉包へ含めない。借用messageをcommit/rollback/closeする責務は持たない。

Mainはsrc配下の2classだけを変更。現sourceの9Main＋package-info二つの限定Maven構成を公開sourceから厳密copyし、root同一compiler設定Java25/ErrorProne2.50.0/NullAway0.14.1/JSpecify1.0.1でcompile。成功Mainを再buildせず、fixture命名の修正時はTestだけをfresh compileする。subset buildを六module正式buildと混同しない。PMD/Checkstyle・SpotBugsは対象と適用性を記録し、抑制・coverage手動除外を行わない。

予定実行: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1250_jms_provider_final_qualifier.py run <固定commit>`。入力hash・環境・実command・開始/終了・exit・JUnit実名・当class CRC・四coverageをPG26506→PG26508のmanifestへ保存する。全188physical入力（Protocol176＋限定12）の自然code0も入力に保持し、line/method/class/branchの未網羅を隠さない。

作成時点: green未実行、coverage未確定。F02/F03・実broker/native・全451・元190正式受入は未完。実行結果・対象commit・証跡hash・BUG/YKT閉鎖は真正終端と独立postの後で追記する。
