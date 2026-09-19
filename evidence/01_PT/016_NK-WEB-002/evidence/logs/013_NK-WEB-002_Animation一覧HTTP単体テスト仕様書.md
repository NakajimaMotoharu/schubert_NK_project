# Animationメニュー・一覧HTTP単体テスト仕様書

NK-WEB-002/SCR008/009、AnimationController.menu/main/ova/list/exchange/actor、AnimationMvcConfiguration.animationController。FUN006/AUT/SYS006/TST、UI221～223/232/235/264、SS311～314/321/323/352、PG207。正式23で12PT合格、詳細は014とmanifest参照。AnimationControllerTestの12methodと以下IDを一意対応させる。

| Test ID | method | 事前条件・入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-SCR-054 | animation054SuccessAndWire | USER/ADMIN、3route、0000/0200、ANM15/4/1/20・ANL0/1/50 | ANM256byte/ANL272byte、MAIN/OVA16byte、各1送信、閉pageだけ、件数/順序一致 |
| PT-SCR-055 | animation055ErrorMapping | 3route×全10error code | 既定HTTP mapping、0102以外のerrorはpageなし/no retry |
| PT-SCR-056 | animation056SessionInvalid | 各routeに0102、実DB Web session | local破棄/302 session-expired/cookie削除、後続MQなし |
| PT-SCR-057 | animation057MalformedAndTransport | malformed bytes/context/UUID、sender例外 | 503、pageなし、pending0/buffer0 |
| PT-SCR-058 | animation058ResponseBinding | menu合計不整合、ANL count/category/parent/duplicate/size不正 | 503、productionが送った不正値を期待へ合わせない |
| PT-SCR-059 | animation059NullAndUnknown | constructor/endpoint null、非SessionPrincipal、model/HTTP未知例外 | 明示契約/同一未知例外、無用な追加送信なし |
| PT-SCR-060 | animation060MvcRoutes | 固定3GET/HEAD、未知route、POST | 実template/handler選択、未知404/POST405、許容外はMQ0 |
| PT-SCR-061 | animation061RealHttpSecurity | 実Tomcat/security chain、未認証・両role・HEAD | 未認証302/MQ0、正常200/no-store/nosniff/CSP、HEAD本文0、CSRFはLogoutだけ |
| PT-SCR-062 | animation062EscapingAndIsolation | actor/title/path/IDにHTML/特殊文字 | 明示DOM text/percent URL、script生成なし/context不露出 |
| PT-SCR-063 | animation063EmptyAndGrouping | 0件、main＋sub先行/欠落sub、OVA | Current空section/200、main順・pair grouping・固定nav/MB |
| PT-SCR-064 | animation064ConcurrentRequests | 8workerで64actor/3route、共有facade | username/context/correlation独立、64送信/pending0 |
| PT-SCR-065 | animation065CompatibilityTrace | 公開合成menu/main/OVA | 3card/件数/URL・pair/順序、公開traceのみ、actualNkGate=false |

Fixtureは合成actor・独立UI232/235 byte配列、DBは既存WebLogDatabaseFixture/SessionRepository、実HTTPは既存EmbeddedWebSecurityTest.Serverを利用。Production encoder/modelからexpectedを生成しない。Current AnimeController/templatesの固定文言・空表示・link・順序を明示assertする。body/raw session/context/cookie/CSRFはGitへ保存しない。独立例外/境界/並行は上記method内で展開し、JUnit件数を水増ししない。

実行はJava25/Maven3.9.12、selected新12＋PG206 wire/PG204 model/PG205template・既存Scenario回帰、その後clean verify。line/method/class/branch100%・NullAway/SpotBugs/format合格、失敗/flaky/skipped/not-runは不合格。実行command/環境/commit/時刻/exit/coverage/BUG/SSC/証跡path/hashは014結果とevidence/manifest.jsonに記録する。実MQ/動画watch/Range/本番logging・全起動/実NKgate・PGPT/IT/STは完了にしない。
