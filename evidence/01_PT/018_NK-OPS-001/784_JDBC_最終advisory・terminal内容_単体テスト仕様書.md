# PG2486 JDBC 最終advisory・terminal内容

NK-OPS-001／MorningDatabaseSession.Session.observeBackup/retainedBackupSuccessful、SS343/353/354、SSC133/134。WBS-P017-01、N05参照費0、0642群予算1/3/7ppのsubsetで二重配賦0。PG2482二PTと新二PTを同じfresh隔離DB実行にまとめ、未網羅の最終advisory・実terminal内容を確認する。

PT-MDB2486-001／mdb2486001：正規committed FAILED二行を用意し、対象operation開始後の実JDBC advisory読取を数える。初回は実際の保持値、二回目だけfalseを返す。OBSERVE/RETENTION両者は最初のadmissionを最後へ流用せずIOExceptionで拒否する。読取はちょうど二回、Connection閉鎖・owner/advisory0、別SQLでFAILED二行/開始終了/count/error原値不変更を確認する。

PT-MDB2486-002／mdb2486002：FAILED二行の実readback境界で有効SUCCESS内容、+1秒終了、または正規IO_FAILURE理由を提示する。実DBのstatus/時刻/count/errorは改変しない（理由caseだけ最初から承認されたIO_FAILUREとしてcommit）。独立期待=COMMAND_FAILUREだけを既定失敗へ読み替えず、内容/終了時刻/理由の不一致を拒否、実SQL元値保持・Connection閉鎖・資源0。expectedは固定SQL後条件・literal診断allowlist・標準時刻加算から作成する。

継続回帰=PT-MDB2482-001/002の八case。実command=`python3 -B tools/quality/pg2486_backup_observation_selected.py`（固定PYTHONPATH）、fresh PG2486-selected-v1。JDK25.0.4/実PG18・Werror・四XML/FES/aborted/notRun0・全Main1643 CRC・PG2404 fixture/依存前後hash・PG2474最新九native・PG2478v4選択hashを確認。旧source native・VM業務操作・全体合格読み替え0。実結果/commit/coverage/証跡hashは取得後記録。
