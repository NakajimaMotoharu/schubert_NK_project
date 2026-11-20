# F02 API Repositoryの直接型依存の実行結果

| 実行 | Test ID | 期待値一致 | 物理 | 工具／試験判定の終了 |
|---|---|---:|---:|---|
| PG40584、元工具 | PT-F02-REPO-TYPE-001〜010 | 3/10 | 19 | 期待した違反検出の終了1／期待差による終了1 |
| PG40586、aa2da6a8eb | 同10と既55対照 | 10/10、55/55 | 101 | 期待した違反検出の終了1／独立期待と一致して終了0 |

元7見落としを型宣言単位で確認した。修正後は意図した計42指摘だけだった。現製品Core e7bfd5e1f2ec4b4e16ecf32601bed052b5330461に変更なし。

[PG40584 元結果](evidence/PG40584-f02-repository-declaration-before-v1/manifest.json)
[PG40586 修正後](evidence/PG40586-f02-repository-declaration-after-v1/manifest.json)
[PG40588 独立証拠](evidence/PG40588-f02-repository-declaration-independent-v1/manifest.json) SHA-256 e1a9cf5c9c19c3fb3fc42fdd7cd3633fe6435fcda79d5297fc7d4e3d2c45d768。

BUG-3390／YKT-2724。工具試験のみを計上した。F02は現API/Web JAR、StorageのJDBC一辺、全六依存とruntime・451が残る。
