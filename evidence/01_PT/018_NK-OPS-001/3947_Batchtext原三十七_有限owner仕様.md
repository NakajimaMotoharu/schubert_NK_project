# 3947 Batch text原37 有限owner仕様

G03.05主/P01809関連、REWORK着手前見積1/4/8pp cap10。原2823/2824のBatchMetricTextTestはBATCHTEXT001..024とBATCHFULL001..013のwhole1/37（コメント24に限定しない）。834行全body/fixture/initializer、Main BatchMetricText/StandardMetricSource/StandardMetrics/JvmMetrics/SystemMetrics/GcMetricRegistrationと既LabelPolicy/Metric/Modeを全文確認。元110を成功確認再演しない。

BUG2581を915修正前起票後、batchtext024とbatchfull011の二worker TWR終了だけをregistry/standard外側TWRの内側で単一finally.shutdownNow-await10へ是正。既submit/Futureget10三site、64job/16×2・全37期待/literal/fixtureを保持、worker終了後に借用standard/registryが逆順close。Product外部仕様変更0/QA不要。

NORMAL_PTの根拠は2823の既定範囲と現477/continuous-v2。原batchfull012は所有する試験子JVM自身のJDK public CPU/heap標準metricsを読むもので、元期待値/actual自己SDKをfakeへ置換しない。固定SDK bind順JVM→SYSTEM→GC、owner受領後GC listener bind、finally GC→registry close、強制GC/負荷/OOM/dump/外部target/attach/Root/DB/実VM/サービス/network/鍵/permit操作0。F03 Root11等と四held compile/init/probe/保護工具二名HOLDを変更しない。直前のfake群の実観測0は各群の限定範囲であり、2823の自己JVM通常PTを撤回する利用者指示は現477/継続方針にない。元公開SDK証拠8170/8173を同byte時だけ再利用する。

SDK: 固定1.17.1 Micrometer四Jar/1.7.0 Prometheus六Jar/Hdr2.2.2。既8170の15Jarから不要OTEL initializer/otel3と重複JSpecifyを除く11Jar、外部endpoint/exporter起動0、cwd/tmpはfresh own。Mainは現normal7aedからBatchMetricTextの完全一Source一Codeだけcoverage用抽出、全Main再compile0。元37 wholeをfresh javac/一JVM/一sessionで一度再試験、input/環境/command/終了/CRC/held四/独立golden/static/四counterを正直に記録。SDK identityをProduct coverageへ加算せず、旧110/SDK実測を新sourceへ転用0。

独立oracle：固定HELP/TYPE/sample byte・6familyとkey/series順、NaN/+Inf/-Inf/signed0/min/MAX文字列、counter負値/非finite拒否、null/未知/追加/欠落/重複/wrongtype拒否、provider読取各一回/変更後snapshot、途中失敗partialtext未返却・同例外、STANDARD provider無読取/borrowed所有、custom→standard順、standard文字列固定cpu42fixtureとactual自己CPUの独立Runtime値（別case）、並行64/16×2。Main production methodでexpected生成0。証跡PG25218/20/22/24/26/28と3948。正式1964/53・520unique/工数null/全HOLD維持。

実行前補足（BUG2582/2583）：GJFのC_HEADER/G_HEADER各二連結は元literal値をexact2定数だけ復元・各3反例で確認、元915失敗は25230へ保全。LabelPolicy static initializerのStep/BatchStep二enumと二Sourceが25224 whitelist/input記述から漏れていたがMain Jar全byteは固定済み。25232 reviewで製品前検出、916/25238が既25134合格post→25130のauthentic pin/currentnormal/indexからexact2だけ補足・missing/hash/unknown3反例。旧preflight/entryは不変更、unit/独立postは元入力と補足入力の同source SHAを両方検証する。追加未知class許可/期待/品質/HOLD変更0。工具draftの仮置きpin式は実行前reviewで撤去し真正旧post pinへ修正、body未実行のbefore hashを25239へ保全。
