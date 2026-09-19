# NK-BAT-001 CleanupRepository資源横展開仕様

PG180/SSC063/BUG195・206/YKT154・162、2026-09-20。DAT009/OPS009/UI251/SS331§3.3・3.9/332/341。対象CleanupRepository.execute/readLogProgress/countsとowned Statement/ResultSet、共通JdbcResourceFailuresは060の契約を再利用する。未実装・未認定。

既存BAT012 jdbcFailuresRemainRedactedへ、2method×2resource境界×34=136複合を追加する。各34は060の独立5×5/同一未知4/body成功closeのみ5。getter/provider IAE単独と同一unknown body/closeの反例を先行する。全17既存PT（8kind allowlist、limit全境界、null、不正counts/reason/complete、lock/backup/role、UTC、削除/保持/rollback、resource所有）も再実行する。

Fixtureは実PG18の空Log/公開固定run/当日backup2行。progress読取の反例では同じ借用transactionで先に実Log cleanupを実行して進捗を用意し、未作成状態のエラーへすり替えない。probeは対象SQLだけの公開JDBCを監視し実close後に例外を注入。取得済row/statement各1回、未取得0回、live数0、Connection commit/rollback/close/config変更0。caller rollback後に別admin接続からlog_cleanup_progress0とLog0を確認する。暗黙commit/偽の成功を許さない。

JDBC resourceのnonnull契約違反（null Statement/ResultSet）は既存NPE非正常化契約を保ち、Objects.requireNonNullの取得境界で固定message `JDBC statement`/`JDBC result` により明示拒否する。SQL columnのNULLを固定DB不正として扱う規則とは区別する。未取得resourceはcloseしない。4つのnull resource反例でも取得済みだけcloseし、借用Connectionを破棄・rollbackするのはcallerとする。NPEをcatchして正常結果へ変換しない。

不正projectionは固定BatchRepositoryException/message/causeなし/suppressed0。未知primaryは元identity＋固定secondaryのみ、known SQL primary＋unknown closeはclose identity。期待は独立例外表とSQL後条件、同Production methodからexpected生成禁止。IAE捕捉はpure値構築/enum parseに限定し、JDBC getterのunknownを捕捉しない。null/範囲入力は元境界拒否、未知例外を正常/空/0へ変換しない。

選択commandは060にCleanupRepositoryTestを追加し、既定JDK25.0.4/Maven3.9.12/M2で実行する。全変更classのline/method/class/branch100%、NullAway/Enforcer/Spotless/SpotBugs成功、抑止/除外なし、failed/error/skipped0、続いて単一clean verify/46負canary/38scope。実行日時/OS/tool/commit/command/exit/期待実際/coverage・hashは063と正式manifestへ記録する。

新JUnit/部分成果加算0。BUG195/YKT154/SSC063、YKT162の広域候補は完了しない。実parent/backup/全cleanup/PGPT/IT/STの完了でもない。
