# 検索HTTP単体テスト仕様書

NK-WEB-002/SCR003、ScenarioController.search、FUN003/AUT001～003/SYS006/TST001～005、UI221～223/234/264、SS312/313/314/323/352、SSC072/PG203。仕様先行・未実装・未実行。ScenarioSearchControllerTestの以下12methodをTest IDへ一意対応する。

| Test ID | method | fixture・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-SCR-034 | search034SuccessAndWire | USER/ADMIN、空/全条件、NFC/trim、0/1/100結果 | SRC→GAM→SPK各1回、UI234 byte offset literal、page100、contextはactor、閉model/順序 |
| PT-SCR-035 | search035InvalidNoMq | 重複/未知/enum/byte/control/page不正、全7field | HTTP400/search、固定error・入力再表示、結果なし、送信0 |
| PT-SCR-036 | search036ResultErrorsAtEveryStage | 3段階×各error code | WebResultMapper既定HTTP literal、後続送信なし、Modelなし |
| PT-SCR-037 | search037SessionInvalidAtEveryStage | 各段階0102、既存session/security context | 302 session-expired、session破棄、後続/描画なし |
| PT-SCR-038 | search038MalformedAndTransport | 各段階不正wire/known送信失敗 | 503、後続/描画なし、buffer消去、再送なし |
| PT-SCR-039 | search039ResponseBinding | 最終page補正/要求と異なるpage/不整合count | 正当な最終補正だけ成功、不整合503、secret非反射 |
| PT-SCR-040 | search040NullAndFailurePropagation | null/非SessionPrincipal、Model/response/未知callback例外 | constructor/API境界拒否、未知例外同一instance伝播、NPE正常化なし |
| PT-SCR-041 | search041MvcGetHeadAndMethod | 実MVC/resolver、GET/HEAD/POST/未知parameter | 200 DOM/HEAD空/POST405、invalid400かつMQなし |
| PT-SCR-042 | search042RealHttpSecurity | embedded HTTP/実Web session DB、匿名/両role/0102 | 匿名302かつMQ0、成功no-store/nosniff/Logout CSRF、失効cookieと次回no-MQ |
| PT-SCR-043 | search043EscapingAndIsolation | 特殊文字q/speaker/chapter/username | escaped DOM、独立固定href、raw context/電文/例外なし |
| PT-SCR-044 | search044ConcurrentRequests | 64独立actor/query、共有controller | 各3要求のcontext/query分離・192独立correlation、混入なし |
| PT-SCR-045 | search045CompatibilityTrace | public synthetic検索/0件/頁/音声有無 | 明示HTTP/DOM/順序、公開countだけのtrace。実NK gateではない |

FixtureはUI234の256byte header、SRC672/PAGED48/record5584、GAM9/272、SPK9/152から独立に組む。ExpectedにProduction codec/mapperを使用しない。requestはbyte offset/length/paddingを独立比較し、秘密値をGit証跡へ残さない。正常/境界/異常/例外/null/並行/再操作を網羅し、再送は自動なし・新HTTPは新correlationを確認する。Java line/method/class/branch100%、NullAway/SpotBugs/Spotless、既存階層・template・script回帰を要求する。

実行command/環境/対象commit/日時/exit/coverage/関連BUG/SSC/hashは010結果とmanifestへ記録する。実行前の合格記載禁止。実broker/API/本番bootstrap/REQUEST log/実NK CHR/IT/STは別gate。
