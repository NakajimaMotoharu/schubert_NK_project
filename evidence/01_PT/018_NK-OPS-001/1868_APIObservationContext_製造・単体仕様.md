# API観測・SDK assembly 製造/単体仕様

2026-10-25/WBS-P018-09/group2100/PG-D636。開始4/7/10pp/cap10/fresh56残44、原/v4/v5不変更。Program NK-OPS-001、class ApiObservationContext prepare/ctor/initialize/rejectStopping/metrics/close。RD171/UI252/SS311332342351、必要依存1867、worker1864/RO1858/cache1860/pump1862/binding1852。実APIへのMain接続・既残期限供給/nativeは未受入HOLD。

caller保持後SDK initialize→DEBUG worker start一回。STDは観測worker/SQLなし。既remaining portを借り、worker stop→有限await確認後だけSDK close、UNKNOWNは同owner/policy・SDK/Poolを後続解放しない。initializer/close競合と再入は非正常保持。借用Poolのclose/権限変更0、新60秒/親予算リセット0。非fatalとfatalのfailure graphは元objectで保持、provider textは出力0。

独立oracleは明示literal順序/回数・同failure identity・固定text/元予算supplierアクセス回数・fake JDBC後条件/明示Prometheus値。productionからexpected生成0。既44や全4222確認再演0、当scopeに必要なfake fixtureはcompile-only。新OBSCTX001～026の予定一覧：

| Test ID末尾 | 入力/操作 | 独立期待・観点 |
|---|---|---|
| 001 | public prepare各null9境界 | 各NPE、factory/SQL/worker開始0 |
| 002 | 未知/空/小文字mode | 固定config拒否、外部操作0 |
| 003 | internal ctor各null4 | 各NPE、lifecycle0 |
| 004 | STD public prepare→initialize→render→close | bean/SQL/clock/remaining/failure0、詳細outboxなし |
| 005 | DEBUG public prepare、初期化前 | supplier/SQL0、borrowed metricsは同owner |
| 006 | DEBUG public fake query→render→close | 明示3/5/7件・2/4/6秒、close前cleanup順・Pool操作getConnectionだけ |
| 007 | DEBUG public query Runtime | 同object failure通知一、SDK closeはworker終端後 |
| 008 | normal initialize二回 | 二回目拒否、setup/start各1 |
| 009 | close前initialize | initialize拒否、setup/start0 |
| 010 | 未初期化close二回 | SDK取得/registry close0、remaining未読・正常冪等 |
| 011 | SDK setup Runtime | 同primary、worker start0、後close1 |
| 012 | SDK setup Error | 同fatal、worker start0、後close1 |
| 013 | worker starter Runtime | 同primary、SDK保持、close確認後1 |
| 014 | worker starter Error | 同fatal、SDK保持、close確認後1 |
| 015 | 正常worker start/close | 元remaining参照、worker終了後SDK close1 |
| 016 | worker未終端/残0 | 初回IOExceptionはliteral observation worker stop unconfirmed/同policyobject、再closeはassembly literal API observation context close unconfirmed・SDK close0/正常化0（BUG1736/YKT1487でorigin根拠を明確化） |
| 017 | 残supplier Runtime | 同object、SDK0、policy1 |
| 018 | SDK close Runtime | 同object、再close正常化0、SDK再close0 |
| 019 | SDK close Error | 同fatal、policy一、抑制0 |
| 020 | UNKNOWN policy Runtime | 原primary保持/suppressed同diag |
| 021 | UNKNOWN policy Error | 同fatal優先/元primary保持 |
| 022 | initialize中の別thread close | 非blocking UNKNOWN、後SDKも保持 |
| 023 | initialize callback再入close | UNKNOWN・再入lock拒否、initialize停止拒否 |
| 024 | worker.start callback中close | UNKNOWN、start後停止検査・元worker回収はfixtureだけ |
| 025 | close中の別thread close | 二次UNKNOWNで一次も正常化0、SDK close一 |
| 026 | requestStop failure | 同failure保持/UNKNOWN・SDK0、自己所有fixtureで回収 |

全null/例外/境界/競合・全class四counterを当sourceで実測、到達不能除外/無意味assert0。実command/source/run/OS-JDK/input/XML/CRC/session/static/manifest/hashは1869と当runへ保存。実VM/DB/Root/既存サービス操作0、普通fixture回収は実UNKNOWN解除/実資源受入ではない。正式1964-53/原190新受入0/工数null・QA051final・全actualHOLD維持。
