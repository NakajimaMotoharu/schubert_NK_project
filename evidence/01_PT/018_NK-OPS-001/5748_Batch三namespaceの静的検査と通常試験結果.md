# Batch三namespaceの静的検査と通常試験結果

PG42920、2026-11-23 JST、dev-foundation、Core `e8368d22c4da2ec841f008df793594d3be9066af`、試験 `76f7a35e813a1b95a47e74ef02d4e4d5a8137288`。元条件を保持した41件すべて成功（Backup 16、Maintenance 19、Unit 6、7 suites）。失敗、エラー、skip、対象未実行0。旧反射3の実行0。親外部処理へ接続せず、元合成出力は隔離されたrun内だけに生成。独立Backup goldenのSHA-256と一致した。

| 無フィルター対象 | 行 | method | class | branch | 命令 |
| --- | ---: | ---: | ---: | ---: | ---: |
| BackupManifestCodec | 77/79 | 6/7 | 1/1 | 12/12 | 386/393 |
| MaintenanceRecords | 66/68 | 15/16 | 1/1 | 22/22 | 330/337 |
| UnitStateParser | 28/30 | 3/4 | 1/1 | 36/36 | 189/196 |

未測定6行・3 methodはいずれもprivate constructor。各非生成の静的検査、物理名と独立CRC、JUnitの元件数を分離した。元coverageを足したり対象除外を入れたりしていない。YKT-2863の後続11、実Backup・C02・P004-03・六製品451へ継続。

公開 `evidence/01_PT/018_NK-OPS-001/evidence/PG42920-batch-three-namespace-without-private-reflection-v1/manifest.json` SHA-256 `79331f0bdc1288dea5b7b82edd6a4f772e510ab631e1f60746ac3f254c263862`。
