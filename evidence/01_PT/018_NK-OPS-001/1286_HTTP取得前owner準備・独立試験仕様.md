# 1286 HTTP取得前owner準備・独立試験仕様

PG-D461/SSC312/BUG1545/YKT1305。NK-WEB-002/NK-OPS-001、SYS002004/MON003/SYS001006/AUT001、UI222/226/243/252/253、SS313/342/343/352/354/362。三classはApiManagementServer、WebManagementServer、WebHttpServerのfactory取得とprivate constructor。固定API8091/Web8081/HTTP8080、URL/電文/権限/SQL/ready/既cleanup例外順位は変更しない。

独立oracle=SS312ではなくSS313/342 SSC312の順序契約と固定literal。PT-HTTP-OWN001/002はfixture factoryが一度だけ呼ばれ、127.0.0.1/backlog32/port0、IOException/IAE/ISE/NPE/Errorの同一Throwable返却、null NPEを確認する。003はTomcat supplier一度・同Runtime/Error保持・null拒否・owner通知0、checked IOExceptionは非適用。factory自身の未返却資源はcaller所有と推定しない。新fixtureは資源を作らず、既実HTTP正常/設定・URL/cleanup再試行/並行/割込の全API/Web通常PTを併用する。未refreshMVC/未開始executorには開始済資源がない。

構造oracle=実ClassFileのconstructorを独立解析し、全owner fields/state/lock/executor/MVC/address allocationがfactory前、factory後はnonnull/final store/returnのみ、全public ABI・既取得後method命令不変を確認。故意のOOM/実VM/稼働DB/Root/current/失敗cohort操作はしない。旧8703985や599925を新source成功へ加算しない。branchを除外/到達不能補完せず実四counterを保存する。

開始前見積り=0.5/2/6週次枠pp（F03主、共用新全体K01.01別主/参照費0）、原v3/v4/工数null維持。通常PT着手判定は462へ保存後、全API/Web＋他module guardsを新only namespaceで一回、全原XML/source固定/終了0/六format型nullSpotBugs/全Main物理差・無除外PMD/CS/対象四counterを独立確認する。必要当source全体は変更群をまとめ一回、真正結果を回収し別source結果と混ぜない。

正常/境界/null/異常/例外は上記独立fixtureと既suite、並行/再送は既close/owner/readiness PTと当source全体。未確認native/CHR/451/trace/QA051final/正式条件は別未完。実command/OS/JDK/branch/commit/時間/exit/input/expected/actual/coverage/BUG/path/hashは公開manifestと結果1287予定へ記録、raw/鍵/credentialはGitへ含めない。
