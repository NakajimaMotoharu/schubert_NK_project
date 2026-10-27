# Main残Map八件・所有とcopyのsource-only PGレビュー

WBS-F03/PG-D737/event2688、source442441c83f73935eb2bd33cd40a7b9884eb7dfe3/save3370b92a2 push97439真正0、開始0.5/2/4週次共有pp cap10/fresh60残40/reset1793599188。先行の選定読取はInspector全416行とMaintenance先頭240行、以後残241～1426/三不変値record全文を確認。動的許可や原成功を再発行しない。

対象MainはMaintenanceRunFiles（原owner/costP00403、NK-BAT-001/OPS009/UI251/SS341343/SSC055/PT-BAT058..113）とInspectorUnitSnapshot（P00404、NK-OPS-001/UI251/SS341343/SSC060/UNIT001..008）。PMD02847..02850はretirementScanのruns/begins/done/plans、02853..02855はscanのruns/begins/done、03093はparseのfields。全八UseConcurrentHashMapを個別span/属性/IDへ結ぶ。

Maintenanceのprivate scan二methodは毎回new HashMapで、read/decoder/IO portへMapを渡さず取得値だけをputする。retirementScanはprivate Inventory compact constructorのMap.copyOf四で防御copyし、scanはprivate static graphが検証後Map.copyOf三をprivate Graph recordへ渡す。Session.performのstateLock/executeのscopeLockは補助根拠だが、Map自体が呼出し内local→copyで外へ渡らないことを主根拠とする。Map値のBatchRun(UUID,Instant)/MaintenanceActivation(BatchRun,UUID)/MaintenanceCompletion(activation,Instant,enum)も全文で不変型を確認。Inspectorのparseはfresh fields→private constructor final values=Map.copyOf、入力clone/wipe・返すString/enum/Optional/数値はMapの可変aliasを出さない。

metadata001：normal12312固定source/inputhash・原10690 row/完全属性・byte span/独立enclosing method・copy経路・private値型/原ownerを確認。002：source/ID/path/属性/変数/method/span/control/owner/コピー根拠/新PTや受入水増しを反例で拒否し、sourceContexts/rawRetainedの意味と分母を一意ID集合八から導出する。003：原source/上位仕様/コード/実PT/staticの変更0、原raw8保持/全F03判定待ち、current-setへの理由参照八だけを結合。004：485追加参照/486inventorySHAのみ、983sourceRows/原owner-cost/artifact/要求/予算/受入不変・所定全監査HOLDを維持。

source-only reviewであり、Main.create/Session.scan/retire/observe/parse/Unit/Root/DB/Backup/ファイル/VM/native/署名/配置/permit/鍵を呼ばない。原InspectorUnitSnapshotTestやMain関連保持fixtureの部分抽出/別harness/新Inputで代用しない。新製品PT/coverage/動的qualification0、既免除を増やさない。将来Mapをfieldへ移す・copyを除く・mutable valueへ変える・callbackへ渡す場合は再評価が必要。具体理由が確定しないものはRAW/UNKNOWNを保持する。実結果/hash/負例/集合/保存は2324以降へ、正式1964/53・17/190・工数null/QA051final/HOLD/原見積不変更。
