## 現候補で12月2日の判定に使う資料

製品Core `8e2a6b055c45f9f868433c73174b87bc72972d77`。今回の正式判定IDは **0件**。四担当への引渡し資料は下表に集約した。最新の公開照合基点はmain `1a3ad1400e4effdf467681b65ff4be330fde045c`、dev-foundation `a630ea94aa6f2377a872365b3d0cf43143360b71`。この公開範囲で新しい担当受領・署名を確認できていない。

| WBS | 現候補の証拠 | 担当と未成立条件 |
| --- | --- | --- |
| F02 | 正規JAR 4/6、物理1,116。API/Web資源32/34。SYS要件13/13に証拠・不足を対応。正規Batchと同じ物理で整形後Backup18/18。 [PG44952](../../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG44952-f02-sys002-host-java25-packaging-boundary/manifest.json) [PG44956](../../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG44956-f02-current-thirteen-criterion-handoff-witnesses/manifest.json) [PG44828](../../../../../evidence/01_PT/017_NK-BAT-001/evidence/PG44828-current-backup-original-eighteen-plus-two-and-pmd/manifest.json) | ビルド・アーキテクチャ／Storage担当。API/Web正規JAR、QA-056四型、QA-062、SSC-461のStorage実証、当候補の起動と13要件の個別判定・署名。 |
| F03 | Protocol正規Maven 174件／40スイート、失敗・エラー・スキップ0。実測行・メソッド・クラス・分岐の未到達はすべて0。正規4製品のNullAway 485源と分けて、現API148/286源、Web166/262源を重複なく確認。許可済みCheckstyle／SpotlessはMain1,028/1,033、試験1,164/1,196。 [PG45004](../../../../../evidence/01_PT/002_NK-PRO-002/evidence/PG45004-current-protocol-canonical-ci-174/manifest.json) [PG44872](../../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG44872-six-product-checkstyle-exact-source-delta/manifest.json) [PG44874](../../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG44874-six-product-canonical-spotless-seven/manifest.json) | 品質担当。全六製品の同一source/runで451、保留Main5・試験32・Root11、PMD等の原指摘の適用性と所有者判断、正式署名。ProtocolのPMDは別記録。 |
| C02 | 保守再起動前の期限境界と停止条件の現証拠。 [PG45002](../../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG45002-g13-two-current-ops-test-deltas/manifest.json) | 運用・Unit担当。専用受けUnit、同bootの現所有・実効設定・owned終端。 |
| F04 | 直接OS環境の既存引渡しと適用条件。 [PG44794](../../../../../evidence/01_PT/018_NK-OPS-001/evidence/PG44794-current-four-owner-handoff-and-plan-gap/manifest.json) | 基盤・haruka担当。現利用権限・所有、同候補FileStoreと実経路・Browserの結果。 |

歴史SSC447は152/152、失敗・エラー・スキップ・未実行は各0。今回の正式受入は累計16/190、重点0/5、指定0/12、正式加算と完了元行価格は0。正式PT1,964件／53領域を維持する。今回再開からの技術試験実行は延べ1,276件。重複と候補の変更を含むため、固有試験数と工数完成率は未確定。
