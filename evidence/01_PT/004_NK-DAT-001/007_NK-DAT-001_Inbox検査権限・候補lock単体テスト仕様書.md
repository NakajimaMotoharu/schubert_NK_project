# NK-DAT-001 Inbox検査権限・候補lock単体テスト仕様書

2026-09-09 V016回帰追補（SSC-049/PG-D-141、BUG-127/129・YKT-102）: 現在の独立catalog期待値はversion付きmigration001～016の16件、業務/technical計23table・PK23/FK23/UK constraint30/CHECK154/constraint trigger1。QWK partial unique indexはconstraint数へ混同せず045/PT192で別照合する。後述の初回V005～015等の値は当時の履歴であり、現在の回帰期待値には使わない。全31route・更新3成功のQUESTION/JOB、ERROR/NONE、168hと6種参照matrixは045/PT177～192および015/PT051～056へ追跡。各Programの実行結果・manifestにある正式sourceを正とし、未実行を合格へ含めない。

## 1. 対象・根拠

Program NK-DAT-001、V008の`maintenance_next_auth_inbox`/grant、provisioning001のschubert_inbox_inspector。RD OPS-009/DAT-009/MQ-008、UI212/241/251、SS331 §3.4/324 §12/332/341/343/352、QA-046/UIC-006/SSC-049、PG-D-121、BUG-014/YKT-012。
PostgreSQL 18の実DBで、公開SQL APIとcatalog、SQL後条件を独立期待値にする。追加SQLの全IF/AND/OR/NULL/empty/exception/lock分岐を下表へ対応付ける。Java wrapperがないSQL artifactへJaCoCoの架空100%を付けず、SQL分岐matrixと既存Java全coverageを併記する。

## 2. Case一覧（未実施）

| Test ID | 目的・入力/操作 | 独立した期待値 |
|---|---|---|
| PT-DB-INBOX-017 | role属性、owner membership、function owner/security/search_path、PUBLIC権限 | 専用LOGINだけ、特権false、owner membership0、限定EXECUTEのみ |
| PT-DB-INBOX-018 | NULL run/cutoff、±infinity、backup無し/片方/別run/別日/未完了、成功両方 | 22023または55000、対象0・変更0。最初のafter=NULLは許可 |
| PT-DB-INBOX-019 | 期限前/丁度/超過、PROCESSING/COMPLETED/ERROR、LGN/LOG/他layout、UUID順・cursor | expired LGN/LOGの完了行だけPK順に最大1行。cursor以前を再取得しない |
| PT-DB-INBOX-020 | 候補Inboxへの別connection更新/DELETE/lock、親transaction rollback | 保持中はNOWAIT拒否、終了後取得可、行は不変 |
| PT-DB-INBOX-021 | AUTH_SESSION存在/欠落/NONE、参照の別connection更新、backup SUCCESS行更新 | 存在参照/backupをFOR SHARE保護。欠落は補完せず返し、Javaの参照検査が拒否。SQLは認証を与えない |
| PT-DB-INBOX-022 | app/batch/Web/backup/opsのfunction呼出し、検査roleの直接Inbox/password/Web SELECT・DML・DDL・SET ROLE | 全て権限拒否。許可9列だけSELECT成功、他auth列は拒否 |
| PT-DB-INBOX-023 | 71419602を別sessionが保持、解放後再試行、未知cursor/空候補 | LOCK_BUSY 55P03、再試行取得可、候補0は空集合。lockを失った行を削除へ使わない |
| PT-DB-INBOX-024 | Flyway新規8件/再適用0、既存V001～007 checksum維持、schema/table/関数/既存cleanup回帰 | 既存DDL/PK/FK/UK/role条件を維持。SQL検査は削除・復号合格ではなく不正暗号も未検査として返す |

fixtureは隔離PG18/syntheticユーザー/Inbox/session/backup行、実connectionと明示transaction。秘密鍵/実credential/実dumpを使わない。DBの任意変更は隔離fixture内だけ。期待ID/件数/SQLSTATEをliteralにしProductionでexpectedを作らない。caller/競合connectionの終了とrollbackを必ず確認する。

## 3. 実行・証跡

005と同じJava25/Maven/Flyway/JDBC/toolchainで `./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress clean verify`。実行環境/日時/branch/commit/command/exit/SQL分岐matrix/実際値/関連BUG/SSとsanitized出力hashは008結果へ確定後記録する。
未実行/failed/flaky/skippedは合格へ加算しない。既存メッセージ削除functionの未検証Inbox削除はBUG-014の別残件であり、本関数だけで基盤100%としない。
