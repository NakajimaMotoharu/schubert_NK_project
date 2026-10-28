# 2503 JUnit共通reporter 工具実装・自己試験仕様

2026-10-29、PG-D817予定、START2882/開始0.5/2/4pp cap10/freshused27残73/reset1793774153。source17ab52b25不変更、保存26f3c2a8cb958c6a370f7fca831140a9f38b02ed（push36794終端/remoteは別確認）。主F03のtool改善費で新機能/元計画消化/新Product PT/coverage/受入に数えない。

## 目的・不変更条件

BUG2075ではclass選択と四summary件数を別々にコピーし工具失敗・必要再試験が発生した。新SharedSelectedJunitReporterV1は一つのMap<class,count>をdefensive copyし、合計をMath.addExactで導出する。各suite件数・一意class/methodとfound/started/succeeded、FES/abort/container条件の全成立だけ成功。class名/正件数/非空Mapと新only XML directoryを検査する。古い実行済helper/共通hostやsource/runを変更せず、既scoped_prometheus_hostのEXTRA_TEST_SOURCESへ新共通Javaを明示追加して使う。今後の選択binderは小さい固定Map wrapperとし、元whole source/hash/件数のpreflightを保持する。

通常JUnit engine/公式SDK/全caseの独立post/同source/exec/session/CRC・coverage条件を緩和しない。既結果は同じshared reporterを通すために再実行しない。新工具の自己試験だけを先に行い、次の未資格ordinary wholeへ適用する。source/Main/Test/上位設計不変更、モデル/料金/券/VM/Root/DB/MQ/HTTP/鍵/Graph9/held二工具の変更・操作0。

## 工具用fixture・独立期待

ReporterToolFixturesV1は新規の最小JUnit fixtureで、reporterが成功/失敗/skip/abort/not-runを正しく記録・拒否するためだけのもの。空の成功method/意図的例外/Disabled/Assumption/BeforeAll失敗は工具入力であり、Production仕様の試験や意味のないcoverage加点には使用しない。固定Driver以外のclass/profileは自己試験で選ばない。

|profile|期待run exit|独立期待|
|---|---:|---|
|passing|0|found/started/succeeded2、一suite二case、FES等0|
|two-passing|0|合計3/二suite、各2/1・一意case|
|wrong-total|1|実二成功でも期待3に不一致・不合格|
|wrong-distribution|1|合計3は一致しても期待1/2と実2/1が違い・不合格|
|failing|1|一case failure、元messageをXMLへ出さず型/限定frameのみ|
|skipped|1|一skipをPASSへしない|
|aborted|1|一abortをPASSへしない|
|failed-container|1|found1/started0/containerFailed1、未実行をPASSへしない|
|empty-tests|1|found0/started0、予定1未実行をPASSへしない|
|empty-map|1|JUnit起動前・XML directory未作成で拒否|
|zero-count|1|JUnit起動前・XML directory未作成で拒否|
|invalid-name|1|JUnit起動前・XML directory未作成で拒否、外側pathを作らない|

新SLOTと固定JDK25.0.4/公式JUnit七jarだけでjavac -proc:none/-Xlint:all/-Werror、各child JVM有限30秒で実行する。Product sixjarはclasspathへ入れず、アプリclass/methodはロード・実行0。既公開13692のdependency hashから七jarの実byteだけ再使用し、元Product成功/execを転用0。元stdout/stderrは自己fixtureの新only private SLOT、公開はexit/安全summary/XML・hashとmanifestだけ。failure text sentinelがXML/summaryに無いことも検証する。各期待1は意図した工具negativeであり実行PTのPASSへ数えない。失敗や想定外の結果を再解釈して成功化しない。

工具自己試験が合格し独立receipt照合が完了してから、次の必要な既wholeを具体call tree/fixture/権限/副作用でPT_DEFAULT判定し適用する。候補のMorningExpiryObservationInvariantTestは全180行読取・ExpiryReceiptFixtureは手書きstateとinjected checker/supplierの107行、まだMain Gate/record全到達bodyを照合していないため未判定/未実行。実Root/permit/サービス起動の許可にはしない。正式1964-53/17-190/工数null/QA051final・全HOLD/全保全物を維持する。
