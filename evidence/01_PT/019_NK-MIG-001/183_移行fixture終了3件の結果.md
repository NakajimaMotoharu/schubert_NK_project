# PG45298 移行fixtureの終了結果

固定試験source `d028594096eb2f246af38e7f0babd5e6ddd54f2e`。PT-BOOT-MIG-WORKER001～003全実行・全成功、失敗・エラー・スキップ0。単一execで `close` L8/M1/B2全到達。試験補助型の未到達メソッドは生結果に保存。正規Spotless・Checkstyle・SpotBugs0。PMD生13件は元結果とともに品質側に残す。試験基盤のみの3件で製品試行・実CHRには加算しない。

[元コマンド・XML・測定](evidence/PG45298-fixture-worker-termination-and-interrupt/manifest.json)

## PG45528 Schema並行fixtureへの適用

整形後の固定sourceでPT-OPS-SCHEMA008と補助WORKER004が各1件成功。一次例外と一件の抑制診断を対照で確認。従来WORKER001〜003は上記元結果で保持する。JAR二本から実使用7物理の同一性を確認。正規書式2/2。選択一件の製品四指標はL73/93、M13/18、C2/2、B38/72。旧16件の単一測定とは別に保持し、実DB・Flywayは対象外。

[当sourceのコマンド・結果](evidence/PG45528-current-schema-fixture-diagnostics-and-format/manifest.json)
