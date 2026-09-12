# NK-BAT-001 cleanup_step値単体テスト仕様書

正式実行済: PT-WEB-20260913-08/sourcefbc121e2、対象PT-BAT-154～161全PASS。結果・独立期待値・coverage/環境/command/hashは対の027_NK-BAT-001_cleanup_step値_実行結果.mdを参照。以下の先行仕様・探索履歴は変更せず、未実装記述は起票時点の状態である。

PG164/SSC057（先行78bde51a）、OPS009/DAT009/UI251 §6・11・12/SS331 §3.14/332/341。初版はPG163正式07の凍結中に仕様のみ先行。現在はPG164の実装・選択探索試験まで実施、正式全reactorと同source証跡認定は未実施・認定0。既存V001～019/削除predicate/保持/Current baselineは変更しない。

| Test ID | class/method | 目的・事前条件/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-154 | CleanupStepValuesTest.kindStepMapping | 8既存kindのstep対応と非Log7 subset、progress2kind=CLEAN_BATCH_RUN・LOGS禁止 |
| PT-BAT-155 | CleanupStepValuesTest.successfulChunkContracts | OKの今回target=deleted/skip0・既知step累積>=今回、completeは0chunkのみ |
| PT-BAT-156 | CleanupStepValuesTest.rejectionAndDeferredContracts | LOCK_BUSY/BACKUP_GATEはunknown累積empty、FKはknown累積/0chunk/noncomplete、4reason組合せ固定 |
| PT-BAT-157 | CleanupStepValuesTest.summaryCountsAndCompletion | 保存step全体と今回差分の独立値、初回baselineと他kind累積・deferredは未完了 |
| PT-BAT-158 | CleanupStepValuesTest.counterOverflowAndBounds | 0/MAX/負/各成分不一致・退行・差分安全、返却累積を推測しない |
| PT-BAT-159 | CleanupStepValuesTest.nullAndRedaction | 全constructor/API要素null、optional null/empty、toStringのidentity/秘密値非出力 |
| PT-BAT-160 | CleanupStepValuesTest.immutableValues | 全accessor/value equals/hash/immutable所有、別identity不一致 |
| PT-BAT-161 | CleanupStepValuesTest.concurrentValues | 独立固定32～64threadで同immutable値を読取・別入力を混同しない |

Fixtureは隔離PG18.6/Flyway/JDBC42.7.13・公開literal run/handle/時刻/件数のみ。期待値はSSの固定SQL後条件/候補predicate/型・byte/手計算差分/固定JDBC呼出表で別途定め、Productionの出力・観測mapからexpectedを生成しない。正常/境界/異常/例外/NULL/未知/割込/再送/並行/commit不明を全分岐で網羅する。故障は修正前915、共通原因は916、設計修正はSSC057等へ先行する。

実行は421 JDK25.0.4/Maven3.9.12/M2を用いるoffline Mavenの該当module -am test/clean verify。対象commit/branch/command/日時/OS/tool/終了code/input/期待・実際/line・method・class・branch100%/static/BUG・SSC/証跡path・SHA256を027_NK-BAT-001_cleanup_step値_実行結果.mdとmanifestへ実行後記録する。failed/flaky/skipped/not-runは合格にしない。未実装の親OS/実子/実backup/通常Question/pending revoke・全cleanup順序を本部品の試験だけで完了にしない。

2026-09-13探索追記: 新値8、7kind/全invariant/NULL/MAX/64並行/独立値を選択実行でPASS。BUG179/180・YKT140/141は017/032で修正・全横展開を管理する。正式clean verify/38scope/30負canary/源commit・hashの確定前は部分成果へ加算しない。
