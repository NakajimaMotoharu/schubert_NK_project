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
