# NK-DAT-001 Inbox永続進捗SQL単体テスト仕様書

RD DAT-009/MQ-008/OPS-009、UI212/241/251、SS331 §3.8/341 §7.3/343、QA-046/UIC-006/SSC-049、BUG-014/YKT-012、PG-D-127。Production V012の進捗table/3function、InboxInspectionProgressBoundaryTest。Java/oneshotは本SQL合格に含めない。

| Test ID | method / 入力・操作 | 期待値と独立根拠 |
|---|---|---|
| PT-DB-INBOX-073 | newAndResumedRunKeepOneCutoff / 初回・同run・別cutoff・既完了 | 初回0/NULL/未完了、同run不変、別cutoff55000、再開で累積保持 |
| PT-DB-INBOX-074 | outcomesAdvanceOnlyMatchingState / DELETED/PROTECTED/END、cursor/件数不一致・UUID符号境界 | 対応countだけ増加、DB UUID順、重複/stale/不正Message拒否、END一度だけ |
| PT-DB-INBOX-075 | deletionAndCheckpointCommitTogether / 同TX削除→記録→rollback/commit、記録故障 | rollbackで行と旧進捗復元、commit両方確定、次run/readで二重計上なし |
| PT-DB-INBOX-076 | invalidInputsAndConstraintsReject / NULL/欠落/未知/非有限、全CK、count上限 | 22023/55000/23514等を分類、overflow22003で全rollback、NULLと0の区別 |
| PT-DB-INBOX-077 | backupAndConcurrentRunsStayLocked / 全backup/advisory・同run別TX・checkpoint lock | 未backup/競合で0変更、状態lockはtransaction終了まで、相互取り違えなし |
| PT-DB-INBOX-078 | completedProgressRetentionIsBounded / 400日±1µs/同run/未完了/RUNNING/FAILED/lock/limit | 完了・400日超・別run・非調査中だけ削除、上限と再走/rollback、他table不変 |
| PT-DB-INBOX-079 | rolesAndFixedFunctionsCannotEscalate / 全service/PUBLIC/owner/path/UTC | 検査2function/通常batch清掃1のみ、通常API/Web/batch/検査のbase SELECT/DML/SET ROLE不可。backup SELECTだけ維持してdump対象に含める、DML不可、暗号/Inbox権限増加0 |
| PT-DB-INBOX-080 | migrationAndInventoryAreAppendOnly / 新空DB/既存schema/再適用/旧hash | V001～012/22table/PK22/CK149、既存FK23/UK30/trigger1維持、旧11hash不変、再適用0 |

Fixture: 隔離実PostgreSQL18.6、合成run/backup/Inboxのみ、動作するDDL/Flyway/role、期待値はliteral SQL後条件と事前状態。production methodからexpectedを生成しない。実DB raceを同期、失敗/skip/flakyを算入しない。SQL全IF/WHERE/例外は022結果でTest ID対応を記録し、Java全4種100%/NullAway/SpotBugsはroot gateへ追跡する。

実行command/branch/source/日時/環境/exit/input・expected・actual/BUG/SSCは022と専用sanitized manifestへ確定する。秘密/raw wire/cipher/session/token/dumpを保存しない。未実施。
