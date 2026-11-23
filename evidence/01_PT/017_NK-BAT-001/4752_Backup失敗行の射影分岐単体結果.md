# Backup失敗行の射影分岐の単体結果

PG43930、Core 23a7874f01b432a01256ee0e58823f8038fca59a、試験 1a17ed920f6657b747175e6fc880b937d5d9ceef。新UTC004～007と既11件を同一execで実行し15/15成功。書式、Checkstyle 0。PMD生1は単独合成JDK JDBC interfaceの定義loaderで、適用外根拠と元データを保持。対象の生I361/361・L65/65・M10/10・C1/1・B66/68。残る2枝はverifyRow正常終了時のTWR close判定。分母を保持し、正式451と実DBは別。 [仕様](4748_Backup失敗行の時刻瞬間照合単体仕様.md) [当証跡](evidence/PG43930-backup-projection-current-single-exec/manifest.json)
