# BatchとAPIのJackson依存是正の試験仕様

NK-OPS-001、WBS-P018-02/2、RD171 SCM-005、SS352 §13、BUG-3596／YKT-2830。対象は親POMの `tools.jackson.core:jackson-core` と `tools.jackson.core:jackson-databind` の版管理。Flyway 13.4.0のBatch通常依存とAPI試験依存に、同じLTSの3.1.8を使用する。既知指摘の元出力はPG42656。

| Test ID | 入力・操作 | 独立した期待値 |
|---|---|---|
| PT-OPS-SBOM-022 | 元と現の六製品Maven dependency treeをruntime・testで解決 | 影響scopeの2座標を3.1.5から3.1.8へ変更。公開Centralの3.1.8。別majorの座標、Flyway自体、他モジュールへの未使用依存を維持 |
| PT-OPS-SBOM-023 | 同一候補のCycloneDXと固定OSV snapshotを用いる | 対象の元7指摘の有無を独立比較。元の結果、候補結果、件数と実際の対象を記録 |
| PT-OPS-SBOM-024 | Flywayが使うJARのversionと公開API、候補Batchの正規ビルド、許可済み関連通常PTを確認 | 同じ支援module、JDK、旧ABIとの比較、期待一致、終了code、適用が未確認の範囲を保存 |

Mavenの入力には固定の親・子POMと既カタログのCacheを使う。OSV snapshotの日付、tool version、SHA-256、終了コードは実行証跡へ保存。QA-056、実DB・配備と全scope 451の未検証項目は受入判定に残す。
