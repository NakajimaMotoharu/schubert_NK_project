# NK-OPS-001 三fixture返却前setup単体テスト結果

対象3505/BUG2245/YKT1991。初回source7f523d042a609f4833fbf6d7acf0c375643973ebのPG18558はb50ede actual0、静的指摘是正後sourcecc8e00ac6b9d7e8c7f0301b94d42f84b220d3682のPG18564は17831/8fcc44 actual0。各runは同じ12method/3Test class（各26literal vector、計78）、F/E/S/aborted0。24uniqueへ算術加算しない。元失敗工具と元62指摘は637/638、是正後は640へ分離する。

|program/class|Test ID|結果|helper coverage（line/method/branch）|
|---|---|---|---|
|NK-OPS-001/BatchDatabaseFixture.beginTransaction|PT-FIX-SETUP001～004|4method/26vector PASS|13/1/6、miss0|
|NK-OPS-001/ApiLogDatabaseFixture.beginTransaction|同上・classと組で一意|4method/26vector PASS|13/1/6、miss0|
|NK-OPS-001/WebLogDatabaseFixture.beginTransaction|同上・classと組で一意|4method/26vector PASS|13/1/6、miss0|

独立期待値は3505とTest内固定20rowのwinner表/同一例外四row/正常/nullの二row。Mainの順位判定を呼んでexpectedを生成していない。normalは同一connection返却・設定false一回/close0、失敗は設定→close一回/その他JDBC0、SQL/未知Runtime/NPE/Errorの正確なwinner/secondary同一性を検証。NPEを正常業務に変換しない。3Fixtureを実体生成せず、JDK proxy以外のJDBC取得/DB/Flyway/Root/VM/サービス操作0。

compileは-proc:none/-Xlint:all/-Werror JDK25、標準JUnit Console1.13.4を明示12method selector/--fail-if-no-testsで実行。実command/環境・source/input/class/tool hash/時刻/真正exitは各公開manifestのbegin/stages、原XML/exec/info/classinfoはown host slotのmanifest参照。標準JaCoCo0.8.15の単一sessionは各run別、3CRCを実execとclassinfoで照合。生成byteはPG18554/18560、事前独立性は636/PG18560、postは637/640。元成功結果を更新Test sourceへ移さず、必要な更新12件だけ再実行した。

```text
PG18564 standard command pattern（完全argvはmanifest begin.command）
JDK25 java -javaagent:org.jacoco.agent-0.8.15-runtime.jar=destfile=<own>/jacoco.exec,append=false,sessionid=PG18564-FixtureSetup,includes=<exact3Fixture>
  -jar junit-platform-console-standalone-1.13.4.jar execute --disable-banner --fail-if-no-tests --details=summary
  --reports-dir <own>/reports --class-path <exact6classes>:flyway-core-13.4.0.jar
  --select-method <each exact12 class#method>
JaCoCoCLI0.8.15 report <same exec> --classfiles <each exact3Fixture.class> --xml <own>/coverage.xml --csv <own>/coverage.csv
```

whole Fixtureはline212/method26/branch34が未実行。class counter3coveredは全method/全分岐合格を意味せず、whole四100やcoverage除外は主張しない。公開XMLは実case class/name/timeのみへ正規化し、system properties/stdout不要情報を省いた。実環境versionは元JUnit XMLから指定OS/JDK keyのみ抽出しmanifest追記へ記録、秘密値/認証cookie/DB原本はGitへ保存しない。

静的は初回PMD62→定数化後56、Checkstyle0、処理error0。全六DuplicateLiteralsを解消し、残56のrule/method multiset不変を640で照合。設計必須のidentity/typed cleanup27、純粋proxy所有9、standalone JDK loader3は具体根拠付きレビュー、未変更constructor17は適用性判断待ち。PMD0/全F03/全451を宣言しない。三Fixture/三Testのcanonical ownerは旧485未登録でUNKNOWN、変更担当P004-05を主担当へ推測転記しない。

新実績はTest infrastructure12methodの限定成功。原Product3008/451、正式1964/53、歴史17/190、新個別受入0、工数nullを維持。BUG2245/YKT1991は部分是正・pure unit確認済み、実provider/影響caller・全品質/traceを残しOPEN。初回代表Vは別の未達HOLDのまま、今回をV成功/本体費用較正へ付け替えない。
