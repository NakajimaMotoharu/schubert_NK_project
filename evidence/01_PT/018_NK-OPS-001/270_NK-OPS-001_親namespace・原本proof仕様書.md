# NK-OPS-001 親namespace・原本proof PT（PG380）

RD OPS-009/SYS-004/BAK-001、UI251/253、SS341§5.1・342§4.4・343§6.15、SSC109/BUG327/YKT259・BUG328/YKT260。範囲は同Morning→Backup所有経路のみ。正式run・工程完成率は更新しない。

| Test ID | class/method・目的・fixture/input | 操作・独立期待値 | 結果/証跡 |
|---|---|---|---|
| PT-OPS-MNAMESPACE001 | MaintenanceFileLock.tryExclusive/verifyCurrent。実保持inode/flock、独立host/private readonly flags | hostRW/private共有runROはcallback1、hostRO/appRO/fileRO/別inodeはcallback0。全FD close、外部flock再取得0、書込み0 | 271 |
| PT-OPS-MNAMESPACE002 | MaintenanceRunFiles.capture/verifyHostAncestors。同inodeのhostとprivate、独立flags | shared var/lib/appのprivateROだけ許容。hostRO/maintenanceRO/runsRO/attemptsRO/hostinode違いは原本callback0、publish/write0、全FDclose | 271 |
| PT-OPS-MNEW012 | MorningNewRunAdmission.executeVerified、同DB/原本callback | 固定run/activation/cutoffが渡りowner内proof1回。別thread/終了後/default未結線proofはIOException、proofを再resumeへ置換しない | 271 |
| PT-OPS-MUNIT002/003 | MorningServiceUnitTest、候補template | strict、固定3RW対象、root最小2CAP、ambient空・NNP・30分oneshot・SIGKILLなし。旧「RW0/CAP0」の内部候補oracleはSSC109により変更 | 271 |
| PT-OPS-MDB015 | MorningDatabaseSession completion/state | 同session両FAILED/readback/二重完了拒否。backupFinishedは既存共有boolean同様volatile、SpotBugs抑制0追加 | 271 |
| PT-OPS-MBACKUP001 | 実Morning→Stage.freshVerifiedEpoch→実Unit Cycle→artifact/DB→original/current/request/marker | 478の真正外部path、同一親budget/M/A/DB/Epoch。ホスト注入だけでは実経路PASSにしない。VM同source class hash・agentでcoverage採取 | 未実行 |

環境はhost JDK25.0.4/Maven3.9.12/Node24.19.0、隔離VM Ubuntu26.04/PG18。選択commandは固定JAVA_HOME/PATH/m2でBatch `clean test -Dtest=<271の対象> spotbugs:check jacoco:report`。stale execution data/class不一致reportは不採用。line/method/class/branch100%は実native entryを含む同source host/VM採取と全正式scopeが閉じるまで未達。failed/flaky/skipped/not-runを加算しない。

同原本証明は新一般frameworkではなく既存Session.observeCleanupのreadonly graph engineをSession.observe(expectedActivation)へ共用し、保持ownerの失効/再入/namespace guardを維持する。Main未結線のまま成功0/10は返さない。新Control/Stage native経路・全StopPass待ち・実archive・Expiry・issuerの外部網羅は後続。原本/DBdump/秘密/実tokenはGit外、metadata/hashのみ証跡化。
