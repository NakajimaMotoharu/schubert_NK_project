# NK-DAT-001 原子cleanup_step単体テスト仕様書

PG164/SSC057（先行78bde51a）、OPS009/DAT009/UI251 §6・11・12/SS331 §3.14/332 §11/341 §7.2。初版はPG163正式07の凍結中に仕様のみ先行。現在はPG164の実装・選択探索試験まで実施、正式全reactorと同source証跡認定は未実施・認定0。既存V001～019/削除predicate/保持/Current baselineは変更しない。

| Test ID | class/method | 目的・事前条件/入力/操作・独立期待値 |
|---|---|---|
| PT-DB-INBOX-259 | StepCleanupBoundaryTest.sevenKindAtomicCounts | 隔離実PGの全7kindでDELETEとRUNNING step target/success加算、0/1/1000/1001・同step複数kindの保存累積を独立SQL確認 |
| PT-DB-INBOX-260 | StepCleanupBoundaryTest.handleArgumentsAndIdentity | 7引数のNULL/unknown/UTC0001～9999/µs/step id・attempt・started/JST日付・run/terminalの全不一致を保全拒否 |
| PT-DB-INBOX-261 | StepCleanupBoundaryTest.backupLockAndRoleBoundary | 自己DB exclusive/backup2成功・当日/最新/rowlock、step NOWAIT・別role/PUBLIC・gate時unknown累積NULL |
| PT-DB-INBOX-262 | StepCleanupBoundaryTest.zeroChunkLockedRemainder | 各7kind/構成tableの唯一対象を別TX lockし旧chunk0でも新wrapper非complete/LOCK_BUSY、解除後同対象だけ削除し0END |
| PT-DB-INBOX-263 | StepCleanupBoundaryTest.retentionAndProtectedRows | 各現行predicateの±1µs/NULL/active/lease/通知存在/同run/RUNNING・FAILED調査保護を保持し、保護だけは削除候補0 |
| PT-DB-INBOX-264 | StepCleanupBoundaryTest.rollbackOverflowAndForeignKey | DELETE＋step加算rollback、long上限overflow時削除も復元、QUESTIONS FK23503だけdeferred/旧累積保持・他kind異常伝播 |
| PT-DB-INBOX-265 | StepCleanupBoundaryTest.typedProjectionAndNoBypass | 7列SQL型/optional累積、固定kind→既存関数/step対応、他table/Inbox/Log/diagnostic非変更、unknownを0補完しない |
| PT-DB-INBOX-266 | StepCleanupBoundaryTest.appendOnlyMigrationInventory | V001～019 checksum不変、V020/type SQL全20・SCHEMA1/再migration0、全既存inventory/権限・table数不変 |

Fixtureは隔離PG18.6/Flyway/JDBC42.7.13・公開literal run/handle/時刻/件数のみ。期待値はSSの固定SQL後条件/候補predicate/型・byte/手計算差分/固定JDBC呼出表で別途定め、Productionの出力・観測mapからexpectedを生成しない。正常/境界/異常/例外/NULL/未知/割込/再送/並行/commit不明を全分岐で網羅する。故障は修正前915、共通原因は916、設計修正はSSC057等へ先行する。

実行は421 JDK25.0.4/Maven3.9.12/M2を用いるoffline Mavenの該当module -am test/clean verify。対象commit/branch/command/日時/OS/tool/終了code/input/期待・実際/line・method・class・branch100%/static/BUG・SSC/証跡path・SHA256を063_NK-DAT-001_原子cleanup_step_実行結果.mdとmanifestへ実行後記録する。failed/flaky/skipped/not-runは合格にしない。未実装の親OS/実子/実backup/通常Question/pending revoke・全cleanup順序を本部品の試験だけで完了にしない。

2026-09-13探索追記: SQL8、17predicate代替×3境界・全7kind/10table/typed7列/NULL/FK/rollback/20inventoryを選択実行でPASS。BUG179/180・YKT140/141は017/032で修正・全横展開を管理する。正式clean verify/38scope/30負canary/源commit・hashの確定前は部分成果へ加算しない。
