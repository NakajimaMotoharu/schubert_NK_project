# API／Web標準SDK段階解放の単体仕様

NK-OPS-001、ApiStandardMetricSource.close／WebStandardMetricSource.close、RD171 MON-010～013、UI252、SS311／351、PG-D614／615、WBS-P018-09、BUG-3418／YKT-2740。

**APIHOST017／WEBHOST017**。役割ごとの既存自己所有fixtureに固定SDKを供給する。DEBUG bind後、GCは正常close、registryは一回目だけ固定Runtimeにする。期待はGC→registry、同じ失敗、DEBUG scrape拒否。明示再closeによりregistryのみ再試行し、完了後は冪等。期待総順序GC→registry→registryは所有契約から独立に定める。既16件ごとに、前段失敗、初回と部分取得、close順序、並行、null、固定モード・roleを影響回帰する。

PG40876は旧コードの新1件ずつ、PG40878は修正後の全17件ずつ。各roleのclasspathは固有ソースと固定SDKに限定し、Batch試験、実サービス、外部収集、全451は別。実行環境・対象source・指標と終了状態はmanifestを参照する。
