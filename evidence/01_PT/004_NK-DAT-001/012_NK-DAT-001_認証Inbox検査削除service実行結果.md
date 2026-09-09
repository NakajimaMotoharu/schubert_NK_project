# NK-DAT-001 認証Inbox検査削除service実行結果

## 1. 対象・判定

011仕様/PT-DB-INBOX-033～040、AuthenticationInboxCleanup・内部Candidate・InspectionRun・InspectionStep/Outcome・InboxMaintenanceExceptionの6class。探索全47件PASS、新6classのline/method/class/branch100%、NullAway/format成功、SpotBugs0。正式全体回帰・収集前のためまだ確定合格に加算しない。PG-D-122、QA-046/SSC-049、BUG-084/YKT-075再試験中。非認証/oneshot/全run管理/V006置換は未完了。

## 2. 探索・期待値正常性

| 実行・終了日時JST | 実際結果 | 判断 |
|---|---|---|
| session37216 / 2026-09-09 09:04:19 | 新8＋既存39の47件PASS、Protocol5/Storage16も成功、SpotBugs0、exit0。ただし新Cleanup line2/branch2未網羅 | 途中結果。rollback故障、資源終了を一経路へまとめる構造整理、鍵世代を追加確認。並行testの広すぎる例外許容をBUG-084/YKT-075としてc0cd60ffで修正前起票 |
| session36606 / 09:07:44 | 47件再PASS、全新6classの全line/method/class/branch missed0、SpotBugs0、exit0 | JDBCの各mandatory NULL、全fault/rollback失敗、aborted transaction、commit前後・close、current/previous鍵、100並行の実55P03と08006/未観測拒否canaryが成功 |

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,AuthenticationInboxCleanupTest,AuthenticationInboxInspectorTest,InboxDeletionBoundaryTest,InboxInspectionBoundaryTest,DatabaseMigrationTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。dev-foundation、未commit作業中、隔離PG18.6。Production capture/encodeでexpectedを生成しない。

BUG-084: production例外のredactionは維持し、testのtask-local JDBC probeが観測したSQLSTATE55P03だけを予定競合として許可する。08006または未観測で合格しない負canaryを追加し、全100future/connection close/SAVEPOINT0を確認。他のSQL競合testは生SQLSTATEをassert、既存認証並行はfuture失敗がそのままtest失敗なので非該当。未解決の全体障害を本件で完了にしない。

## 3. 実装・試験の追跡

- constructor/run/step invariantとcollection防御copy: PT035。NULL APIは契約違反、SQL必須NULLは固定の運用失敗。NPEを保護成功へcatchしない。
- 候補0/1/複数、canonical/owner/token/version/HMAC形式・known version、欠落/未知列、snapshot最大最小不正、参照整合: PT033～035/038。未検証行は保護WARNING。
- 正常Login0000/0101/0106、Logout0000/0200/0102の独立暗号wireから同一transaction削除、session/backup非更新、次回END: PT033。
- 候補・参照・backupを検査～DELETEまで保持し、外部SQL更新55P03。SAVEPOINT0/中間commit0、最後にcommit1/close1: PT036。
- open/autoCommit/prepare/bind/query/read/result close/statement close/health/delete/commit/rollback/connection close: PT037。失敗時rollback・close、cause/suppressed/SQL値非公開。commit後故障は削除済の可能性を隠さず固定例外・同run再実行END。
- 複数UUID順、保護→次の正常行削除、既削除再実行、別run/別日のbackup拒否: PT038。
- 同一row100並行の削除1、予定した55P03のみ許容・全結果回収: PT039。例外を一律合格にしない。
- current/previous両鍵とclosed鍵、結果toString非秘密、health誤値のrollback: PT040。process鍵のOS上の配置/rotation排他はoneshot側の残gate。

候補処理を単一returnへまとめ、候補0/1とも同じ資源終了境界を通す。分岐を除外したり到達不能と宣言したりせず、同じ実例外試験を全経路へ実行する。SQL自身の暗号証明ではなく、公開しない所有connectionと検査呼出し順序で保証する。

## 4. 正式gate・証跡

未確定。正式全回帰後にrun/source/環境/command/開始終了/exit/全Test ID/全6class coverage/関連BUG/hashを `evidence/authentication-cleanup/manifest.json` と本節へ固定する。
