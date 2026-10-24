# 1757 Timer標準text encoder PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351、1754/1756を前提、WBS-P018-09/C07、group1984開始3/5/9pp・cap10固定。現既資格candidate f02fae44e、全ownjob終端/未配備、actual VM/Root/DB/endpoint等HOLD。後続索引はSummary1754/1753で、Timer標準textは未実装を確認済み。

## PG-D594・今回の一経路

共通bootstrap srcのPrometheusSummaryExporterを拡張し、既scrape（Summary/秒）/旧package writer seam/既IO error message・wireを維持、新scrapeTimers（Timer/ns snapshot→秒）を明示追加する。内部SourceKind enum二値で型契約と単位を分離し、同一snapshot/CDF検証・公式model/text処理を共有する。boolean mode/private反射/fake registry・marker/暗黙Loaderは追加しない。field/keyの閉集合、borrowed lifetime、unknown meter無視/選択wrong型拒否、finite非負total/有限CDF順・整数・2^53精度拒否を保持する。Timerはcount値を変換せず、totalと有限boundだけ1e9で割る。変換後boundが0/非有限/非正順なら拒否し、極小値の消失を正常0bucketへ偽装しない。MAX sumをlongへ戻さない。

既class名/APIは保持する（summaryは観測集約の内部名称）。HTTP counterは今回の受入対象へ混ぜず後続別群。実service/Web/Caddy/Root起動・deploy/DB/JMS接続なし。SS/業務仕様/Currentbaseline変更なし。

## 独立Test matrix（実行前固定）

|Test ID|目的・fixture・独立期待値|
|---|---|
|TIMERENC001～016（新16）|bootstrap fake public Timer snapshot/own registry：literal ns→秒/9bucket/+Inf/count、1ns/二Long.MAX_VALUE ns、複数series/labels、wrong Summary/Counter型、null/closed/空・unknown、負/NaN/Inf/count、CDF順/整数/上限、bound変換underflow/順/非有限、snapshot一回、RTE/Error同一伝播・借用非close、mutable namespace切離し、SourceKind二型生成factoryのtyped独立契約。期待text/sampleはliteral、Productionから生成しない|
|HTTPEXP001～006（新6）|実OverflowSafeHttpMeterRegistry＋実HttpMetricRecorderのown memory接続：DEBUG35timer/一family420sample・native helper/1750counter非公開、STANDARD空、/loginの1ns/九境界前等後/二MAX正sum、window超過後もCDF保持、別owner/有限worker。labelは独立route fixtureの既承認/loginとserviceWEB、実HTTP requestではない|
|SUMENC001～024/APISUM001～006（必要既30）|共通検証/出力の変更影響として旧Summary/秒/wire/IO/借用/null・API二histを同新sourceで確認。既oracleを変更しない|

合計 **52件/4suite**予定、新22＋必要既30。実Test一覧と依存fixtureをsource固定前に照合し、異なれば成功加算せず実行前訂正を記録する。boundary oracleはSS351の.05/.1/.25/.5/1/1.5/2/2.5/5秒とliteral long ns、CDF累積独立計数、暗号/DB原本等fixtureなし。IOは旧checked seamで共通catchを検証する。

新source正常六build/NullAway/Spotless→fresh同source52/4→当変更bootstrap Main/enumの全branch・四counter100/静的/生成factory別証明→全六physical/全source-owner/五architecture→1758/公開scan/push。旧source32/58/4222を合算しない。失敗/flaky/skipped/not-runは合格0、既実装違反は915/916先行。実command/OS/JDK/source/fixture/期待actual/XML/exec/coverage/BUG/path/hashは1758と公開manifestへ。

現在未実装/未実行/coverage未測定、正式1964-53/原190新受入0/工数null/QA051final/PTALT0不変。元-v4-v5/群開始見積不変更、消費共有枠/実tokens/PGPT-PMO/追加発見/手戻り/再認証を分離する。通常小区切り停止0、現行continuous-v2を維持する。
