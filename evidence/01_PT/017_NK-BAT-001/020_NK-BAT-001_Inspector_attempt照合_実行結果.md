# NK-BAT-001 Inspector_attempt照合実行結果

PG162探索成功（未commit候補、正式認定0）。explore1: 2026-09-13 04:00:48 JST終了/11.343秒/exit0、pure8/Storage8成功。explore2でも回帰。手計算累積/差分/MAX・0/10・END不変・64並行を確認。 JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13、421環境。raw /tmp/pgpt-parent-summary-explore1～3.log、commandはoffline Mavenの該当module -am -Dtest指定test（全正式runとは別）。探索JaCoCo新規3class/11method/74line/40branch missed0、01925＋0171負canary成功。BUG新規発見なし。全reactor/静的解析/37scope/hashは正式run05後に認定する。

PG162/SSC049、PT-BAT-122～129。未実装・未実行・正式認定0。対象commit/環境/command/日時/exit/coverage/期待・実結果/BUG/evidence hashは実行後に記録する。親工程・PGPT完了へ算入しない。
