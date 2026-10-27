# 供給PoolCollector・Batch監視九件 製造単体結果

2026-10-28、source14198cb1878ec73319511ba1067133992d335e63/dev-foundation/PG-D739/BUG1968YKT1716。2328の原38/五suite全成功、F/E/S/aborted/container失敗0、新TestID0。九String73参照だけ変更、全元38/helper raw逆42異常。全Main1843同byte、五SourceFile十物理Test差/他1952同byte、単一exec PG12380-POOLBATCH-JPのCRCと全API467/Web358/Batch645を独立確認。normal六module成功PT0は38へ加算しない。

|証拠（evidence/provisional）|終了・SHA256|
|---|---|
|PG12374-pool-batch-plan-v1|0 / e73107802e5b4d7605add4d2255393c02df82bd4d202306c4300e9ba5967e557|
|PG12376-pool-batch-source-post-v1|0/42異常 / adb98e35478e485d103b28109954ef8ae52fe13aacdfd9444b65feba77709739|
|PG12378-pool-batch-six-compile-v1|0/PT0/session97737真正0 / 27e5dafc18e19fb5e29edd96958a5ba2f05da01611aa12b1ca8208735eb52b75|
|PG12380-pool-batch-host-v1|0/38/session15788真正0 / d12e56ad21684f4c31b690880763c69db7744be141228db54119ce0dcf71c12f|
|PG12382-pool-batch-static-v1|gate1/35→26/CS-processing0/session56468真正1 / ef847e28425796fadd1e804a7367c5f4fca93da901c84a8ea544838b0e277d5e|
|PG12384-pool-batch-post-v1|0/session75710真正0 / c89e090a9e054d00206a094b29c0e41694cd87e3433f81211e1ae0048791724d|
|PG12386-pool-batch-context-v1|0/26理由 / f7c2f9ed8356a354b4c93755f783cff32d23c532a62129b7f1fcecf555e86a07|
|PG12388-pool-batch-context-post-v1|0/22異常 / 4add8469630e4c0325a7db3698013a3d0f1af78804526ae688e278d6185b8152|
|PG12390-pool-batch-trace-v1|0 / b2481b73b8a2da895ef7e3eca042a82a8d0ca975bbab0eebd367da90770f63b8|
|PG12392-pool-batch-trace-post-v1|0 / 000041dc9a01c10f2b008f35d191ff2dbaa40513967d4e89358c93af7a7e2495|
|PG12396-current-pool-batch-delta-v1|0 / 0176966841ad4dfad133672b141c860ddae4edfb278b8d61fd72e76875e95d0a|
|PG12398-current-pool-batch-delta-post-v1|0/八異常 / dfb9abd04e22a344696dede1d28f06fbf0bd575d91fce6321a38a15cb01c8c1d|

実command/argv/branch/source/時刻/OS/JDK/input/期待fixture/実case/XML/一exec/CRC/依存SHAは各manifestで結合、各entryは2328のchecked command。toolchainはJDK25.0.4/Maven3.9.12/JUnit5.13.4・Platform1.13.4/JaCoCo0.8.15/PMD7.28 record1298/CS14.3/GJF1.36.1、Enforcer/Spotless/NullAway-JSpecify/-Xlint-Werror維持。TSVの実classpath outputと元resourceのhashも一致。fake support二Testはfixture/helperだけを借用、@Testの再演なし。実DB/JMX/network/file変更/VM/Root/鍵/Graph9呼出0、新工具失敗0。

## Counter結果（covered/missed、旧exec合算無し）

|対象|Line|Method|Class|Branch|
|---|---:|---:|---:|---:|
|API/Web collector本体二|34/0|6/0|2/0|8/0|
|MetricContract/Kind二|47/0|9/0|2/0|6/0|
|TransferMetricRecorder/Counts/Suffix/Usage四|51/0|18/0|4/0|16/0|
|MonitoringModePolicy|28/1|8/0|1/0|13/2|
|MonitoringModePolicy/DetailService・RetentionConfiguration二|8/0|2/0|2/0|4/0|
|API/Web observer各一|各9/0|各2/0|各1/0|各5/3|
|API/Web pool recorder外側各一|各24/3|各7/1|各1/0|各8/5|
|API/Web pool Counts各一|各5/4|各2/0|各1/0|各5/9|
|API/Web pool State各一|各9/0|各3/0|各1/0|各0/0 N/A|
|完全API467（447解析＋20package注釈）|64/12675|17/1825|5/360|22/4800|
|完全Web358（350解析＋8package注釈）|64/9866|17/1795|5/315|22/3582|
|完全Batch645（644解析＋1package注釈）|134/18282|37/3168|9/404|39/8419|

直接八Main=132L33M8C30B miss0だが、全19対象/全artifactは未100。MonitoringModePolicyの欠落service/不一致modeや借用pool Counts等未実行分岐を除外しない。標準JaCoCo enum/record生成code filter・自然0branch=N/A、手動除外や人工到達なし。

## 静的・所有・集合

残26はThread22/CloseResource1/CompareObjectsWithEquals2/EqualsNull1。threadはstandalone自己worker、ローカル期限の有無/TWR又はcatalog finally shutdownNow+await10秒を区別。CloseResourceはその明示終了oracle、identity二はimmutable snapshotが二つの供給原instanceの一方であること、equals(null)はgenerated record契約を意図しており、機械的置換はoracleを削る。26一意ID/元XMLの全属性・別method解析・明示control・原実caseの成功を結合し、row16/manifest6の22異常を拒否。rawを保持し全体適用性判定待ちとする。

原owner/cost全五P01809、changeOwner F03。983行の五SHA以外978同一、logical join五件はreviewed candidateで未受入、全WBS監査前後同HOLD1。現行集合は9409−859是正＋追加8保持=8558（Main1512/Test7046）。理由参照3135=3131−22＋26、当source結合待ち720=694＋26、未参照5423。原九ID以外消去0/追加8保持、全静的再発行測定値ではなくsource差分集合。

正式1964PT/53scope・17/190・工数null/QA051final/全F03-451・各HOLD/元予測不変更。原群2/5/8pp cap10、共有開始62残38、実専有費/N/Tはnull。完成結合・最終quota/公開scan/保存commit/pushは追補2330又は456へ。通常小群/報告/commit/PMO待ちで停止せず許可済み独立PG/PTを継続する。
