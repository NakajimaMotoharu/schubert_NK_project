# 2861 Web MetricHttpHandler原whole23 単体テスト仕様

NK-OPS-001/WBS-P018-09/RD171/UI252/SS342・351/1817、Production6b53/normal14216/dev-foundation固定。event3259で元2/6/10pp cap10を実行前固定。API原836行全読＋Web843行の全文role正規化差分を全読：package/class/method/service/ready prefix WEB、pool1/1/0/2・max2、022はWebServiceTest原static helperによるHTTP正常値一回観測。原whole23はcurrent1654のsuite/全Sourceに未登録。

Test ID webmhttp001～023、001～021/023の観点は2857のAPI原wholeを参照し、当Web literalで独立に実行する。200真偽prefix、404rawpath/405method、query有無、Content-Type/Cache-Control、UTF-8 byte長、header/body IOException identity、失敗時未公開、handleはexchange一回close/writeはcaller close、sample7.5→9.5→11.5、借用fake pool統計missing/真ゼロ/deferred supplier一回、caller cleanup一回。022は二memory responseでHTTP count1/duration0.25とDB max2を保持しHTTP再記録0。固定status/body/header/数値とcallback回数を期待値にしProduction expected generatorなし。

## 着手前のGraph独立性

WebServiceMetricBindingTestのwhole22は選択しない。元Test内のfixture/recordOne/request/response/observerと全initializersは既全読済み。022が直接呼ぶoriginal helperはvalid GET-/login-200・250msをinvoke/logし、二回目logはrequest-owned claimでno-op。fakegetterにfaultを設定せず、terminal Runnableは空、counter/durationは既存owner-compatible固定registryで正常入力、HttpMetricValve.signalFailure/Graph分類器を呼ばせるケースではない。WebService原009/013の故障注入は未選択HOLDのまま、新fixtureへの抽出や拒否ケースの分割再演なし。補助原Test二file（Observation/Service）はcompile-onlyで、JUnit選択はWebMetricHttpHandlerTestだけ。23件以外が発見/実行されれば不合格。予期しないGraph経路/失敗があれば再試行せず当scopeを保全する。

本検証はown SDK/GC handle・memory exchange/byte stream・未起動Tomcat Request/Response/Connector（socket未開始）だけ。実HTTP server/client/VM/DB/JMS/Root/鍵/配備/network0、forcedGC/heapdump/attach/targetprocessなし。normal Main/Test byteを固定しSource/fixtureを変えない。WebService/Valveの全counterや故障経路を受入/解放したとしない。

command: `env PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15186_web_metric_http_twenty_three_pt.py`。Java25.0.4/freshjavac -proc:none -Xlint:all -Werror/六normalJar/親180秒。post15188で同一exec CRC/全一Source closure/四counter、独立15190で全原23宣言XML/Helper未選択/固定HTTP LF literal/SS351/実ownerを照合する。必要なら同じ既存execのpassive classcounterだけでWebStartupException未実行を確認し、Graphを起動しない。元OS/JDK/時刻/command/exit/source/hash/input/XML/exec/coverage/BUGを2862へ保存。未実測coverageは未確認、除外なし/公式filter維持/execunion0、Failed-flaky-skipped-not-run合格0。障害は修正前915/916。

正式1964-53/歴史17-190/工数null/QA051final/451-F03-G07/全安全HOLD不変。供給readyやmemory200を実runtime/native/Browser受入へ換算しない。準備orchestrationのconst変数重複SyntaxErrorは全tool/commit/event実行前に停止し、識別子是正後に一回だけ開始した。

post15188では既存同一execだけをJaCoCo公式ExecFileLoaderでpassive読取する工具OwnedWebFailureProbeAbsenceをfresh compileし、既知WebStartupExceptionとnestedの記録probeにtrueがないことを検査する。Product classのload/初期化/invoke0・新exec生成0。正規sessionだけ合格し、異session/不足引数は工具の負checkで拒否を確認する（Product PTに加算0）。Source/Jar/agent/hashは元runに固定、結果は「当execに当prefix true probeなし」の限定測定で、Graph Test合格/全HOLD解除/未測定coverage100に換算しない。
