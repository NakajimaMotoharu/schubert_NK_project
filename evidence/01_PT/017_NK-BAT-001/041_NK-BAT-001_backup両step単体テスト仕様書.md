# NK-BAT-001 backup両step 単体テスト仕様書

SSC061先行26fb3bad、PG168。BAK/BKO/OPS009/DAT009/UI251/SS311・3318.3・3416.6・343。13b9931aで仕様先行後、ProductionとPT-BAT-210～217を並行実装。選択再試験は成功、全clean verify認定前のため認定加算0。独立14列/JDBC全出現位置・実trace・BUG191～194/YKT151～153の全対象は045を参照。

Production BackupStepRepositoryのconstructor/全public/private methodを対象に独立PTを並行実装する。manifestは公開合成fixture（PG165/166の3file bytes26/35/32と同一）。合成run/cutoff/2完全handleをfixtureとして明記し、期待値はProduction methodで生成せずliteral14列/SQL後条件/時刻を使用する。秘密credential/DB dump/実master/実manifest値はGitへ保存しない。

| Test ID | class/method | 目的・入力・操作・独立期待値 |
|---|---|---|
| PT-BAT-210 | BackupStepRepositoryTest.runningAndCommittedPair | 公開合成2行・両RUNNINGは空、両SUCCESSの同endedを返す。DB件数1/bytes26、CONFIG件数2/bytes67、failure0とNULL診断を独立SQL SELECTで確認。 |
| PT-BAT-211 | BackupStepRepositoryTest.fullHandleAndMissingRows | 全handle id/run/JSTday/step/attempt/startを各改変、0/1/3行・重複・逆id順を確認。where句をoracleにせず返却列も独立検証。 |
| PT-BAT-212 | BackupStepRepositoryTest.statusCounterAndTimeMatrix | RUNNING/SUCCESS/WARNING/FAILED/SKIPPED/未知の全対、14列null・count負/違い・ended差/µs/逆転/未来境界。両RUNNINGと共通end両SUCCESS以外拒否。 |
| PT-BAT-213 | BackupStepRepositoryTest.atomicPairAndReplay | complete両update同transaction、caller rollbackで両RUNNING復元。commit後再試行は旧end不変、新観測時刻で書換えない。片成功不補完。 |
| PT-BAT-214 | BackupStepRepositoryTest.databaseGuardsAndLocks | 自己advisory有無/他connection/identity不整合、autoCommit/readOnly/isolation、row lock競合・query timeout固定5秒。独立旧migration hash不変。 |
| PT-BAT-215 | BackupStepRepositoryTest.everyJdbcFault | 正常read/新complete/既SUCCESS再読それぞれのJDBC順と全出現回数を独立列挙し、全SQL/close位置の失敗で非成功・未commit・resource解放。 |
| PT-BAT-216 | BackupStepRepositoryTest.nullAndUnknownFailures | 全API null/Statement/ResultSet/14列nullの契約、未知Runtime/NPE/Error identity、既知SQL診断cause/suppressed除去、前後interrupt保持。 |
| PT-BAT-217 | BackupStepRepositoryTest.concurrentBindings | 独立connectionの同pair/別pair、DB lock直列化・同一end維持・別run不混入。fixture公知IDのみ、実PostgreSQLとfault portを分離。 |

全line/method/class/branch100%、NullAway/SpotBugs/Spotless・NULL/境界/例外/並行・全JDBC出現位置を確認する。安易な除外/無意味assert/同Productionによるexpectedは禁止。TDD最初の未実装以外の仕様違反は修正前915/共通916へ登録する。

実行環境は421のJDK25.0.4/Maven3.9.12/PostgreSQL18.6/JDBC42.7.13。選択Batch-am PTと全clean verifyを実行し、source commit/branch/日時/command/exit/input/expected/actual/4coverage/static/BUG/SSCを対応する実行結果とevidence/manifest.jsonへ記録する。試験仕様・actual sanitized trace・hashは020 collector/019独立negative canaryで検査する。

親root manifest生成/信頼reader、実fsync/atomic/backup/7世代・OS排他・全親/実NK CHR/IT/STは本部品から成功推定しない。借用Connectionは単独所有、失敗時caller破棄が必須。
