# NK-DAT-001 通常batch削除境界単体テスト仕様書

2026-09-09 V016回帰追補（SSC-049/PG-D-141、BUG-127/129・YKT-102）: 現在の独立catalog期待値はversion付きmigration001～016の16件、業務/technical計23table・PK23/FK23/UK constraint30/CHECK154/constraint trigger1。QWK partial unique indexはconstraint数へ混同せず045/PT192で別照合する。後述の初回V005～015等の値は当時の履歴であり、現在の回帰期待値には使わない。全31route・更新3成功のQUESTION/JOB、ERROR/NONE、168hと6種参照matrixは045/PT177～192および015/PT051～056へ追跡。各Programの実行結果・manifestにある正式sourceを正とし、未実行を合格へ含めない。

QA-046/SSC-049、BUG-014/YKT-012、PG-D-126。RD DAT-009/MQ-008/OPS-009、UI212/241/251、SS331 §3.7/332 §11.4/341。対象V011 maintenance_cleanup_message_stores、OutboxCleanupBoundaryTest。既存PT-IDEM-013/DB-011を回帰する。Productionの期待値生成は禁止し、以下のliteral後条件を使用する。

| Test ID | method / 目的・入力/操作 | 期待値・独立根拠 |
|---|---|---|
| PT-DB-INBOX-065 | inboxRowsAreNeverTouched / expired全31route＋unknown、COMPLETED/ERROR/PROCESSING、NULL/bad cipher/参照を合成しbatch呼出し | 全Inboxの列値/件数不変、正常Outboxだけ削除。SS実行主体分離 |
| PT-DB-INBOX-066 | outboxBoundariesAndSharedLimit / API/Web SENT7日±1µs、lease±1µs/null、PENDING/ERROR、limit1/1000 | 期限strict・leaseなし/失効だけ、API→Web合計上限、同run再走0、rollback復元。SS332/341 |
| PT-DB-INBOX-067 | invalidArgumentsAndFixedReasons / 各null/±infinity/limit0/1001、別run・backup不在 | 22023、または0件BACKUP_GATE。秘密値非反映/全データ不変 |
| PT-DB-INBOX-068 | backupStatesAndDatesAreLocked / 5状態/別JST日/endedなし/同run2成功/片側、backup行更新競合 | 両側同日SUCCESSだけOK、その他BACKUP_GATE、処理中backup更新55P03・終了後更新可 |
| PT-DB-INBOX-069 | competingMaintenanceNeverDeletes / advisory競合・対象Outbox行lock、正常release/commit/rollback | LOCK_BUSY0件、行競合だけSKIP、他rowのみ削除、解放後残row再走成功 |
| PT-DB-INBOX-070 | backupSnapshotCannotBeReplaced / DB backup lock待ちを観測して別TXでCONFIG追加 | 当該snapshotはBACKUP_GATEで0削除、次TXは両行lock後削除。時刻sleepに依存しない |
| PT-DB-INBOX-071 | currentFunctionsAndRolesCloseBypasses / owner/security/path/role/default/public、現行全cleanupと専用検査DELETE分類 | batchのみ本function可、他role42501、batch直接Inbox/検査function不可、全汎用cleanupにInbox DELETEなし。V008～010は検査roleだけ |
| PT-DB-INBOX-072 | migrationAndLegacyOraclesRemainExplicit / V001～011 inventory/再適用、旧V001～010固定hash、旧DB/Outbox期待差分 | 11履歴、再適用0、旧10hash不変。旧不正Inboxは2保持、Outbox7日期待不変更 |

Fixtureは隔離実PostgreSQL 18.6、合成user/Inbox/Outbox/backupのみ。production暗号byte/credential/masterを使用しない。SQL NULL/欠落/未知/例外/並行は上表。Java追加処理なしのため本SQLへJaCoCo分母を捏造しない。全Java4種100%/静的解析はroot gateで維持し、SQL条件全枝を020に列挙する。

実行: 421のJDK25/Maven3.9.12/driver42.7.13/Flyway13.4.0でOutboxCleanupBoundaryTestとMessageStoreCleanupTest/DatabaseMigrationTest/既存Inbox境界を並行して開発・検証後、root clean verify。対象commit・実行日時・command/exit・実行環境・入力/期待/実際/Test ID・BUG/SSC・sanitized hashは020とevidence/outbox-only-cleanup/manifest.jsonへ確定する。未実施を合格へ算入しない。
