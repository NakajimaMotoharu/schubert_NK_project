# NK-OPS-001 検査起動wrapper・unit 単体テスト仕様書

2026-10-28追加（原監視Test十の規約是正影響再試験）：2412/2413・PG-D773、元whole81/十suiteの全既method ID/全期待を不変更。private時刻名十＋DEBUG fixture一だけ元token逆52反例で是正、scope worker20/gate1は保持。当源全81/同exec/23Main各四100・十九source44class全体/全artifact未達・clock/observeNow未使用0を独立確認する。索引evidence/monitor-test-name-regression/manifest.json、新Test ID0・全F03/451/実経路未受入。

2026-10-28静的用途補足：2408/2409・PG-D771、元型56の残28（request5/Thread9/issuer-baseline7/receipt4/scope1/repository2）をsource保持元と比較siteへ結合する。型解析/製品PT/既成功の再演0・新Test ID/受入0、用途の必要性と実行正常性を分離し全actualHOLD保持。

2026-10-28静的補足（製品PTではない）：2406/2407・PG-D770、元Main比較56/36fileの型・用途を照合、Throwable28のidentity根拠のみ確定・非Throwable28用途保留。source変更/製品PT/coverage/新規受入0、実例外graph/全F03/451はHOLD。Program内の既HTTPMETRIC等とは別の静的診断根拠でありTest ID数へ加算しない。

2026-10-28追加（監視metadata部分限定）：2404/2405・HTTPMETRIC001～006、HttpMetricContract private map命名一と元Test外側TWR一を当sourceで確認。固定35route/1750tuple/9bucket・null/未知/境界/collection不変/自己4worker64taskの期待は元1570/2149不変更。evidence/http-route-private-name/manifest.jsonへ同source6/六Main各counter100・完全artifact未達・rawThread四/gate1・BUG2017/2018を結合する。wrapper/native/実HTTP/VM/Root/DBの試験を代替せず、元計画の未実行HOLDを保持する。

RD OPS-009/ENV/SEC、UI212/251/252、SS341/342/343 §6.8/352、QA-046/UIC-006/SSC-049/PG-D-144。専用wrapperとbase/previous選択unit雛形の部分PT。全OPS Programや実unit/ITの完了ではない。

## 1. Fixture・網羅方針

InspectorDeploymentTest（API PT module配置、Program所有はNK-OPS-001）が実sh、ShellCheck0.11.0、systemd-analyze259.5を呼ぶ。wrapperは作業一時directoryへrenderし、固定fake Javaが公開receipt/終了codeを返す。実Java mainの負例も接続。unit検証は一時unit path・stub PostgreSQL dependency・実在する検証専用ExecStartへrenderし、host daemon/設定/credentialは変更しない。

Javaの4指標は全100%。shellは引数/placeholder/child exit/case4status/defaultの全判定とstatementを独立matrixで検証し、traceとsource行対応を証跡化する。class/methodはshell/unitでは非該当でありJava値を流用しない。unitは全directiveと4 previous profileの設定値/重複禁止/固定source pathを独立表で検証する。実root credential配布・timeout/TERM・親OS gateをstatic verifyで代用済みとはしない。

## 2. Test ID

