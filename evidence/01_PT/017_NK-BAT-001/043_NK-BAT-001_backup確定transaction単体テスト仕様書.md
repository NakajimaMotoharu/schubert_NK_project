# NK-BAT-001 backup確定transaction 単体テスト仕様書

SSC061先行26fb3bad、PG168。BAK/BKO/OPS009/DAT009/UI251/SS311・3318.3・3416.6・343。13b9931aで仕様先行後、ProductionとPT-BAT-218～225を並行実装。選択再試験は成功、全clean verify認定前のため認定加算0。独立14列/JDBC全出現位置・実trace・BUG191～194/YKT151～153の全対象は045を参照。

Production BackupCommitServiceのconstructor/全public/private methodを対象に独立PTを並行実装する。manifestは公開合成fixture（PG165/166の3file bytes26/35/32と同一）。合成run/cutoff/2完全handleをfixtureとして明記し、期待値はProduction methodで生成せずliteral14列/SQL後条件/時刻を使用する。秘密credential/DB dump/実master/実manifest値はGitへ保存しない。

| Test ID | class/method | 目的・入力・操作・独立期待値 |
|---|---|---|
| PT-BAT-218 | BackupCommitServiceTest.commitAndExistingReceipt | 入口autoCommittrue→false→2step確認/確定→commit→trueの所有順。返却は実DB共通end、再試行は保存旧end、独立literal14列後条件。 |
| PT-BAT-219 | BackupCommitServiceTest.rollbackBothSteps | 1段目成功後2段目失敗を注入、rollbackで両RUNNING/count0、rollback成功前にautocommit復元禁止。既存他run/旧SUCCESS不変更。 |
| PT-BAT-220 | BackupCommitServiceTest.uncertainCommitReplay | commit前失敗/実commit後例外を分離、今回非成功・次接続同manifest再読で0件新更新。保存end/counter二重加算なし。 |
| PT-BAT-221 | BackupCommitServiceTest.connectionContract | 全parameter null、closed/readOnly/autoCommit/isolation違反、時計µs/範囲/contentFinished前を非成功。未開始のDB変更なし。 |
| PT-BAT-222 | BackupCommitServiceTest.everyBoundaryFailure | 全connection/JDBC/resource境界SQL fault、rollback自体/restore自体/commit後restore失敗。接続の所有closeなし・失敗後破棄要求。 |
| PT-BAT-223 | BackupCommitServiceTest.interruptionAfterCommit | 入口・setFalse・各read/update/commit/復元・最終返却境界のinterrupt、flag保持、commit後なら保存両行を消さず今回の成功返却は拒否。 |
| PT-BAT-224 | BackupCommitServiceTest.unknownPrimaryAndCleanup | primary Runtime/NPE/Errorとrollback/restore SQLの複合、primary同一・固定suppressed・raw診断なし。NullPointerExceptionを成功に変換禁止。 |
| PT-BAT-225 | BackupCommitServiceTest.independentConnections | 異なるconnectionの並行service実行、同一connection共有は契約外。新/旧pair非干渉、全owned statement/row閉鎖。 |

全line/method/class/branch100%、NullAway/SpotBugs/Spotless・NULL/境界/例外/並行・全JDBC出現位置を確認する。安易な除外/無意味assert/同Productionによるexpectedは禁止。TDD最初の未実装以外の仕様違反は修正前915/共通916へ登録する。

実行環境は421のJDK25.0.4/Maven3.9.12/PostgreSQL18.6/JDBC42.7.13。選択Batch-am PTと全clean verifyを実行し、source commit/branch/日時/command/exit/input/expected/actual/4coverage/static/BUG/SSCを対応する実行結果とevidence/manifest.jsonへ記録する。試験仕様・actual sanitized trace・hashは020 collector/019独立negative canaryで検査する。

親root manifest生成/信頼reader、実fsync/atomic/backup/7世代・OS排他・全親/実NK CHR/IT/STは本部品から成功推定しない。借用Connectionは単独所有、失敗時caller破棄が必須。
