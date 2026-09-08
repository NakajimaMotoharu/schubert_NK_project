# NK-DAT-001 Inbox検査権限・候補lock実行結果

## 1. 対象・状態

007仕様PT-DB-INBOX-017～024、V008の検査用role/候補function。開発中で正式未確定、BUG-079/080とYKT-070/071は再試験待ち。各探索は新規隔離PGへ適用して終了時に停止する。未release V008の作業中是正であり、既存正本V001～007/既存本番DBのchecksumを書き換えない。

## 2. 修正前の実結果

| 日時・実行 | 実際結果 | 根拠/対応 |
|---|---|---|
| 2026-09-09 08:06:56 JST終了、session44311、dev-foundation未commit V008 | 新SQL8件PASS、既存DB15件中1 failure、exit1。Protocol5/Storage16成功 | 同時migration後のSQL件数oracleだけ7L残り、actual8。BUG-079/YKT-070をb9872e09で先行起票後8Lへ同期 |
| 08:11:46 JST終了、session3530、dev-foundation未commit V008 | 新SQL8件中1 failure、error/skipped0、exit1。PT021 expected55000/actualACCEPTED | BUG-080/YKT-071を90545e1aで先行起票。DB backup rowを別TXでlockし、検査queryのlock待ちをpg_blocking_pidsで観測、その後CONFIGをINSERT/commit。初回queryがlockしていないCONFIGを後段EXISTSが採用した |
| 08:13:45 JST終了、session17854、dev-foundation修正V008 | 新SQL8/認証参照8/既存DB15の31件成功、Protocol5/Storage16も成功、全failure/error/skipped0、exit0 | 新規適用/再適用/同時migrationと固定inventory8件、backup snapshot raceの55000と次TX正常、全role/row lockを確認。正式全回帰/収集は次段階 |

BUG-080修正前SQL SHA-256: `36da261d78007dfff0e3a2b60ec88236073c00255836dab5b8349ff48d2f269d`。実credential/暗号平文/DB dumpを使わず、時刻/SQLSTATE/件数だけを保存する。
再発防止は同一queryのFOR SHARE結果を集約したstep集合だけで両成功を判定すること。後段EXISTSを廃し、新しく完了したbackupは次のtransactionで取得する。例外を成功へ変換しない。最終削除を接続していないため実削除は0。

## 3. 分岐・横展開の対応

- 引数: run/cutoff NULL、±infinity、after NULL/既知/未知をPT018/019/023。
- Backup: 0行/片方/両方、state/date/run/ended不正、row更新lock、途中追加をPT018/021。
- 候補: expiry未到達/境界/超過、PROCESSING/COMPLETED/ERROR、LGN/LOG/他layout、1行上限/PK順/emptyをPT019/023。
- 参照: AUTH_SESSION存在/欠落/NONE、実独立暗号のJava認証検査と失効非更新をPT021。参照が無くてもSQLで架空sessionを作らない。
- 権限: role属性/列grant/禁止DML/DDL/SET ROLE/他schema/他roleからのEXECUTEをPT017/022。
- Transaction: Inbox/参照/backup row lock、advisory別session競合、rollback後解放をPT020/021/023。
- 既存migration: 新規/同時適用8件、再適用0、全8version/inventory9file、既存V001～007の差分0をPT024＋既存DB15件で再試験する。

V006等の既存6cleanupは新関数のlock済集合を再取得する形式を持たないためYKT-071の同形式修正対象外。既存Inbox誤削除保護を完了にする根拠にはせずBUG-014/YKT-012で継続。新SQLの候補/参照も実際にlockした値を使うことを確認し、検索だけで横展開完了にしない。

## 4. 再試験・証跡

部分探索command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,InboxInspectionBoundaryTest,DatabaseMigrationTest,AuthenticationInboxInspectorTest test`。正式commandは007。正式run/source/終了code/SQL matrix/環境/全回帰・hashを検証後に本節へ固定する。現時点では未合格分を全体へ加算しない。
