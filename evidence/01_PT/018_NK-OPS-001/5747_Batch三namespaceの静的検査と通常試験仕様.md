# Batch三namespaceの静的検査と通常試験仕様

NK-OPS-001、WBS-F03/2-2-b／P004-03／C02、SS331／332／341／343、451 §5、BUG-3644／YKT-2863。BackupManifestCodec、MaintenanceRecords、UnitStateParser。元の各namespace試験はprivate constructorの反射を使っていたため、当通常選択から三件を削除し、Git履歴、元JUnit、元rawを保全する。対象Javaや業務出力の変更なし。

| 観点 | Fixture・操作・独立期待 |
| --- | --- |
| PT-BAT-STATIC001 | 現BatchのBackupManifestCodec classfileでfinalとprivate引数なしconstructorを一件、他memberのstaticを確認。 |
| PT-BAT-STATIC002 | MaintenanceRecordsに同じ非生成契約。 |
| PT-BAT-STATIC003 | UnitStateParserに同じ非生成契約。 |
| 既Backup Manifest 16件 | 元PG38222／38228の独立JSON・スカラー・不変値・境界・並行。元golden resourceのbyte/hash一致。 |
| 既Maintenance 19件 | 元PG37284の純byte、UTC・fixed outcome、借用byte不変、構造・境界・null・並行。 |
| 既Unit State 6件 | 元PG38058の合成byte、固定7項目・重複・異常・ASCII・並行。実Unitは観測しない。 |

製品依存は現Batch JAR中の確認したpure型に限定。固定Java25.0.4、JUnit1.13.4、JaCoCo0.8.15。実Backup、原本、サービス、実DB、保留32、Root11、nativeは範囲外。二種の元合成出力のみ隔離run内targetへ出す。三静的検査は通常の件数と無フィルターcoverageに加えない。PG42920 manifestに環境・対象source・コマンド・JUnit・CRC・coverageと残欠落。
