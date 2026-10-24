# 1758 Timer標準text・app配置是正 PG/PT結果

NK-OPS-001/RD171/UI252/SS311351/1757・PG-D594、WBS-P018-09主費用/C07共有参照0加算、group1984開始3/5/9pp・cap10不変更。

## 今回の確認可能な増分

新独立Test ID **22**（Timer unit16＋実Web recorder接続6）、必要既30（API Summary unit24＋API接続6）と合わせ当source真正 **52件/4suite**。新Timer/ns→秒/九CDF/Inf/count/正sum/標準text経路を追加し、旧Summary/秒の外部goldenは不変更。候補source **3968abacec2052b9e7b803702a3a9231f9209f26**（Production Main/POMはd496同byte）は未配備、実runtime UNKNOWN/HOLD。

配置成果はAPI専用 `ApiDurationMetricExporter` とWeb専用 `WebDurationMetricExporter` の **app Main2**、旧不適合bootstrap Main1/package-infoを退役。未受入SourceKind modeも廃止し、同じ業務model/classをapp間共有せず、単位/入力型の異なる各app adapterが公式model/writerを利用する。六module/業務/SQL/権限/HTTP/JMS公開/Root起動/画面/承認DIF/Currentbaseline不変更。旧配置はGit履歴で回復可能で、原成果を破棄していない。

DEBUG一family/35timer/420sample、1750HTTP counterとnative helper Gaugeの非選択、STANDARD空、1ns→1.0E-9秒、九境界前/等/後の独立CDF=2/5/8/11/14/17/20/23/26/27、二MAX正sum1.8446744073709553E10、窓超過後累積CDF保持、64worker/別owner、未知入力の閉route `/**` とraw非公開を検証。unitはraw negative/NaN/Inf/null、converted bound underflow、CDF整数/順/上限/2^53拒否、snapshot一回、label escaping/duplicate/欠落/未知/null集合、RTE/Error/checked IO/borrowed非closeを独立literalで確認。

## BUG1697/YKT1448：上位を広げずcodeを是正

初稿1a066d08bの8310正常six、8312原 **75eeb2c810a33d67a27ff358eb7c579db081917e9fb88d2791395d5025d6da75**（52全成功）/8314原 **b42db001243cdc99e02c0acbb1598b4a02c57b3ef3da3c0a746ce7d1259fb9ae**（L93/M11/C2/B50全100/static0）は真正結果として保持。しかしcanonical SS311/411では共用Bootstrapは固定起動責務に限定され、pure技術なら任意部品を追加可というPG判断が誤りだった。五architecture edge rule0は責務許可そのものの証明ではない。BUG1697/YKT1448を修正前起票、1754の共用配置適合も再開/保留した。

上位仕様は正しいためRDF/UIC/SSC/QA不要。設計をcode都合で拡張せず、d496e7430へapp配置/明示SDK依存を是正し、3968abaceで各app negativeを補完。既MavenのWeb→API test-only依存はPT-IDEM-016のための不変fixtureで本番依存とは区別し、製品POMのscopeを変更しなかった。旧API wire/IO期待値は保持、未受入SourceKind factory観点016だけを役割固定に伴い退役履歴としWeb checked IO確認へ置換した。

|横展開全対象|是正/非該当と再発防止|
|---|---|
|Bootstrap monitoring/Main/package-info/POM|新monitoring sourceとMicrometer/textformats直接依存を退役、既34sourceの限定起動責務はそのまま。既credential/proof/config/JDBCとStorage依存不変更|
|API app/exporter/POM/全caller|Summary/秒だけをAPI監視packageへ、公式textformat1.7.0をappへ明示。SUMENC24/API6のclass参照を追随しliteral expected不変更|
|Web app/exporter/POM/全caller|Timer/nsだけをWeb監視packageへ、公式textformat依存はWebが所有、API artifactのproduction参照なし。TIMERENC16/Web6と各appのinvalid namespace/label等を補完|
|未受入SourceKind/旧共有Test/tool source|動的type modeを廃止、元1a source/成功を履歴保持。新52はapp-owned型/単位へ独立source/runを束縛、古いhelperは歴史用途で再演しない|
|責務検査と既test-only依存|新8317の初稿はscopeを省略し、既PT-IDEM-016 test-onlyを誤拒否/未公開/製品PT0（ef46be6c5）。元失敗/sourceを保持→f02 immutable Web POMとscopeを明示、production昇格を含む九反例へ。bootstrapへのSDK/source/誤package・型・app間本番edge等を拒否。五edge ruleだけで責務適合を主張しない|

