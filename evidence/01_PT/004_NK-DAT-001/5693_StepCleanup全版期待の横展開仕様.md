# StepCleanupの全版inventoryと歴史期待値

WBS-P004-01.02/2、DAT-009、SS331／343、BUG-3722／3723、YKT-2922。製品の固定版一覧は001～031。

- PT-DB-INBOX-266（062仕様）。StepCleanupBoundaryTest.appendOnlyMigrationInventory。V001～024の元hash、V025の固定hashと各版名、V029の固定index、SCHEMA一行／table24を保持。現全SQL資源の版順・版付き成功履歴件数は、製品資源とは独立に定義したMigrationInventoryから得る。V024／025までの部分fixtureは旧版固定条件。
- PT-DB-ACL031-S04。現試験の全版期待が独立版一覧を参照し、V029を固定の歴史版として扱い、版付き履歴とSCHEMAを区別することをソースで確認する。実行は既存三静的とまとめて `python3 -B evidence/01_PT/004_NK-DAT-001/input/5691_ssc479_routine_acl_source_test.py -v`。
- 実DBのPT-DB-INBOX-266とBUG-3722／3723の正式再試験は別。既存DBC fixtureの環境と権限成立後に通常入口から実施し、版31・SCHEMA1・Flyway validate/再適用0・同元hashを個別に確認する。
