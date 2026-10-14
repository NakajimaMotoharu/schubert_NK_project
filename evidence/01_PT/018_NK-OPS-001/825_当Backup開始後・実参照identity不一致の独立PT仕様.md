# 当Backup開始後・実参照identity不一致の独立PT仕様

PT-MDB-2762-001、NK-BAT-001、Session.recheckConsistent / MorningDatabaseSessionTest.mdb2762001PostBeginRejectsForeignRunAndActualLogCutoffDrift。主担当WBS-P017-01、RD DAT009/BAK/OPS009、UI251/253、SS331§3.12/332/341/343/SSC055/134/451。2748実method1035 run不一致と1049 DB参照identity falseを着手前照合、予算.25/.75/2ppはevent0731で固定。

隔離実PostgreSQL/DDLs、二入力FOREIGN_RUN/LOG_CUTOFF。固定run27620001/2050-04-09T15Z＋日差、FAILED DB/CONFIG各1-target1-success0-failure1-bytes0・終了+3秒を実commit後、正常recheck。foreign runは別UUID/同cutoffを渡しIOException。LOG_CUTOFFはadmin隔離fixtureが当runにcutoff+1秒・全count0・未完了の実log_cleanup_progressをINSERTし、V018実SQLがidentity=falseを返す結果としてIOException。JDBCprojection/私有field/Production expected生成なし。

独立SQLのFAILED二行全列・実log cutoff+1秒/count0/completed NULLが不変、connection/client/advisory解放。Main Source042/PG2654・full2744/保持当native2746v2不変更、Test only、VM/Root/Backup/ADMIN/stop/配置/reload0。実command構築済PYTHONPATHで `python3 -B tools/quality/pg2762_post_begin_identity_selected.py`。初期未実行・正式/global100加点0、source/XML/counter/hash/実終端結果は独立資格後に追補。
