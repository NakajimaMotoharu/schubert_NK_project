# API Lifeの初回停止予算供給・限定製造/単体仕様

2026-10-25/WBS-P018-05/group2104/PG-D638、P018-09必要参照追加費0。開始0.5/2/3pp/cap3、fresh57残43/reset1793382075、元共有0/reset1793306748・90上限/捕捉下限82・不明2/正確nullを維持。80大型新群抑制下の短工程で、既API Lifeへ1870のfirst-stop予算を保持・供給する。原/v4/v5と専有費・工数nullを変更しない。

Program NK-OPS-001/class ApiProcessLifetime ctor/stop/fail/remainingStopNanos/close、RD171/UI252/SS312321342351、必要依存1871。Resource-free注入clock、default System.nanoTime固定、stop通知を先に確定→最初begin一回。closeの通知finallyはclock障害でも主owner終端を通知する。残時間は既保持budgetの値だけでrenew0。Main/Manager/Outbox接続と実Unit期限内の全停止は別未完HOLD。

旧ApiProcessLifetimeTestの既存メソッド/HookDriver/TERMは本文保持し、新lifeBudget001～010だけmethod selectorで選択する。新試験ではinstall/addShutdownHook/HookDriver/TERMを実行せず、自己所有の有限Executorとunstarted hook object/Clockだけ。fixture例外は同object、NPEをcatchし正常化0。旧成功確認再演/旧26・18の新source転用0。

| Test ID末尾（LIFEBUDGET） | 入力/操作 | 独立期待/根拠 |
|---|---|---|
| 001 | 注入clock null | ctor NPE、取得なし |
| 002 | ctor/停止前remaining/close | 初期stopping=false・残期限未開始拒否・clock0、closeで一読 |
| 003 | clock100 stop→109再stop | 停止即true、再通知未読・残59_999_999_991ns |
| 004 | fail/await | 停止true/残60e9、health未読・固定API runtime unavailable |
| 005 | close→clock29再close/owner shutdown | 最初期限保持/残59_999_999_971・計2読 |
| 006 | clock RTE/NPE契約違反 | 同object throw・stopping=true/残0、再通知未読 |
| 007 | close clock Error→自己Executor shutdown | 同Error/残0、最初closeのfinallyでowner終端済み・有限帰還 |
| 008 | healthy=false | fail/停止/固定IOException/同最初予算 |
| 009 | clock保持中二stop | flagがclock前にtrue、clock capture一/全fixture回収 |
| 010 | 固定default constructor | 0～60e9ns、Unit残時間計測/実停止成功とは認定しない |

独立expectedはliteral/time差分/同identity/明示回数、productionでexpected作成0。Source固定後normal六→新10/三static・actual whole-class coverageのmissedも含め保存→旧byte/owner/traceへ。既classの旧guard/hook/native部分が未実行なら全class四100/Program PT完了にせず、全451の保留を維持する。変更行/新methodの試験成功を全API受入へ読み替えない。結果1873/manifestに実source/run/command/OS/JDK/exit/XML/coverage/hash・未実行を保存。正式1964-53/原190新受入0/QA051final・工数null・全actualHOLDは不変更。
