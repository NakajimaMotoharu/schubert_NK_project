# 観測値record診断redaction

NK-OPS-001/SYS002004 OPS009/UI251253/SS352343（broker値はSS321参照）、PG-D513。主P018-03.02、P017-10参照追加0、着手.1/.35/.8pp・共有85/残15/reset1793082864、実費/N/T/工数null。Main正しく不変更、全旧Test/gates固定。

PT_DEFAULT、fixtureはpublic合成文字列/immutable record/Map/Path値だけ。Pathは構築するだけでファイルを開かず、実Root facts inspect/Broker execution/read/native/Unit/DB/JMS/Backup/credential/permit操作0。実サービスの観測済み情報や発行権限のproofにしない。

| Test ID / method | 入力・独立期待・後条件 |
|---|---|
| PT-OPS-OBSDATA-001 / obsdata001FactsRetainPublicInputsButDiagnosticNeverRendersYamlOrBinding | PUBLIC-DATA-A/B、合成Contentsと非重複六Path値・固定digest値。Factsは同config/binding値を保持するが診断はRootServiceFacts[public=＜redacted＞]（ASCII半角）のみ。両null引数拒否。 |
| PT-OPS-OBSDATA-002 / obsdata002BrokerWrapperRetainsImmutablePublicDataButDiagnosticHasNoNestedDetails | 二markerをnested immutable Evidenceへ保持、public Summary(5,c×64)。Observationsは同値を保持するが診断はBrokerObservations[actual=＜redacted＞]のみ。両null引数拒否。 |

expectedは手書き固定literalとconstructorへ渡した同identityから作り、production toString/codecでexpectedを生成しない。値保持と診断非漏えいを両方確認し、空fixtureだけの見かけのredactionとしない。各recordには実conditional branchが無く、実XMLでBRANCH不存在・L/M/C正counterのmiss0を確認する。存在するbranchを除去/無視せず、BRANCHを0/100へ合成しない。auto record生成memberの扱いは既JaCoCo標準のままで新除外設定なし。mutableな処理/transaction/worker/再送/取得資源は無し、実環境の並行/再送条件は別HOLD。

新二method未実行、coverage未測定、関連障害なし。実declaration/選択/元XML/source/hash/終了code/実counterを真正実行後に追記し、loop variantをJUnit件数にしない。旧4213と新selected25を新sourceへ合算せず、正式1964/53/canonical17/工数null/原-v4/全HOLD/PTALT代替0維持。通常小群では停止しない。

## 真正実行・原資格

Source94bc77764565d62985592a7e5b92e9206a2d8f4f、元6916/session30308真正0、09:17:03.191621Z～09:20:03.295675Z（180.104054秒）、archive484608e6c41f9809c150235f24f33bc5239e843257cf3beb569c8dc63c2eef58。実17件9suite=新二method/既純観測port三method/六guard12-7、FESflakyNotRun0・phase000/六SpotBugs0・Source固定。

完全PYTHONPATHで`python3 -B tools/quality/pg6916_observation_values_selected.py run`→同工具read（session75205真正0、追加PT0）。原PG6918-observation-values-original-v1/manifest.json SHA256=32118884012095e87885c0246f083a27193f2d56394842e8459eed4d770145f4、全851/1669 Main差0/raw1409保持/Checkstyle0。6920原target/TestID manifest15dcfea7b0f54810b782ad0c98b1b00914667d4a0e147ea81eb6087fd48115d4で二record各実L5/M2/C1 miss0・BRANCH実不存在を確認しN/A理由を記録、positive四100のclass数へ加点0。

共通qualifier拡張はa54ede8d1の旧版を保全し、既四正counter判定を不変更、callerの明示reasonがありactual XMLにBRANCHが無い場合だけL/M/Cと全present counter miss0を検査する。present Branch/欠落line/曖昧reasonを拒否する管理三＋profile等計七0/pyflakes0。除外/100補完/新global合成0、未実行native/実観測成功へ転用しない。当job/reader終了、fresh86/残14/reset1793082864・secondarynull/券0。次、独立した試験DB constructorのBUG1633/YKT1386（静的発見・実再現前）を計画1513で扱う。正式・canonical17・工数null不変。
