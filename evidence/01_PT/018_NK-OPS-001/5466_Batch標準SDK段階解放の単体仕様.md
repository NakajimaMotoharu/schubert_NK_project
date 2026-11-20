# Batch標準SDK段階解放の単体仕様

NK-OPS-001、BatchStandardMetricSource.close、RD171 MON-010～013、UI252、SS311／351、PG-D615、WBS-P018-09／C07、BUG-3418／YKT-2740。

**BATCHHOST017**。既存owned SDK fixtureのGCを一回正常closeし、後段registryのcloseだけを既知のインスタンスで失敗させる。独立期待はclose一回目で順序GC→registry、元失敗同一、DEBUG scrapeを拒否、明示close再試行でregistryのみ、終端後は冪等。合計順序GC→registry→registry。BATCHHOST012の前段GC失敗時は、既期待どおり前段再試行後にregistryへ進む。既16の正常・欠落・異常・並行期待を同一sourceで照合する。

SDKとscopeをPG25262／PG8170へ固定し、自己所有レジストリとJVMの既fixtureだけを使う。実サービス、外部collector、接続、既GC handlesには触れない。修正前後の実行command・終了・対象hash、coverageはPG40872／PG40874のmanifest。全451・実観測の受入は別途証拠を要求する。
