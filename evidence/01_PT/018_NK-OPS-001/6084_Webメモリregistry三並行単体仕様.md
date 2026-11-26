# Webの三メモリregistry観測の並行一次診断

WBS-F03/2-2-b、P018-10、SS333・351・354、BUG-3967／YKT-2997。対象は表の既試験だけ。合成pool tuple、Outbox六値と独立系列、duration 256のbucket／別registryを確認する。

| ID | 選択メソッド | 独立期待値の元仕様 |
| --- | --- | --- |
| WEBPOOLMETRIC006 | WebDbPoolMetricRecorderTest#webPoolMetric006ParallelUpdatesKeepWholeImmutableSnapshots | [1728](1728_WebPool観測結線_単体テスト仕様書.md) |
| WEBOBXMET007 | WebOutboxMetricRecorderTest#webObxMet007ConcurrentPublicationKeepsWholeFixtureIdentityAndIndependentGaugeVector | [1721](1721_WebOutbox観測経路_単体テスト仕様書.md) |
| HTTPDUR008 | OverflowSafeHttpMeterRegistryTest#httpDur008ConcurrentWorkersAndIndependentOwnersKeepExactIntegerVector | [4187](4187_HTTPメトリクス原二十八単体仕様.md) |

各workerと入力の個数、元の5秒又は10秒結果取得・10秒終了は元仕様に従う。一次失敗と終了失敗が重なる検証は既ViewFixtureWorkers試験を参照する。各今回TestIDの終端を当当Web三ソースの局所クラスと固定SDKの一つのexecで取得。通常の既済別試験、実DB／原本／領域アクセスは対象外。