| ID | InspectorDeploymentTest.method | 事前条件・入力/操作・独立期待値 |
|---|---|---|
| PT-OPS-INBOX-001 | renderedShellCheck | template全placeholderを固定値でrender、POSIX sh/ShellCheck error/warning0、source hash保持 |
| PT-OPS-INBOX-002 | statusMapping | exact receipt0/10/50/70＋JVM0だけ対応exit。JVM非zero/異常signal相当はreceipt0でも50 |
| PT-OPS-INBOX-003 | malformedReceipts | empty/未知prefix/code/余分text/space/LF/CRLF/改行なし/複数行を50。shellの末尾LF消去で誤受理しない |
| PT-OPS-INBOX-004 | argumentsAndPlaceholders | 引数1/複数/未renderは70、child実行前に停止。未知placeholderは配備不合格 |
| PT-OPS-INBOX-005 | realMainBridge | actual Java mainの負入力をwrapperへ接続し、JVM0＋receipt70→OS exit70、stdoutへraw値を出さない |
| PT-OPS-INBOX-006 | baseUnitAndSyntax | 全base directiveを独立期待表と一致、read-only/専用identity/30min/no-auto-SIGKILL/正しいwrapper、systemd-analyze verify成功。実unit起動ではない |
| PT-OPS-INBOX-007 | previousProfiles | base4 credential（db-inbox-inspector/maintenance-owner/current AES二種）＋optional0/1/1/2の4profile、固定ID/pathと重複なし。空fallback/省略source/広いcredstore検索なし |
| PT-OPS-INBOX-008 | releaseClasspathAndIsolation | API jar＋runtime lib classpath、PG driver runtime依存、固定JVM/native/UTF8/UTC/heap flags、任意command/eval/env上書きの禁止、release layoutとの追跡 |

## 3. 正式証跡

SSC-053/BUG-137/YKT-107追補: PT002に固定od executableだけ一時test fixtureへ差替える非zero faultとJava executable欠落を追加。本番にはtool差替え入力を持たせない。PT003は正規15byteの全16挿入位置へNULを入れ、高bit/余分LF等と合わせ29入力をすべて50とする。raw値をshell変数へ入れず、出力＋JVM status markerを固定odのhexへ変換して4独立vectorと比較する。50件の実tool/sh呼出しをmethod別にtargetへ保存し、正式clean verify後にcollector022が全件数を照合しsanitizeして採取する。Java test method数8と実tool呼出し50を混算しない。

root clean verifyの8 Java testとして実行し、002・evidence/manifest.jsonへ日時/環境/source/branch/command/exit、各IDの期待・実際、sanitized script trace/静的解析結果、unit profile対応、source hashを保存する。collectorは全8完全method名とfail/error/skipped/unknown/重複を検証し、他scopeと同run/source/hashへ束ねる。既存24 DB部品220 PTやbatch29 PTとは重複加算しない。PGPT/IT/ST完了を宣言しない。

## 借用JDBC属性検証の独立通常Port（2026-11-08）

ServiceDatabaseAdmissionPortTest/PT-OPS-DBPORT-001～015、SourceFile二physical（compiler enum switch helperを含む）、仕様3791/input500・実行前502/PG23652（manifest3f18a00ff151a9fb14d9f92a04efb8ea3c71061cd80116cf62c293ee512ec873）。main7aed/normal22084/static22086不変、new Testのcompile23670/static23672は完了、PMDraw6をnull negative4/standalone own thread2の各文脈で非該当・適用0/CS0、規則抑制0。元実DB Test/fixtureは未実行HOLD、当十五もこのsource保存時点ではまだ未実行。結果3792/PG23656で真正実行後に更新し、正式1964-53や実DB接続/起動の資格へ加算しない。BUG2491/YKT2229は新Test cursor式の修正前起票・23662before、修正内容以外token逆同値を23652で確認。

### 借用JDBC Port十五の限定実行完了

初23654全15成功/FESabort0、23656独立post0（9d40975e1b15b7737d4c9cc1d45336d5ed0aa14bb0c10a117f567e3d3b9ccd73）。通常Main L48/M5/C1/B32miss0、compiler生成$1は物理/CRCに含め標準filterによる分母0を3792へ明記、手動除外0。Main不変、実DB元Test/fixtureはHOLD、正式1964-53/工数null不変。仕様3791・sourcebfb6・BUG2491/YKT2229の限定是正/五対象非該当と初15実行を結合済。

## 接続source所有の独立memory Port（2026-11-08、実行前）