## 現sourceの実行・品質

公開manifestは evidence/01_PT/018_NK-OPS-001/evidence/provisional/、元source snapshot/command/OS/JDK/終了receipt/XML/log/execは /home/mini/codex/project1/work/pgpt-runs/PG379 の同小文字slot。JDK25.0.4/Maven3.9.12/offline/clean own environment・明示emptySDK設定。全input/expected/actual/source/branch/hashを1757のTest IDへ結合する。

|段階|真正結果・manifest SHA256|
|---|---|
|PG8320-app-duration-six-compile-v1|正常六package/NullAway/Spotless成功、PT0/UNRUN。**873d524e75f2826777d633eaadc1888b76d47ad0913c8f74b8d957a447d8c7aa**|
|PG8322-app-duration-host-v1|新22＋必要既30=52/4、F/E/skipped/aborted0、fresh Test compile/一JVM・一exec。**f6ef95b48d42d8dc8b6dde807ef4bf020fc23c4d294d16a8ab281708ed44b875**|
|PG8324-app-duration-post-v1|両app Main2のline152/method16/class2/branch92 **全miss0/100%**、CRC0/一session/union0、PMD/Checkstyle/SpotBugs/missing全0、七receipt反例拒否。未受入modeを廃止したのでgenerated enumは現在0、実コードを除外したものではない。**89b5f4a47fe347ce5b92acc9f8bc06f59a2ba9ee0d3e5e0276ffcf45ce6a21cb**|
|PG8317-app-duration-owner-guard-v1|d496の同Production source/POMで34Bootstrap source・app型/SDK/roleと九negativeをmetadata限定検証、PT0/init0。**5e83ac7eed1e7dc6c04cf3190044ad6096899ce2163cff92f3a6a33d85471e4d**。8326で全測定source/三POMの同byteを結合、fixture-only差分のため確認だけの九反例再演0、PT成功へ加算0|
|PG8326-app-duration-six-trace-v1|全六/1801physical、旧共有2を退役/app2追加・他1799全byte/debug不変・原1669不変、src差分10/全160source-owner。五edge0＋別責務guardの実測input同byte、target init0。canonical SS311 main ref/hashも固定。**6551d57bb893ebf30df9a8241cb9d64ca2a65c661fa52c939d73ad1c8bd43996**|

実commandは既PYTHONPATHの python3 -B tools/quality/pg8320_app_duration_six_compile.py → pg8322_app_duration_host.py → pg8324_app_duration_post.py → pg8326_app_duration_six_trace.py。既jobは再起動せず元receiptを読む。8316/8318のd496初回52成功原c7e73fbeも保全、per-role negative補完後の52へ算術合算しない。元共用58やHTTP修正32も別source/別execでunion0。

BUG1697/YKT1448は全配置/依存/caller/試験・scope/metadataと新source再試験/四100/static/traceを結合して本限定範囲CLOSED、完了日2026-10-24。1754の旧共用配置は採用撤回・後継API adapterへ置換として閉鎖、当旧sourceを新配置の適合証拠にしない。

## 計測・後続

保存前8330の初回（tool7fe072964）は削除済み追跡Java三fileを未対応入力としてfail-closedで停止し、scan結果未公開/未合格。新tool依存として三pathをliteral宣言・Git実削除集合と完全一致させ、元regular blobのmode/type/有限size/UTF8/原hashを照合して旧本文も同三patternで検査する。欠落/未知/余剰/記号link/binaryをskipして0へしない。七metadata負例を追加し、元停止/tool sourceは保持する。製品PG/PT再実行やscope/品質緩和ではなく、削除差分の保全検査補完として分離記録する。

直近fresh25残75/reset1793382075、開始24/3-5-9/cap10不変更。初回新22/既30、追加発見1697の配置手戻り、guardのscope fixture補完、per-role negative強化/変更source再認証を分離する。丸め共有差1は専有費でなく、N/T/工数null・usage dbb8498f/13:57:55JSTは明示0/完全性未証明。元-v4-v5や当初見積を遡及減額しない。

次=公開scan/保存/push後、別fresh bounded群で残HTTP Counterの標準text出力をapp監視責務内でPG/PT。実endpoint/owner/source/BOM/CHR/native/全scope same-run/451は未受入、正式1964-53/原190新受入0/QA051final/PTALT0/全actual VM/Root/DB/鍵/配備/拒否未特定HOLD不変更。通常報告/commit/小受入で停止せず継続する。
