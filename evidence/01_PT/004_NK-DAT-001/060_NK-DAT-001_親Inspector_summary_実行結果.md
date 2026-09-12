# NK-DAT-001 親Inspector_summary実行結果

正式05不合格: sourceeaba6b58、2026-09-13 04:09:03～04:14:58 JST、exit1。API652件中6failure（旧migration count18の更新漏れBUG175/YKT136）、Web/Batchはreactor未実行。PG162新SQL8は成功したが全正式認定には算入しない。先行b3ba65db起票後に旧12＋新1の13classを061で棚卸しし、独立test-only MigrationInventoryへ期待一覧を共用化する。V001～018/Production期待結果を修正する対応ではない。次正式run06でcleanから全再検証する。

PG162探索成功（未commit候補、正式認定0）。explore3: 2026-09-13 04:05:45 JST終了/20.559秒/exit0、SQL8＋旧参照10＋DDL15のAPI33件（Protocol/Storage選択PTも成功）。手書SQL・4列/権限/全table/index不変・18旧migration hash不変/再migration0を確認。 JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13、421環境。raw /tmp/pgpt-parent-summary-explore1～3.log、commandはoffline Mavenの該当module -am -Dtest指定test（全正式runとは別）。探索JaCoCo新規3class/11method/74line/40branch missed0、01925＋0171負canary成功。BUG新規発見なし。全reactor/静的解析/37scope/hashは正式run05後に認定する。

PG162/SSC049、PT-DB-INBOX-251～258。未実装・未実行・正式認定0。対象commit/環境/command/日時/exit/coverage/期待・実結果/BUG/evidence hashは実行後に記録する。親工程・PGPT完了へ算入しない。