ServiceDatabaseSourcePortTest/PT-OPS-DBSRCPORT-001～014、3793/input506・23700preflight3638c2bb81209c86c19ed4dead4e1deb74098efc013ce5ecab8ac81ffbdd1659。existing package Connectorへ標準JDK proxyを提供、synthetic charだけで実Driver/DB接続/登録0。public defaultはconstructor/close/closed gateだけ、実接続はHOLD。Main7aed不変/normal22084/static22086再利用。SourceのCode一/abstract Connector NoCode一を物理scopeへ含める。compile23728/static23730は完了、Unit14はこのsource保存時点で未実行。初compile1/全原証拠とBUG2492～2495/YKT2230～2233の修正前起票を保持、結果3794/23704と分離。SchemaHistoryAdmission/Row/JdbcAdmissionFailuresは既同Main22670の全九証拠を参照し再演0・unique加算0。

### 接続source所有Port十四の限定実行完了

初23702全14FESabort0/真0、23704独立0 SHA77ac4912e39373967f603ea6c88ad89c9a369f2c82281d3f17af6ee588accc73、L66M16C1B24miss0/physical二・abstract Connector NoCode1/除外0。sourcebb416a7/Core7aed。八oracle反例・原compile1/修正前証跡・四BUG/YKTを3794へ結合、real driver/default connect/DB/Root/native/四held0。既Schema9は再演0/新unique0、正式1964-53/工数null不変。


YKT2387独立純値/非秘密解析 normal16の当Program結果は[4182_Web非秘密設定原七単体結果.md](4182_Web非秘密設定原七単体結果.md)。公開AAD9/設定7の内数を区別、全4physical限定四100/全project資格・actual4/DB/Rootとは別。


API非秘密設定原七の当Program限定結果は[4184](4184_API非秘密設定原七単体結果.md)。固定Main1の四counter100とruntime配備・実DB-MQ・全451を区別する。


HTTP metrics原whole28の当Program結果は[4188](4188_HTTPメトリクス原二十八単体結果.md)。全11physical/三実行可能source九code四100、自然NoCode/branch0は明示、actual exporter/network/全451は別。


閉host共通工具・群ownerの仕様/metadata結果は[4193](4193_閉host共通工具・群owner検証仕様.md)とPG28194/95/98。41 metadata/source checks・append順序確認は製品PT/coverageへ加算せず、初回必要profile runtime資格は未実施を保持する。


[MPOL8静的不足・通常PT未実施](4238_MPOL原七新一静的不足・通常PT未実施結果.md)。Main13/Test8 compileのみ、Missing1/生PMD79未分類、実PT0/coverage未測定、受入0。


WBS-P018-01公開source契約/独立期待値/TestIDは[4239_P01801全十六artifact契約・独立期待値対応.md](4239_P01801全十六artifact契約・独立期待値対応.md)。metadataのみ、新PT/coverage/正式受入0。


API Web設定原十四通常単体結果：[4242_APIWeb設定原十四通常単体結果.md](4242_APIWeb設定原十四通常単体結果.md)。通常whole14成功・target計測値/fullscope未網羅保持、実DB/Root/Backup資格とは別。


WBS-P018-02公開source契約/独立期待値/TestIDは[4243_P01802全五artifact契約・独立期待値対応.md](4243_P01802全五artifact契約・独立期待値対応.md)。metadataのみ、新PT/coverage/正式受入0。


署名原八新一通常単体結果：[4245_署名原八新一通常単体結果.md](4245_署名原八新一通常単体結果.md)。通常whole9成功・target計測値/fullscope未網羅保持、実DB/Root/Backup資格とは別。


