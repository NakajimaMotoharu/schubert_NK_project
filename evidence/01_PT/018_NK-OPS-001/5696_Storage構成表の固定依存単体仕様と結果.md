# Storage構成表の固定依存単体仕様と結果

SCM-005／SS352 §13、WBS-P018-02/2。PT-OPS-SBOM-006。PG42606と同じJDK25、Maven3.9.12、CycloneDX2.9.3を使い、StorageのPOMだけを対象に直接makeBomを実行。期待はStorage 0.1.0-SNAPSHOTとJSpecify 1.0.1のみの一辺、Apache-2.0、公開SDK JARのSHA-256一致。JUnitのtest scopeは配布用構成表に含めず、PG/PTで必要な試験の対象はそのまま。期待は親POMの固定値・公開JARとCycloneDX 1.6から独立に作成。

試験結果は終了0、期待一致。固定出力 evidence/01_PT/018_NK-OPS-001/evidence/PG42608-p01802-storage-standard-software-inventory-v1/software-bom.json SHA256 fd913b405154e549b0903b0249316f5c10a97358ed1dcfb08ddbb6dd672402ae。現source 1b0545b63644558ba6732e683559605e3c7510fd。tool、OS、argv、終端は同manifestに保持。Java本体のcompile／通常PT／SDK接続、CI起動、実配布、ライセンス方針判定・既知脆弱性スキャンの証拠は対象外。
