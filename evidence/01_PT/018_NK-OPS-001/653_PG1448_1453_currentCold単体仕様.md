# PG1448～1453 current cold所有・有限準備の限定仕様

Program NK-OPS-001、tools pg1448_current_cold_owner/pg1450_current_cold_retry/pg1453_current_cold_post、関連RD運用・互換要件/UI変更なし/SS343353 SSC264265、451425、BUG1102～1103/YKT871872。Production source769ddb15cd735c25fef581b5f9850ef9d0053c0f、releasePG1292/schema028、boot3d69。環境資格・回収だけでPGPT/ITST又はProduction coverageを完了扱いしない。

| Test ID | 入力・操作・前提 | 独立期待値・根拠 | 結果の対応 |
|---|---|---|---|
| PT-ENV-COLD-OWNER-001 | 新observer静的AST namespace/null/未知mode・link追随9metadata | 手書9値/Name対exec固定3件。設定literal SendSIGKILLと実Callを区別。SIGKILL/任意PID操作なし | owner2test、prefix4、BUG1103旧error保持 |
| PT-ENV-COLD-OWNER-002 | 当3323/ticks388541/argv固定、全authority/task/child/FD、socket26546/port56616→DB3344、専用M-A/class113の全二読 | 固定exe/boot/cgroup/UID-GID/cap、peer3344専用batchPG243-cold-empty/他client0、署名hashと1440封印・原24DBを全比較。DB heartbeat active/idleとsocket queue/timerだけ動的、固定address/UID/state/inodeは比較 | PG1448/1449 private before、safehash |
| PT-ENV-COLD-OWNER-003 | 正規qualified proof後本人pidfd→耐久new-onlyTERM予約→予約後再読→普通TERM一回→期限15秒と後条件 | /proc本人/全子・DBpeer/advisory/M-A消失、全元値二読。旧operation正常closeは期待しない、再signal/DBterminate/OSstop0 | PG1449actual0、旧1447actual143 |
| PT-ENV-COLD-PREFIX-001 | 別fresh source4066/new1450組立・javac -Xlint:all -Werror | 独立32field/64MiB正常と超過拒否/null-vector拒否/手書12role UID-GID、旧family literalなし、原本Root/run/ACT/DONE固定 | compile6oracle/Werror0 |
| PT-ENV-COLD-STAGE-001 | new1451 immutable stage、署名秘密鍵/credentialコピー0 | 114files/113hash、Root0400/dir0700、currentboot一致、workerstart/permitなし | PG1451actual0/archivehash |
| PT-ENV-COLD-PREPARE-001 | new1452 M→A/専用readonlyDB/advisory/heartbeat/十Ref/原本Session、current自己bindRO/空namespace12roleのみ | SS343 SSC264限定delta。root0755/nlink8・coverage0755/nlink14/12child0700・UID-GID手書値/empty/ACL0、元原本/DB/署名187不変。全DB/Ref/FD/M-A正常返却 | PG1452actual0/complete literal/afterhash |
| PT-ENV-COLD-POST-001 | Java正常exit後別read-onlyobserverで十Ref・全post二読 | 24DB、Backup47/credential19/original68/oldProof51/18Unitfile/署名187、保持DONE SHA59f3…、ROmount、全資源free、12role等を独立literal/封印/SQL原値に比較。main方法でexpected生成0 | PG1453actual0/afterhash |

並行/再送: current一経路のみ、同prepare/stage/TERM再送は禁止・予約後未知は隔離。null/欠落/未知入力のnegativeはhost oracle、任意live破壊fixtureは発行しない。Coverage=Production変更0/新native0、PG1428残L892/M176/C12/B715据置。有限工具の検査を全分岐100%の代替としない。

実行: `python3 -B tools/quality/pg1448_current_cold_owner_test.py`、`python3 -B tools/quality/pg1448_current_cold_owner.py observe`/`handoff`（既実行・再発行禁止）、`python3 -B tools/quality/pg1450_current_cold_retry.py compile`/`stage`/`prepare`、`python3 -B tools/quality/pg1453_current_cold_post_test.py`/post本体。現在値/所有/各new-only保存先と資格manifestの照合を要する。実行環境Ubuntu26.04.1、VMkernel7.0.0-34/JDK25.0.4/hostPython3.14、LAN QEMU10.2.1/KVM/vCPU4/RAM8GiB。秘密raw・DB・session・keyはroot-private、公開はsafe whitelistのみ。