WBS-P018-05公開source契約/独立期待値/TestIDは[4247_P01805全二十六artifact契約・独立期待値対応.md](4247_P01805全二十六artifact契約・独立期待値対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P018-06公開source契約/独立期待値/TestIDは[4249_P01806全二十二artifact契約・独立期待値対応.md](4249_P01806全二十二artifact契約・独立期待値対応.md)。metadataのみ、新PT/coverage/正式受入0。


HTTP所有原二新一通常単体結果：[4251_HTTP所有原二新一通常単体結果.md](4251_HTTP所有原二新一通常単体結果.md)。通常whole3成功・target計測値/fullscope未網羅保持、実DB/Root/Backup資格とは別。


Web稼働判定終端フラグ通常六結果：[4253_Web稼働判定終端フラグ通常六結果.md](4253_Web稼働判定終端フラグ通常六結果.md)。通常whole6成功・target計測値/fullscope未網羅保持、実DB/Root/Backup資格とは別。


Web停止原六新一通常七結果：[4255_Web停止原六新一通常七結果.md](4255_Web停止原六新一通常七結果.md)。通常whole7成功・target計測値/fullscope未網羅保持、実DB/Root/Backup資格とは別。


WBS-P018-07公開source契約/独立期待値/TestIDは[4257_P01807全三artifact契約・独立期待値対応.md](4257_P01807全三artifact契約・独立期待値対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P018-08.01,WBS-P018-08.02,WBS-P018-08.03公開source契約/独立期待値/TestIDは[4258_P01808三子全五artifact契約・独立期待値対応.md](4258_P01808三子全五artifact契約・独立期待値対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P018-09公開source契約/独立期待値/TestIDは[4260_P01809ログ主四認証関連四・独立期待値対応.md](4260_P01809ログ主四認証関連四・独立期待値対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-F03/1公開品質scope/不足条件: [PG29526](evidence/PG29526-f03-public-six-module-preparation-v1/manifest.json)、[対応表](../../../documents/400_PGPT/470_PMO/600_通常PGPT_20261106/1541_F03六module規約・公開対象・残HOLD対応.md)。原/1のみ、新PT/coverage/全F03/正式認定0。


F03公開source guard追補BUG2839: [PG29556](evidence/PG29556-main-delta-guard-public-metadata-v1/manifest.json)。原v1を保全し現Main105/当coreとの差0を独立に確認、新PT/coverage/正式0。


WBS-P018-03.01,WBS-P018-03.02,WBS-P018-03.03公開source契約/独立期待値/TestIDは[4263_P01803現行二十二Main・epoch許可所有launch契約.md](4263_P01803現行二十二Main・epoch許可所有launch契約.md)。metadataのみ、新PT/coverage/正式受入0。


StartupProofFrame元whole8の有限workerと全3physical四100は[4265](4265_起動proof原八同source・独立通常PT結果.md)、Core3f65/Testb2c2/PG30086・30088。実権限/起動全体/451未受入。


WBS-P018-04.01,WBS-P018-04.02,WBS-P018-04.03公開source契約/独立期待値/TestIDは[4266_P01804停止所有寿命十七Main・独立契約.md](4266_P01804停止所有寿命十七Main・独立契約.md)。metadataのみ、新PT/coverage/正式受入0。


停止snapshot原whole7有限workerと12値独立oracle・全4四100は[4268](4268_停止snapshot原七同source・独立通常PT結果.md)、Core3f65/Test1970/PG30122・30124。実停止/全451未。

## PT-F02-ARCH-013〜022 Framework所有の型付き検査

対象は ModuleDependencyAudit.forbiddenFramework。設計 SS311 §2・§3・SSC084／SSC088、SYS-011、WBS-F02-a。JDK 25.0.4／ArchUnit 1.4.2で合成6 JARのclass定義だけを読む。外部stubをcompile時のみに置き、製品owner・実サービスを含めない。fixture二世代の証跡を保存する。

- 013〜016でBootstrapからSpring JMS、Spring HTTP、JDK HTTP、Jakarta JMSの直接型参照をそれぞれ拒否。
- 017〜019でAPI／BatchのMVC注釈、APIからserver response型の参照をそれぞれ拒否。
- 020〜022でBootstrap JDBC、API業務JMS、Batch Artemis管理を許可。

走行は `python3 -B evidence/01_PT/018_NK-OPS-001/input/5283_f02_framework_fences.py before|after`（いずれか一回用ディレクトリ）、独立照合は `5284_f02_framework_fences_post.py`。手書きownerと型の期待対を終了receipt、監査stdout、class SHAと照合。禁止fixtureの監査exit1は想定。実行結果、sourceとhashはPG40118へ。動的製品PT・coverage対象外。

## PT-F02-ARCH-023〜026 ControllerのSpring JDBC直接依存

SS311 §5.2、WBS-F02-a、ModuleDependencyAudit.jdbc。JDK25.0.4／ArchUnit1.4.2。合成JAR6・10物理、外部fixture型はcompile専用。023はJdbcTemplateの生成と直接呼出し、024は名前がControllerでないRestController注釈付クラスからのJdbcOperations呼出しを禁止。025はControllerでない技術取得、026はControllerからのfacade呼出しを許可。手書きの型対と生監査stdoutをPG40146で独立照合。実行は input/5290_f02_controller_spring_jdbc.py の before/after、検証は input/5291_f02_controller_spring_jdbc_post.py。

## PT-P01808-BIN-018〜023 固定JaCoCo writerの長さ・padding

SS354、WBS-P018-08.03/2、jacoco_readonly_exec_subset.decode。固定0.8.15 writerをjavapで読取照合。独立hexで冗長な0／3の符号、対象／対象外のunused bit非0を拒否。空、127／129、全8bitと端数9bitで正規符号の件数を保持する。実行は input/5292_p01808_exec_canonical_run.py red/green、照合は input/5293_p01808_exec_canonical_post.py。製品nativeを採取しない。

## PT-CHR-PREFLIGHT-FS-001 実FileStoreの正常入口

SS355、WBS-P020-01.01/2-b、BUG3311。GateCli.mainのpreflight分岐と二引数preflightを、実行先の専有run・JDK25で確認する。PG40162のMain 6とSDK pinを用い、compileの17物理を再照合する。引数は通常の `preflight <owned-output.json>`。Runtime rootを実行先の承認済みlocal実FS上に置き、独立したstatvfsと真正FileStoreの双方で20GiB以上。Current source形状、asset、0600の非秘密fixture、Caddy/pgCtl等の非実行placeholder、閉じたloopback URLと別非特権portは全て専有run下の合成物とする。期待はexit0、JSONのPASS、空failures、実測freeBytes、0600、既定allowlistと当runのpath。GateCliが起動する対象は当Java工具のみ。実DB／Current／NK／Caddy／nativeは起動しない。開始PID／boot、各入力SHA、probe独立sessionと終了codeを記録し、実行前の準備や低容量での未実行は成功へ算入しない。

## PT-F02-ARCH-027〜030 APIのrepository方向

SS311 §3、WBS-F02-a。JDK25／ArchUnit1.4.2の合成6 JAR。027は通常persistence、028は監視persistenceのrepositoryからapplicationへの直接呼出しを禁止。029は順方向、030はJDKの局所補助呼出しを許可。input/5302_f02_monitoring_repository_canaries.pyのbefore/afterを、input/5303_f02_monitoring_repository_post.pyで独立照合。製品JAR・実DBは対象外。

## PT-C02-TEXT-010〜015 終了対象範囲の文面

SS341 SSC101、SS342、WBS-C02。現14の凍結設定を用いて固定対象8のKillMode明示または継承を判定。010は現文、011はArtemis誤指定、012はCaddy明示値欠落、013はAPI誤上書き、014はWeb重複、015はWebの正規明示値。API/Web未記載は実効未観測。実行は input/5305_c02_killmode_canaries.py before/after、独立照合は input/5307_c02_killmode_post.py。systemd・サービス・実停止なし。

## PT-F02-ARCH-031〜037 Protocol・StorageのHTTP型依存

SS311 §2、SYS-005、WBS-F02-a、BUG-3345／YKT-2711。六合成JARのfield型をArchUnit 1.4.2で調べる。031/032はProtocolのHttpRequestとHttpExchange、033/034はStorageのHttpResponseとHttpServerを各拒否。035のProtocol URI、036のStorage Path、037のAPI HttpExchangeには当違反がない。各期待は設計のHTTPモデル禁止と既存ライブラリ／管理HTTP責務から固定し、JUnit本数や製品JARへ加えない。実際の同class bytes、前後exit、各FINDINGと静的後条件を独立照合する。
