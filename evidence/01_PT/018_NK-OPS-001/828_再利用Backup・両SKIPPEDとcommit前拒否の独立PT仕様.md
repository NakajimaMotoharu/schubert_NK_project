# 再利用Backup・両SKIPPEDとcommit前拒否の独立PT仕様

PT-MDB-2780-001、NK-BAT-001、MorningDatabaseSession.Session.beginResumeBackup/mdb2780001ResumeRejectsEitherNonSkippedAttemptBeforeCommit。主担当WBS-P017-01、RD BAK/OPS009/DAT009、UI251/253、SS331/332/341/343/SSC116/134/451。実method974のDB/CONFIG skipped=false二条件・throw line969以降の別原因を着手前照合。開始.25/.75/2ppはevent0736固定。

隔離実PG/DDLs、二入力BACKUP_DB/BACKUP_CONFIG。固定run27800001/2051-02-09T15Z＋日差、原SUCCESS二行のtarget/success1/2・26/67bytes・終了+3秒を実SQLでseedし、literal manifestを構築。親同接続のsuccessfulBackup/manifest inspectは実原本を通し、Repo HISTORYの対象stepだけrun_idを別UUIDへ投影する（他値/原DB事実は変更なし）。これにより選ばれたstepの新attemptはRUNNING、他stepはSKIPPEDとして実transaction内にINSERTされるが、両SKIPPEDでないためRootはIOException/公開固定文言でcommit前に拒否。注入回数1/commit呼出0、親のrollback/close後に独立SQLが原二SUCCESS全列だけを確認し、新attempt0/client-advisory解放を確認。

不正なdriver境界を注入する独立negative testであり、正常なSKIPPED成功や本番所有を捏造しない。正常/再利用four-row後条件は既2754/全2770で保持。私有state reflection/Production expected生成0。Source042/PG2654/full2770/当native2774不変更、Test only。実command構築済PYTHONPATHで `python3 -B tools/quality/pg2780_resume_skip_history_selected.py`。初期未実行、source/XML/実counter/hash/結果は独立資格後に追補。全体への新Test統合/global100/正式加点0、Root/Backup/ADMIN/VM/stop/配備/reload0。
