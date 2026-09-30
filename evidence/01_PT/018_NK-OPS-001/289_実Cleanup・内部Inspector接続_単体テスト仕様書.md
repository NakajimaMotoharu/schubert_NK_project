# 289 実Cleanup・内部Inspector接続（実装前）

PG390実caller追加host PT：CleanupMaintenanceWorkTestの3観点は実PG/独立fixture（sequence90020開始）で通知1/質問1/session3/Outbox2/Log0/history3/Transfer2file5byte、current IDs90021～90027、2回目90028～90034のSKIP全0と元SUCCESS不変を検証する。Inspector累積11/9/2・今回delta1/0/1を分離し、今回Inbox/Outboxはtarget3/success2/failure0/PROTECTEDとする。OUTBOX commit全列読戻しを環境退役より先に確認し、callback欠落/二重・親期限前失敗では未実行stepを補完しない。CleanupTerminalRepositoryTestの3観点は手書き全14列/7row（IDs1000～1006）から順序・不変Snapshot・0/10を独立確認し、欠落/RUNNING/FAILED/未知code/summary不一致・null・未知例外を拒否する。MorningProcessMainTest MMAIN009はactual archive完了前/失敗後/異thread/二重完了を拒否し、同callback成功後だけ実Manifestを保持する。CleanupProcessMainTestはnative noargsの実結果0/10/30だけを伝え、未知値/既知拒否は30、未知例外は正常化しない。CleanupServiceUnitTestは固定3credential、SuccessExitStatus=10、限定3RW pathを手書きliteralで照合する。以上はhost接続試験であり、外部Unit/専用credential/全終端の代用ではない。

PG390追加host観点（SSC119）：COWNERFILE001/002は固定NKMAINTOWNER1の手書きliteralから親/Inspector専用file名、profile違反、new-only衝突、異claim退役拒否、全IO故障位置/closeを検証する。RBCR013は専用private copy名/最大1024/不正codec/欠落を独立literalで試験。MGUARD001..003は実PGで残1.999/2.999/5.999/30秒→1/2/5/5sとtransaction-local終了後role元設定30minを検証し、不正返値/null/未知例外も拒否する。Step guardの独立1～10境界（9/10だけ既commit）、Logの1～9境界（8/9だけ既commit）で保存行とcommit/rollbackを確認し、期限後をrollback済と表記しない。BUG363境界3は開始前なのでrollback0、TIME_LIMIT。native共通期限/実Unit/PT全coverageは別未完条件。

Program NK-OPS-001/NK-BAT-001/NK-DAT-001。CleanupProcessMain、CleanupDatabaseSession、InspectorLockHandoff、InspectorEnvironmentFiles、固定Unit engine、InspectionSummaryRepository、InspectionAttempt、StepCleanupService/LogCleanupService/TransferCleanup。RD OPS009/BAK001/DAT009、UI251、SS331/341§7/343、QA046回答済、SSC119/117/118。

PT-OPS-CEXEC001：真正Morning M/A/原本/boot/Epoch/親budget・実Backup成果のfixtureを用い外部Mainから一度Cleanupを起動する。child専用schubert_batch/advisory取得、通知→質問→session→Inbox/Outbox→Log→BatchRun→Transferの固定順。全terminal rowは実DB commit後の独立SQL全列と比較する。BEGIN/未実行をSUCCESS/SKIPPEDとして補完しない。

PT-OPS-CINSPECT001..004：同run before summary→Root所有固定環境→new-only Inspector intent→Cleanup advisory解除→専用role/鍵の真正Inspector Invocation→正常0/10/全kernel空→明示stop/全終端→Cleanup advisory再取得→同run ENDとreceipt/全累積独立照合→環境/intent退役。異run/旧Invocation/残process/signal/GC欠落/manager故障/再取得不明を成功にしない。HTTP/JMS consumer生成0、Cleanupへ鍵供給0、Outbox DELETE前に真正END必須。累積/今回差分の期待は手書きSQLfixtureで算出する。

PT-OPS-COWNER001..004：親の同boot/Invocation/PID/start/deadline/current INVALID/原本/activationが一貫していることを削除前後に観測する。親死亡・deadline境界・未知読取・交換時は以後DELETE/許可発行0、未知childはcallback通常復帰禁止/marker保全。child起動で30分budgetを再開始しない。

PT-OPS-CEXEC002：Backup実FAILED両handle/固定COMMAND_FAILURE全列/正常非0 typed receiptを独立再読した場合のみ、6削除stepをBACKUP_UNAVAILABLE/SKIPPED全0で実commit/readback。DELETE/Inspector0、Transferは実実行。未試行BackupをFAILEDに偽装しない。

PT-OPS-CEXEC003：Cleanup正常0/10/active-exited・全kernel空を保持したまま真正Artemisを起動する。CleanupのInvocation/開始終了時刻/step row全列/試行数が不変で、Requiresにより2回実行されない。次回Morningでは正規停止後に新Invocationとなる。

実行環境：隔離Ubuntu26.04/PostgreSQL18.6/Artemis2.56/JDK25.0.4のPG/PT VM及びhost。Source固定commit/full6回帰/同byte JaCoCo native採取、Test IDとmanifest hashを290の結果へ記録予定。現時点NOT-RUN、未実装/未検証を工程合格に算入しない。全4coverage100%、negative/static0、親hard-timeout実証は別未完条件として明示する。
