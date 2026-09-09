# NK-OPS-001 検査起動wrapper・unit 実行結果

2026-09-09 最新確定: dev-foundation/source20af737d、正式PT-WEB-20260909-42（19:47:16～19:54:18 JST）、全1075件（Protocol80/Storage50/API634/Web241/Batch29/CHR41）PASS、failed/error/skipped0。6 Java moduleのline/method/class/branch100%、Production5 moduleのSpotBugs0/NullAway・Enforcer・Spotless PASS（CHR runnerのSpotBugsは未設定）。12collector・35証跡scopeの同run/source/branch/hash/参照、017の1件・019の14件負canary成功。DB26部品240 PT＋batch2部品29 PT＋OPS2部品16 PT＝30部分成果285件確定。PG-D-146の実Linux flock8 PT（実コマンド双方向競合、32並行、FD/例外回収、inode差替え）を追加し、BUG140/YKT110を再試験完了。正式41はbranch1不足で不合格・後続3module未実行として保存。親root lockfile検証PG-D-147はSS/PT仕様のみ未合格。親inactive/実backup/DB引渡し/root設定publish・全cleanup監査・通常Question writer/replay・RERUN-001は残る。BUG-014/UIC-006/SSC-049/052継続、加重見積約4割（35～50%、456）、試験件数だけで加点しない。週間残18%。元dev-web Scenario3fileは保全・不算入、CHR41はrunner PTであり実NK互換gateではない。以下は履歴。

001/PT-OPS-INBOX-001～008、SS341/342/343/352・SSC-049/053/PG-D-144。実装・探索8 PT成功、正式全体回帰/独立scope/trace/hashが揃うまで合格に算入しない。19:00:57 JST合同探索3は20件成功。実systemd配布・親OS/backup gateは別未完了。

探索1（18:53:05）はSC2194 1件で19/20成功、BUG-136をdc8215d7で修正前起票。専用変数へ固定値を入れ、抑止なしで探索2（18:54:55）20件成功。NUL追加探索は壊れたreceiptをexit0としたため1失敗、BUG-137/SSC-053/YKT-107をe20a45f4で先行起票、SS937cb33c後に全byte hex検査へ修正。探索3でNUL16位置/高bit/余分LF/od失敗/JVM異常/実Java負例・ShellCheck0・baseと4profileのsystemd静的verify成功。失敗runは正式合格に算入しない。正式39予定。
