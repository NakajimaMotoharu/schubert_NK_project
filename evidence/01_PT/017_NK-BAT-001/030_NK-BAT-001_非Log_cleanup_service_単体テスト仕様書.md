# NK-BAT-001 非Log_cleanup_service単体テスト仕様書

PG164/SSC057（先行78bde51a）、OPS009/DAT009/UI251 §6・11・12/SS331 §3.14/332/341 §7.2。PG163正式07中はsource/collector変更禁止、現在は仕様のみ・未実装/未実行/認定0。既存V001～019/削除predicate/保持/Current baselineは変更しない。

| Test ID | class/method | 目的・事前条件/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-170 | StepCleanupServiceTest.allKindsCompleteAndPersistedCounts | 全7kindを実PGで0ENDまで、chunk後DELETE＋step件数同commit、終了時保存累積・元autoCommitを確認 |
| PT-BAT-171 | StepCleanupServiceTest.multiChunkResumeAndSharedStep | 1001→1000/1/0、既committed同handle再開・他kind初期累積・今回差分と全step値を独立確認 |
| PT-BAT-172 | StepCleanupServiceTest.lockBackupAndForeignKeyDeferral | 初回/途中gate失敗/ロック残件は未完了、QUESTIONS FKだけ保全deferred/非complete、未読値を補完しない |
| PT-BAT-173 | StepCleanupServiceTest.transactionFaultsAndUnknownCommit | 全JDBC/commit前・commit済応答不明/rollback失敗、未確定summaryなし・同handle再実行で保存累積再読 |
| PT-BAT-174 | StepCleanupServiceTest.timeoutInterruptAndClockWrap | 単調30分-1/just/plus・wrap/負経過、開始/各chunk/最終割込flag保持、途中END扱い禁止 |
| PT-BAT-175 | StepCleanupServiceTest.counterContinuityAndOverflow | before=保存累積-今回chunkの独立差分、後続退行/飛躍/MAX/保全理由・0complete整合、外部改変を補完しない |
| PT-BAT-176 | StepCleanupServiceTest.connectionStateRestorationAndNulls | autoCommit/RW/isolation/null/LOGS/skip、設定復元・rollback確定前の暗黙commit禁止/unknownruntime・Error後所有 |
| PT-BAT-177 | StepCleanupServiceTest.concurrencyAndIndependentTrace | 別connection/独立run・step/rowlock、同run既committed countsの単一読取、全7kindの実SQL traceと独立literal比較 |

Fixtureは隔離PG18.6/Flyway/JDBC42.7.13・公開literal run/handle/時刻/件数のみ。期待値はSSの固定SQL後条件/候補predicate/型・byte/手計算差分/固定JDBC呼出表で別途定め、Productionの出力・観測mapからexpectedを生成しない。正常/境界/異常/例外/NULL/未知/割込/再送/並行/commit不明を全分岐で網羅する。故障は修正前915、共通原因は916、設計修正はSSC057等へ先行する。

実行は421 JDK25.0.4/Maven3.9.12/M2を用いるoffline Mavenの該当module -am test/clean verify。対象commit/branch/command/日時/OS/tool/終了code/input/期待・実際/line・method・class・branch100%/static/BUG・SSC/証跡path・SHA256を031_NK-BAT-001_非Log_cleanup_service_実行結果.mdとmanifestへ実行後記録する。failed/flaky/skipped/not-runは合格にしない。未実装の親OS/実子/実backup/通常Question/pending revoke・全cleanup順序を本部品の試験だけで完了にしない。
