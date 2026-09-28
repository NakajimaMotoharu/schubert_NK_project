# 176 NK-OPS-001 Cleanup親DB引渡し単体テスト仕様書

Program ID: NK-OPS-001/NK-BAT-001。対象は `RootStartupContext.Service.CLEANUP`/`capture`/`recheck` と `MorningDatabaseSession.Session` の `beginBackup`/`handoffCleanup`/`requireUnused`。RD OPS-009/BAK-001、UI251、SS341 §3/7・342 §4・343 §6、SSC-104。新規 Test ID は PT-OPS-ROOTCTX009、PT-OPS-MDB009～012。既存 ROOTCTX001～008/MDB001～008/InspectorLockHandoff PT030～037も回帰対象とする。

前提: root contextは `RootStartupContextTest` の固定ASCII `/proc`・systemd Unit literal fixtureを用い、Productionの `Service.unit()` から期待文字列を作らない。DBはTestcontainers相当の既存 `BatchDatabaseFixture` 上で実PostgreSQLを作り、provisioning/Flywayを適用する。親と子は別Connection、`schubert_batch` role、独立observerは別Connectionとする。合成fixtureのschema callbackは真のrelease承認を発行せず、実本番のBOM/原本/backup現物を満たしたとは扱わない。

| Test ID | 入力・操作 | 独立期待値・根拠 |
|---|---|---|
| ROOTCTX009 | literal `schubert-nk-cleanup.service`/自己PID42/固定CG/Invocationの二重観測・recheck。親Morning/APIの同観測、MainPID変造 | 自分自身のCleanupだけ受理、他Unit・変造は固定IOException。SS342の固定Unit名とsystemd 7 property、kernel CG literalから独立算出 |
| MDB009 | 未commit時handoff、null callback | 子callback0、固定IOExceptionまたはnull契約NPE。SS341の両backup begin commit前はlock貸出不可 |
| MDB010 | 実DBで両backup begin同transaction commit→別子Connectionがadvisory 71419602取得→子close→親再取得。callback中再入、別thread、再送、2回目begin | 子保有中observer取得false、帰還後親保有中false、親終了後true。再入/別thread/二重handoff/二重beginは拒否。PostgreSQL `pg_try_advisory_lock` の独立後条件 |
| MDB011 | 実DBの子callbackがIOException、親scope close | 成功値を返さず固定IOException、callback1回、親終了後observer取得true。未知子終端を成功扱いにしない |
| MDB012 | 実Connection proxyがcommit後のautoCommit状態をfalseと報告 | 子callback0、固定IOException、親Connection close。driver状態不明をlock貸出へ昇格しない |

実行: Linux/JDK25.0.4/Maven3.9.12、`-pl :schubert-nk-batch -am -Dtest=ResourceScopeTest,ReleaseApprovalTest,RootStartupContextTest,MorningDatabaseSessionTest,InspectorLockHandoffTest test ...spotbugs:check` とJaCoCo report。security境界に触れるため、Production6moduleのclean全PT/静的解析/coverageも451/471に従って別途実行する。実行日時、branch、対象source hash、input/expected/actual、F/E/S、四指標、BUG-309/YKT-242、manifest/evidence hashは177へ保存する。全条件・例外/NULL/再送/並行は上記と既存8+8+8 Test IDの合成negativeを合わせて評価し、外部Cleanup Unit/実削除・Artemis起動/CHRには算入しない。
