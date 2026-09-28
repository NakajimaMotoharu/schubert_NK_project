# 親Backup送達不明例外境界 PT結果（PG365、限定）

- Program NK-OPS-001、`MorningBackupUnitCycle.execute`、PT-OPS-BUCYCLE-005（関連001～004）。仕様242、RD OPS-009/BAK-001、UI251、SS341/343、SSC105～107、BUG-324/YKT-256。公開合成portでstart呼出後IOException/StopGateException/RuntimeException/Error、null attempt/status/awaitを投入し、保持port1/stop0/retire0を独立期待値とした。pre-start baseline失敗はstart0で通常拒否。
- RED: 修正前2026-09-29、BUCYCLE5件中F1/E/S0、exit1。`start.execute()`のIOExceptionが保持portを経ず外側へ伝播することを確認。不合格を合格件数へ算入しない。
- GREEN: `dev-foundation` source/test `0eb7df06f`、2026-09-29 JST、Linux x86_64、JDK25.0.4、Maven3.9.12、SpotBugs4.10.4.0、NullAway0.14.1、JaCoCo0.8.15、Node24.19.0。選択BUCYCLE5PT F/E/S0/static0。親資源所有のsecurity横断triggerで、同commit全6 `clean test spotbugs:check jacoco:report` exit0。Protocol80/17、Storage149/21、Bootstrap177/22、API756/125、Web560/87、Batch755/90、計2,477PT/362suite、F/E/S0、SpotBugs各0。
- coverage missed I/B/L/M/C: Protocol/Storage0、Bootstrap60/37/11/4/0、API95/3/32/4/0、Web80/1/25/4/0、Batch1393/29/302/120/15、`MorningBackupUnitCycle`外側122/8/26/8/0。全100%・全分岐は未達、native factory/実Unitも未到達。これを実親30分hard-timeout・archive/Cleanup/permit・R2/R3/実NK CHRの合格へ読み替えない。
- 証跡: `evidence/provisional/PG365-start-boundary/manifest.json`に同source、command、結果、raw XML/hashを保存。raw JUnit/Jacoco、秘密、session/token、VM credentialはGitへ置かない。BUG-324直接原因の修正は再試験済み、YKT-256は他入口の横展開中。
