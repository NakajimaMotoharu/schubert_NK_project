# SCM-005 Maven BOMの座標一意性

NK-OPS-001、RD171、SS352 §13、WBS-P018-02/2、BUG-3664、YKT-2881。

| Test ID | 独立期待 |
| --- | --- |
| PT-OPS-SBOM-026 | 同じclassifierのquery項順を変えた二component、rootと値が等しいcomponentを重複として拒否。 |
| PT-OPS-SBOM-027 | 同じgroup/name/versionで既定とvariantのJARを独立の2件として検証。 |
| PT-OPS-OSV-011 | 検証で重複を拒否し、scannerの呼出は0。 |

固定3 byteと独立のSHA-256を用いる。Python 3.14.4、`PYTHONPATH=tools/quality:tools/quality/tests python3 -B -m unittest -v test_verify_maven_sbom test_verify_maven_advisories`。旧工具で改修対象3形の欠落（テストexit 1）。修正 `2d7cdcda0e` で21成功。保存六modelは元入力のSHAと、元repositoryでartifact hash／graphを再照合。最初に選んだ共有cacheはBootstrap snapshot SHA不一致。元receiptのrepositoryへ戻して一致を確認した。QA-061は配布条件と担当が未決。署名、現release、外部scanner、製品PTは別。

[公開manifest](evidence/PG43084-sbom-unique-maven-identity-v1/manifest.json) SHA-256 `43cefa860a41041004ac9bef1454ff88c551d20618387913e0f1503b6aa0c12d`。
