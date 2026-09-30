# NK-OPS-001 Cold Backup／同run request再使用 PT

関連: OPS009/BAK001/BKO001/UI251、SS341/342/343、SSC113/112、BUG344/345/YKT274/275。Production: BackupUnitReceiptGate.stateProjection/capture/observe、BackupWorkerRequestFiles.prepareResume、MorningBackupRequestPublication.create/openNative、MorningBackupStage.verifiedEpoch。

BGATE010: 独立18field ASCII/LF vectorでloaded/inactive/dead/PID0/空Invocationを与え、process-list callbackを呼ぶとAssertionErrorとなるfixtureでcold projectionは呼出0と確認。captureは別kernel terminal1回・manager前後2回、kernel不明なら拒否、runningはempty、not-found/未知状態は固定非成功、null拒否。既存BGATE001～009/BackupUnitTerminationのpresent/absent/nested/proc/ABA/close failureを回帰。必要状態だけでkernel成功を生成しない。

BREQFILE009: synthetic root0600/link1/tmpfs/ACL0 fixtureで不存在→literal NKBACKUP1公開、同request明示resume→全byte・ino/ctime/size/mtime不変・publish回数不増・新part不存在。異run/異cutoff/ACL/nullは拒否し元request維持。fresh collisionは既存試験を維持。不明をMISSINGへ補完しない。scope外の同owner/全8終端はhost fixtureだけで証明せず、実外部Morningで別実測。

期待値は固定vector・独立Files属性・callback回数・SQL後条件で作成。Production methodでexpectedを生成しない。境界/未知/失敗/並行/再送は既存request/receipt/full-terminal suiteと合わせる。selected実行: JDK25.0.4/Maven3.9.12/JaCoCo0.8.15、offline固定m2、Bootstrap+Batch同reactor `clean test spotbugs:check`、test=ReleasePayloadVerificationTest,BackupUnitReceiptGateTest,BackupWorkerRequestFilesTest,MorningBackupRequestPublicationTest,MorningBackupStageTest,MorningBackupPreparationTest。各module1件以上実行、skip不算入。2026-09-30 11:06:50 JST、49PT F/E/S0/static各0。sourceは本仕様と同commit固定後全6回帰する。途中format/古いM2 Bootstrap単独compile拒否は合格不算入、pg384-selected/selected2.logへ保存。

Native: fixed署名/RO fullBOM、V023実Flyway成功、新approval/current再読済。PG383外部Morning Invocation00c050c4d1134eda9af6dee5420fde38は実両begin/request公開後cold query拒否exit30、worker起動0。same-source parent.execを保存し到達行を照合、未実行をFAILED/SKIPPEDへ代用しない。修正候補で同原本resume・実worker fresh Invocation・dump/config/age/MANIFEST・同owner両SUCCESS/独立DB再読・request/intent退役を確認する（まだNOT-RUN）。known FAILED/UNKNOWN/timeout/resume・native全分岐/正式100%は別必須で未認定。
