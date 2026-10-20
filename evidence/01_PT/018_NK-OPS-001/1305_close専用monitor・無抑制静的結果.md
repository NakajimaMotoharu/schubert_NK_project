# 1305 close専用monitor：無抑制静的確認、実PTは未実行

元exec99942/pg6160-api-monitor-static-v1、source **292c06cc226522028aeb9978e545c1f12d7c84c9**。2026-10-20T19:10:30.766561Z～19:11:38.218154Z、真正0/Maven0/source固定、archive **a08d2b8223bd4e7b6510de34eb1d203e3028842196c67da218f8b760f4713423**。固定JDK25.0.4/Maven3.9.12。元commandはpg6160/manifestのAPI＋依存四module `test-compile` と固定SpotBugs4.10.4.0 check、format/Main型null/Test-Xlint-Werror不変更。

protocol/storage/bootstrap/apiのcompile/SpotBugs **全0**。元CWO四件を抑制/除外/閾値変更せず、四close専用private final owner monitorで同じ通知先行/phase/例外意味を表現した。管理のbudget tryLock/broker共用lockは不変更。JUnit実行0/TEST XML0/JaCoCo exec0、coverage未測定、旧sourceの八対象counterを移植0。BUG1557/YKT1314は静的是正確認まで、動的並行/新source全体依存は未完。

公開 `evidence/provisional/PG6160-api-monitor-static-v1/manifest.json`、私有PG379同runに原log/inputs/command/exitを保全。これはS3b製造前の静的確認で、実PT/正式/native/代替PTへ加算しない。次はPG-D466/1304の固定native保持portsと独立自己所有fixtureを同sourceで検証し、関連群をまとめて動的PT/全体/全理由/現traceへ進める。実VM/current/failedcohort等安全HOLD/正式1964-53/17-190/工数null/QA051final/PTALT対象不明/原v3v4を維持する。
