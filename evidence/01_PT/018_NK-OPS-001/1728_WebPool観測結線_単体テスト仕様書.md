# 1728 Web pool観測結線 単体テスト仕様書

NK-OPS-001/WBS-P018-09/C07/RD171 MON005010013/UI212226252/SS311342351/PG-D579。1727の限定source gapを基に、WebDbPoolMetricRecorder/Observation/CollectorをWeb module内で実装する。Web→API依存なし、SS/実Pool設定は変更しない。各三Mainと同名Test、下記24Test IDに対応する。

## 共有契約・独立fixture

DEBUGだけ固定nk_db_pool_connections/GAUGE、labelはservice=WEB/state=active,idle,pending,maxの4series。各瞬間値は独立でactive+idle<=max等の関係を捏造せず、negative/maximum0はinvalid/missing。immutable Counts(long×4)は非負/positive maxをconstructorで保証。供給longのIEEE754表現はLong.MAX_VALUE→2^63を独立期待し、正確long snapshotを保持する。未知NaNと実0を区別、STANDARDは登録/保持/getter読取0、null/未知mode/stateは先行拒否、registry所有はcaller。

Observationは借用HikariPoolMXBeanのactive/idle/pending、HikariConfigMXBeanのmaximumを固定順に4回だけ読む。実HikariDataSource/Poolを構築/open/getConnectionせず、JMX lookup・control・config/credential getter/setterを禁止したinterface-only Proxyを使う。実owner/role/source/asOf/generation認証を推定しない。WebJdbcPoolの実max2/min1は既source/admissionの責務で、監視は取得したactual正値をclampしない（診断vector max8等は実Web設定の承認ではない）。

Collectorはprivate owner lock内でread→完全publication。invalidはunknownへ、取得Runtime/Errorはunknown後に同一Throwableを返し、normalへ変換/cause walk/format/retry/closeをしない。null入力はcaller契約違反として観測前拒否、既有snapshotを消さない。別Gauge scrape横断atomic性は保証しない。

期待値は固定literalの3/5/2/8・0/0/0/1・Integer.MAX=2147483647・longMAX→binary64 2^63、型付きclosed enum定数と独立record hash94248/固定文字列から作る。production methodをexpected生成に呼ばない。Proxyの許容getter名は固定4個のみ、それ以外はAssertionErrorで失敗。source/callerの秘密・実接続値をfixtureに含めない。

## Program別Test ID

|Program/class|Test ID|目的/操作と期待値（独立根拠）|
|---|---|---|
|WebDbPoolMetricRecorder|WEBPOOLMET001|DEBUG4series/型/全tag集合/初期NaN、4stateのliteral順序・enum values/valueOf/clone/null/未知を確認|
|同|WEBPOOLMET002|Counts3/5/2/8・全getter/value/四Gaugeをliteral照合、record equalsの各成分差/null/他型/hash94248/toStringを独立検証|
|同|WEBPOOLMET003|実0はknown、missingはNaN、後の1で回復、元tupleは不変|
|同|WEBPOOLMET004|STANDARD0/0保持、null/counts/registry/modeと未知modeは拒否|
|同|WEBPOOLMET005|四負/最大0,-1/unknown-null state・longMAX全値/SDK2^63、null record後も元snapshot保持|
|同|WEBPOOLMET006|64自己所有workerの二immutable tuple、partial混成なし/label4のまま|
|同|WEBPOOLMET007|2件目Gauge factory Runtime/Error時は同一例外/1件残留/caller close前0・後1|
|同|WEBPOOLMET008|別owner値独立、1000record/missingでもseries4、未知label追加なし|
|WebDbPoolMetricObservation|WEBPOOLREAD001|四getter順/各1回・3/5/2/8の独立値、control/credential未読|
|同|WEBPOOLREAD002|0/0/0/1はknown Optional、呼出し順4を維持|
|同|WEBPOOLREAD003|active/idle/pending負・max負/0の5入力をEmpty、0へ変換せず全getter順確認|
|同|WEBPOOLREAD004|pool/config/null両方を先行NPE、getter0|
|同|WEBPOOLREAD005|4getter各位置×Runtime/Errorのidentity、後続getter/再試行なし|
|同|WEBPOOLREAD006|全intMAX→2147483647longを正確保持、sumしない|
|同|WEBPOOLREAD007|64独立Proxy入力の返却tupleと入力同一性、可変state共有なし|
|同|WEBPOOLREAD008|getter後変更/別ownerでも返却immutable tupleは不変|
|WebDbPoolMetricCollector|WEBPOOLCONN001|read4回→同一complete tupleを4WEB Gaugeへ結線|
|同|WEBPOOLCONN002|旧known→max0でunknown→実0で回復、旧tuple不変|
|同|WEBPOOLCONN003|4getter×cyclic/unformattable/Errorでunknown/同一Throwable/再試行なし、次validで回復|
|同|WEBPOOLCONN004|STANDARDで悪意getterも未読、入力nullはNPE、保持0|
|同|WEBPOOLCONN005|constructor各null/未知mode・collect nullは先行拒否、既snapshotは不変|
|同|WEBPOOLCONN006|同owner first getterで有限latch保持、second threadが実BLOCKEDになりgetter未入場→順にpublication/全future回収|
|同|WEBPOOLCONN007|64並行Proxy入力を各正しいcomplete tupleで返却、series4|
|同|WEBPOOLCONN008|別ownerと100連続供給で値独立・series4、control/close/credential読取0|

