# NK-DAT-001 認証Inbox条件付き削除実行結果

## 1. 対象・現在状態

PG-D-122、V009、009仕様PT-DB-INBOX-025～032。新規の条件付き削除SQLで、既存V001～008は不変更。探索成功、正式全回帰・証跡未確定。SQLは暗号検証を行わず、Java接続・全layout・oneshot・BUG-014全体は未完了。

## 2. 探索履歴・障害

| 実行・終了日時JST | 結果 | 根拠と対応 |
|---|---|---|
| session48557 / 2026-09-09 08:43:36 | API31件中1failure/1error、skip0、exit1 | PT030: 存在しないWeb/ops role名、PT031: revokedだけ更新する不正fixtureでexpected55P03/actual23514。BUG-081/082・YKT-072/073を134269abで修正前起票 |
| session70100 / 08:45:44 | API31件中1failure、error/skip0、exit1 | PT031: UUID(0,104)と文字列末尾104の十進/十六進不一致で参照欠落。lock期待に対して例外なし。BUG-083/YKT-074をf283372eで修正前起票 |
| session34103 / 08:47:12 | 新SQL8・既存候補8・既存DB15の31件PASS、Protocol5/Storage16もPASS、exit0 | role実在と実connection拒否、失効複合条件、session参照JOIN1を事前assertしてlock前後/解放後を再試験 |

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,InboxDeletionBoundaryTest,InboxInspectionBoundaryTest,DatabaseMigrationTest test`。branch dev-foundation、未commit V009作業中。実credential・平文・dumpを保存しない。期待値をコード都合で変更せず、正本role/制約/UUIDへfixtureを一致させた。

## 3. SQL全条件matrix・横展開

- 引数の各NULL、±infinity、transaction ID format/1～20桁境界、hash長・不一致、別/終了済transaction: PT026/028。
- Backup無し/片方/両方/別run/別日/FAILED/ended欠落、advisory競合、backup確認途中のSUCCESS追加をPT029（同じlocked snapshotだけで合否判定）。YKT-071のV009追加対象も再発防止試験する。
- WHERE: Message・暗号文hash・LGN/LOG pair・両version・PROCESSING/正常/error・NONE/AUTH_SESSION/他参照・owner/token・日時finite/order・168h±1µs/等号・cutoff±1µs/等号をPT025～028/031。owner/token/不正参照/created>completedは実CHECK拒否23514も確認。SQLが検証できないAES/refはJava gateへ残す。
- RETURN: DELETE1/0/既削除、rollback復元・commit確定・再実行をPT025。session/backup/userは非更新。
- 権限/catalog/PUBLIC/service role/任意DML/SET ROLEをPT030。V008/001の既存正本roleも照合（YKT-072）。
- 競合: 正しいFK参照JOIN1を前提に候補・参照・backupの更新が削除前後55P03、rollback後更新成功をPT031（YKT-073/074）。SQL単体によるSAVEPOINT暗号証明は主張しない。
- Migration新規/同時9件、全001～009/再適用0、resource10file、旧8migration不変、既存DB15をPT032/DB001/013/015で照合。

## 4. 正式証跡

正式run/source/環境/command/時刻/終了code/全回帰/SQL matrix/関連BUG/hashは全体gate成功後、`evidence/deletion-sql/manifest.json`と本節へ確定する。未実行/failed/skipped/flakyは合格に算入しない。
