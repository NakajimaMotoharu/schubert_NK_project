# NK-DAT-001 認証Inbox検査削除service実行結果

最新正式判定: PT-WEB-20260909-20/sourcea389975b、2026-09-09 10:47:29 JST完了、全862件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/authentication-cleanup/manifest.jsonの現行SHA-256は `d66a1028748236a4cf15fa25cebff4557bad9e1661264723d942f3cde9a39b36`。8collector/16scopeの全hashとtrace負canary、V001～011/Current baseline不変、秘密pattern scanを確認。共通6classはline139/method14/class6/branch66全missed0。SQL条件は016/020 matrixに追跡。V011の通常batch迂回削除は廃止済み、BUG-091/YKT-082再試験完了。永続run/oneshot・Question/通知参照/横断監査は未完了、BUG-014/SSC-049継続。

以下は初回・探索・旧正式runの履歴。旧hashは証跡commit d98961c6等の該当履歴を参照し、現行manifestのhashと混同しない。未確定という旧記述は本段落の対象sliceに限って更新済み。

最新回帰PT-WEB-20260909-18/source56935aa0、2026-09-09 09:44:09 JST終了、全838件/全Java coverage100%/静的解析0、認証原子的削除8件再PASS。現在のauthentication-cleanup/manifest.json SHA-256は `7b590a35db42d0f989a7fb9bfdba9efd0883743000ddb41e7177114f0e6d6f89`。以下run17/hashは証跡commit b87c3c17の初回確定履歴であり最新manifestと区別する。

## 1. 対象・判定

011仕様/PT-DB-INBOX-033～040、AuthenticationInboxCleanup・内部Candidate・InspectionRun・InspectionStep/Outcome・InboxMaintenanceExceptionの6classを正式PT-WEB-20260909-17で確定。新6classのline130/method13/class6/branch66は全missed0、NullAway/format成功、SpotBugs0。BUG-084/YKT-075は再試験完了。非認証/oneshot/全run管理/V006置換は未完了。

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

正式PT-WEB-20260909-17/source7200d8d6、dev-foundation、2026-09-09 09:14:51 JST終了、exit0。全830件（Protocol80/Storage34/API434/Web241/CHR41）、failed/error/skipped0、全5moduleのline/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。8collector・12証跡scopeを収集しchecksum全一致、trace正負canary成功。baseline843de94/既存V001～009不変。CHR41はrunner PTで実NK互換gateではない。

`evidence/authentication-cleanup/manifest.json` SHA-256 `44b7d645366d476d1c5804592c919c814cf627147ac4845f93a1f87e75eedf0d`。OS/JDK/tool/command/開始終了/source、全PT033～040とmethodの一意対応、全6class個別coverage、独立expected/実結果、BUG/SSC、全体正式manifestへの存在/hash検証済リンクを保存。秘密情報・raw session/token/鍵/電文/DB dumpは保存しない。正常認証Inboxの削除接続の範囲だけが確定であり、工程/Program全体を完了にしない。
