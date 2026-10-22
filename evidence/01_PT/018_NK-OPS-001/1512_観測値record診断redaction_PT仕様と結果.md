# 観測値record診断redaction

NK-OPS-001/SYS002004 OPS009/UI251253/SS352343（broker値はSS321参照）、PG-D513。主P018-03.02、P017-10参照追加0、着手.1/.35/.8pp・共有85/残15/reset1793082864、実費/N/T/工数null。Main正しく不変更、全旧Test/gates固定。

PT_DEFAULT、fixtureはpublic合成文字列/immutable record/Map/Path値だけ。Pathは構築するだけでファイルを開かず、実Root facts inspect/Broker execution/read/native/Unit/DB/JMS/Backup/credential/permit操作0。実サービスの観測済み情報や発行権限のproofにしない。

| Test ID / method | 入力・独立期待・後条件 |
|---|---|
| PT-OPS-OBSDATA-001 / obsdata001FactsRetainPublicInputsButDiagnosticNeverRendersYamlOrBinding | PUBLIC-DATA-A/B、合成Contentsと非重複六Path値・固定digest値。Factsは同config/binding値を保持するが診断はRootServiceFacts[public=＜redacted＞]（ASCII半角）のみ。両null引数拒否。 |
| PT-OPS-OBSDATA-002 / obsdata002BrokerWrapperRetainsImmutablePublicDataButDiagnosticHasNoNestedDetails | 二markerをnested immutable Evidenceへ保持、public Summary(5,c×64)。Observationsは同値を保持するが診断はBrokerObservations[actual=＜redacted＞]のみ。両null引数拒否。 |

expectedは手書き固定literalとconstructorへ渡した同identityから作り、production toString/codecでexpectedを生成しない。値保持と診断非漏えいを両方確認し、空fixtureだけの見かけのredactionとしない。各recordには実conditional branchが無く、実XMLでBRANCH不存在・L/M/C正counterのmiss0を確認する。存在するbranchを除去/無視せず、BRANCHを0/100へ合成しない。auto record生成memberの扱いは既JaCoCo標準のままで新除外設定なし。mutableな処理/transaction/worker/再送/取得資源は無し、実環境の並行/再送条件は別HOLD。

新二method未実行、coverage未測定、関連障害なし。実declaration/選択/元XML/source/hash/終了code/実counterを真正実行後に追記し、loop variantをJUnit件数にしない。旧4213と新selected25を新sourceへ合算せず、正式1964/53/canonical17/工数null/原-v4/全HOLD/PTALT代替0維持。通常小群では停止しない。