並行fixtureは自身のthreads/latchesだけで、全待機とfuture回収に有限期限を付ける。失敗・flaky・skipped・not-runを合格にしない。NPEをcatchして正常扱いしない。未実装TDD最初の失敗と実装済み障害を区別し、後者は修正前915/916へ実番号確認の上起票する。

## 実行・品質・計測

予定は新24＋必要既Web90を同source114/14。正常六Main/Test compile＋NullAway/format/正規classpath/PT0→明示14safe-class JUnit→全29Java/実25class＋metadata2の四counter100/CRC0/一exec/static→全1799physical/147source-130追加physical、source変更は前141から不変141/新6→生成新2type9method＋既8type27method・全raw個別理由/metadata/owner負例/秘密scan。Hikari7.1.0/SLF4J2.0.18は既正常Web依存と固定Jar hashに束縛し、Micrometer4とtyped-interface依存を区別、外部ライブラリのcoverageへ移転しない。

実行command/OS/JDK/tool/version/branch/対象commit/開始終端・coverage/結果/BUG/エビデンスpath/hashは1729と各公開manifestへ結合する。正常六compileのPT0はUNRUN、同sourceが変われば旧sourceの成功を転用しない。Program別24IDをcase/class/method・要求・仕様・証跡へ一意trace。秘密・rawセッション/token/key/password/実DB結果は取得/保存しない。

groupP01809_WEB_POOL_OBSERVATION_V1、PG8120 fresh receipt/開始3-5-9pp・cap10。原-v4-v5/既usage38de08c8/旧markerlast27区間と共有累積null/90再基底化0・実token/PGPT-PMO配賦/工数null維持。元製造24新IDと必要既90再資格・追加発見/手戻り/toolを分離する。正式1964/53/原190新受入0/QA051final/PTALT0/whole451-native-CHR/全actualHOLDは不変更。collector/kernelのPG/PT完了だけを実pool/source/scheduler/exporter受入へ拡大しない。

## 2026-11-24 排他方式の是正

BUG-3738／YKT-2929、WBS-F03/2-2-b。WebDbPoolMetricCollectorの借用観測から公開までは同一の私有ReentrantLockで直列化する。正常、STANDARD早期return、供給RuntimeException／Errorでfinally解放。WEBPOOLCONN001～008の元合成proxyと全期待値を保持し、同一runでL/M/C/Bを採取する。PG43806で同期指摘を修正前後比較する。元例外を保持するPMD catchの生結果と全451の未検証を別計上する。
