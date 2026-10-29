# 2584 Metric・Mode・保持設定元whole二十一 現source通常PT仕様

2026-10-30 JST/PG-D858/event2970/source0061・F03開始0.5/2/4cap10、現canonical五Main/Test pathはP01809候補未受入/追加費0。後続2412/2351/2328等と現16exec183method31suiteを照合し、本scopeは未含有。原sourceの成功を現sourceへ移植せず元whole三を新一JVMで資格確認する。

PT_DEFAULT：MetricContractTest全6/MonitoringModePolicyTest全7/MonitoringRetentionConfigurationTest全8と各helper/initializer、Main MetricContract/MonitoringModePolicy全bodyを読取。Java enum/Set/Map/Duration等のmemoryだけで、service/mode/retentionという名称は実環境操作でなくcaller-supplied observation/configの値契約。Resource読取は原26行metric-catalog.tsvだけ、任意path/private情報に触れない。自己pool64task・finally/TWRの当pool後処理だけでRoot/VM/Unit/DB/JMS/鍵/native/intent/permit/回収/削除/実mode switch/host設定・権限変更0、既HOLDの部分抽出/新stub/拒否試行0。

|元Test ID|入力・独立期待と観点|
|---|---|
|METRIC001～006|原独立TSV26行のname/type/labels、unknown/null/空/大小文字/余白・敏感key追加/欠落・immutable map/set・HTTP buckets .05,.1,.25,.5,1,1.5,2,2.5,5。64task同じ元26行を保持。|
|MONMODE001～007|DEBUG true/15日/5,000,000,000decimal byte・STANDARD false/0/0、四service観測全32真理値（mode二×16）、missing/null/未知/alias固定診断、input非変更・64taskの不変。実サービス起動/停止はしない。|
|RETCONF001～008|15/5,000,000,000と0/0の厳密一致、day±1/byte±1/GiB別値・missingと正当0の区別、負/最小/最大/overflow/Null、service観測と保持値の独立性・64task不変。元record値契約のequals/hash衝突・固定toString goldenは原仕様として保持し、coverage目的の新人工呼出しを追加しない。|

原TSV path=src/schubert-nk-batch/src/test/resources/monitoring/metric-catalog.tsv、SHA1447faabc6f056120561e4356dd75696ace4df613b6379246af29f9837fc43dc。Git当source/現byte/新classrootへのcopyを同pinで照合、fixture/Main/Testは非改変。期待値をproduction methodから生成0。14128 checked entry→Java25 proc-none/Xlint-all/Werror・parallel=false・新append=false/session・外JVM180秒、局所pool invokeAll/get/TWRの無期限可能性と区別する。

14130は元XML/FES0/全Source/六Jar/元fixture＋copy/単一session・CRCと全二Source五physical（Metric.Kind・Mode.DetailService/RetentionConfiguration含む）を独立測定する。default generated filter以外変更0、未達は除外せず保存し全artifact/native/451/正式を認定しない。結果2585/manifestへ実command/環境/時刻/branch/source/退出/hash/counter/関連障害を保存、新機能ID/受入0/全HOLD・QA051final保持。
