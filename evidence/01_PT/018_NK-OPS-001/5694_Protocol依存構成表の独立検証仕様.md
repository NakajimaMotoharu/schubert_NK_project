# Protocol依存構成表の独立検証

SCM-005／RD171、SS352 §13、WBS-P018-02/2。Java 25とMaven 3.9.12、Maven CentralのCycloneDX Maven Plugin 2.9.3を固定し、既存root POMと各module POMだけを複製した作業領域でProtocolのmakeBomを直接実行。通常Mavenライフサイクル、Java compile／単体試験、実配備、CIの起動は未実行。

| Test ID | 固定期待 | 結果 |
|---|---|---|
| PT-OPS-SBOM-001 | rootはProtocol 0.1.0-SNAPSHOT、compile依存はorg.jspecify:jspecify:1.0.1、JUnitのtest scopeを含めない | PASS |
| PT-OPS-SBOM-002 | ルートからJSpecifyへ一辺、JSpecifyの子は空。CycloneDX 1.6 | PASS |
| PT-OPS-SBOM-003 | JSpecifyのApache-2.0を識別し、JARのSHA-256と出力の記載が一致 | PASS |
| PT-OPS-SBOM-004 | compile/test/packageに相当するJava class・JUnit reports・JAR生成を観測しない | PASS |
| PT-OPS-SBOM-005 | 生成時刻に依存しない設定を有効化 | FAIL。指定した値が読まれず、BOMに実行時刻が残った |

固定期待は依存宣言、個別JARと公開仕様から独立に作成。補助工具の結果4件を正式PT、coverage、脆弱性検査、全六製品のSBOMに加算しない。自動CIと各build、脆弱性・ライセンス方針、配布側条件はP018-02の未成立事項。

- evidence/01_PT/018_NK-OPS-001/evidence/PG42604-p01802-protocol-standard-software-inventory-v1/software-bom.json SHA256 e0a9ca0b86bfba508e0c9ba7c783235a7624a48a871396380bbcac643c026be7
- evidence/01_PT/018_NK-OPS-001/evidence/PG42604-p01802-protocol-standard-software-inventory-v1/manifest.json
- https://cyclonedx.org/docs/1.6/json/
- https://github.com/CycloneDX/cyclonedx-maven-plugin/releases/tag/cyclonedx-maven-plugin-2.9.3
