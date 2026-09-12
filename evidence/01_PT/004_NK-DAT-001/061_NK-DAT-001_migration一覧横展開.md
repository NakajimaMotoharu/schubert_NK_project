# migration一覧横展開

是正後探索4: 2026-09-13 04:17:11 JST終了/1分02秒/exit0、上記全13classのAPI121件＋Protocol/Storage選択PT成功、failed/error/skipped0。全13classが独立MigrationInventoryを参照し、DB258が固定19要素・文字列・不変性/旧18不一致を別literalで検証する。歴史hashと列/権限/後条件は不変。raw /tmp/pgpt-parent-summary-explore4.log。正式全module・37scope/26負canaryの再試験までは完了を保留。以下の未修正表現は起票時点の履歴。

BUG175/YKT136、先行b3ba65db、PG162/V019。正式05は非成功・未認定。修正前の期待値18が実19に対して失敗したもので、DDLや既存migrationを期待値へ合わせて変更しない。

初回起票の「旧11class」は棚卸し前の仮値で、実際は旧12＋新1＝13class。改行された件数assertも含む全grepと、各SQL後条件を確認した。

| 全対象class | 期待値形式と対応 |
|---|---|
| DatabaseMigrationTest | 明示version一覧、migration件数、resource一覧。V019 sourceを追跡 |
| RunReferenceBoundaryTest | version連結、file総数、旧17固定hashを維持 |
| CleanupSafetyBoundaryTest | version連結と再migration0 |
| InboxInspectionProgressBoundaryTest | 明示version一覧、再migration0 |
| LogCleanupProgressBoundaryTest | version連結 |
| QuestionQueryInboxCleanupTest | version連結 |
| InboxInspectionBoundaryTest | SQL count、旧hash・再migration0を維持 |
| InboxDeletionBoundaryTest | SQL count、旧hash・再migration0を維持 |
| InboxMaintenanceBoundaryTest | SQL count、旧9hash・再migration0を維持 |
| QuestionMutationInboxInspectorTest | SQL count、23業務table件数は変更しない |
| OutboxCleanupBoundaryTest | SQL count、再migration0 |
| BackupRerunBoundaryTest | SQL count、owner/旧migration・再実行 |
| InspectionParentBoundaryTest | 新DB258、旧18固定hash・全19件一覧と再migration0 |

同じ承認済み期待versionのtest-only MigrationInventoryを用い、固定一覧をProduction file/DB/実件数から生成しない。count/連結文字列はこの独立期待一覧から得る。各historical hash・permission・列・DML後条件は個別oracleを維持する。JDBC/Outbox fixtureのflyway_schema_history権限付与は現在一覧のassertではないため変更不要。PG18というtoolversion、業務18件、旧checksum17/18は別の意味なので一括置換しない。

再発防止: DB258で共有期待一覧の独立19要素を明示検証し、旧18が一致しないこと、immutableを確認。13全対象の期待一覧参照・個別後条件と全reactorを実行し、source/日時/command/結果/coverage/証跡hashを060と正式parent-summary manifestへ記録する。現時点は未修正・再試験待ち。
