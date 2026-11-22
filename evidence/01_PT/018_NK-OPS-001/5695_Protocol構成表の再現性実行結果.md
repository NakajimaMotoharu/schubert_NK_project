# Protocol構成表の再現性実行結果

SCM-005／SS352 §13、WBS-P018-02/2、5694のPT-OPS-SBOM-005。CycloneDX 2.9.3の公開ソースが参照するMavenプロパティは project.build.outputTimestamp。初回はoutputTimestampで指定し、BOMに実行時刻が入った。元出力と判定はPG42604に保全した。

同じJDK25・Maven3.9.12と固定POM八件を独立ディレクトリへ複製。Mavenのプロジェクトプロパティを固定し、個別実行番号を出力させず、ProtocolのmakeBomを二回実行した。Maven offlineの準備実行はプラグインのオンラインモード要件で終了1。その試行で構成表を作らず、二回目は未実行。修正後二回はMaven標準のオンラインモード、strict checksum、既取得の工具／依存を使った。

現二出力は終了0、CycloneDX schema 1.6、実行時刻と個別serialの項目なし。依存一件とedge、SDK SHA-256、ライセンスは5694と一致。二つの出力SHA256は 8c62b7f9dd0b7f079238f82aeb4ace7302d16720d9b7860ed9db93de4241bdf3。正式試験・全6製品構成表・CIやリスク検査は未実施。

- evidence/01_PT/018_NK-OPS-001/evidence/PG42606-p01802-protocol-reproducible-bom-requalification-v1/manifest.json
- https://github.com/CycloneDX/cyclonedx-maven-plugin/blob/cyclonedx-maven-plugin-2.9.3/src/main/java/org/cyclonedx/maven/BaseCycloneDxMojo.java
