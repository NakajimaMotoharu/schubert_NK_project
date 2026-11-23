# 1721 Web technical outbox観測経路 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171 MON003/005/010～013/UI242252/SS324332351/PG-D572。対象はWebOutboxMetricRecorder（Status/Observation含む）、WebOutboxObservationRepository、WebOutboxMetricCollectorの一接続経路。三Mainと対応PTを並行作成し、実DB・driver接続・業務schema/dispatcher/claim/send/再送・暗号payload/鍵・実時計/サービス/Root等を操作しない。

Web storeは既V003/既WebLogOutboxRepositoryのschubert_web_session.web_log_outbox、Status PENDING/SENT/ERROR。固定SELECT status/COUNT(*)/MIN(created_at)一statementのみ。借用ConnectionはautoCommit=false/readOnly=true/READ COMMITTEDを確認し、設定/commit/rollback/close/abort/別接続をしない。query timeout1秒、JDBC4.2 OffsetDateTime→UTC、渡されたasOfからDurationを算出。group rowはcount>0/非null/既知status/重複なし/created非null・futureなしを厳密検証し、statement/resultを全closeしてから返す。成功した完全group resultの未出statusだけをknown0/Duration.ZEROへ補完し、途中失敗を空DBへ変換しない。

Observationはcount三longとage三Durationのimmutable record。負count/負age/null age・count0に非zero ageを拒否し、count>0/age0は正当な同時刻として許容。age秒はgetSeconds+nanos/1e9でlong nanos累積overflowを作らない。RecorderはDEBUG固定六Gauge（rows/oldest×status三、store=WEB）だけ、unknownはNaN/Optional.empty、完全known0は0として区別。STANDARDは登録/保持0。単一AtomicReference publicationはsnapshotとして整合するが、別々のGauge scrapeが多meter transactionになるとは主張しない。借用registryの部分登録/取得故障を補償・再試行・closeしない。

Collectorはprivate owner lock内でread→complete Observation→publication→返却。STDはrepository未呼出。SQLException/Runtime/Errorはmetricsをmissingへした後、同じThrowableを再throwしNPEを正常化しない。外側期限/実connection唯一性/permission/scheduler/asOf/source真正性を認証したものではない。

| Test ID | Program/観点・独立期待値 |
|---|---|
| WEBOBXMET001 | Recorder: 固定六Gauge/name/type/WEB・三status/初期NaN、known count2/0/1とage5.25/0/.5秒、snapshot同一・全値 |
| WEBOBXMET002 | Observation: 各count負-1/MIN・各age負/null・zero count非zero age拒否、正countzero age/全zero/MAX long/Duration境界・非overflow秒 |
| WEBOBXMET003 | Status: 三typed literal/strict parse/未知・空・小文字・null、values配列独立/valueOf既知・未知・null、新生成2 |
| WEBOBXMET004 | record/missing: null/nullStatus拒否・既値不変、missingで六NaN、既Observationのgetter/age/count全status、STD登録/保持0・未知mode |
| WEBOBXMET005 | SDK第二Gauge factory Runtime/Error: 同一identity・prefix1/borrowed close0/caller finally close1 |
| WEBOBXMET006 | 独立record九生成contract: 六typed accessor/equals同値・各field違い/null/型違い/hash整合/固定toString、当source ordinaryと非初期化javap |
| WEBOBXMET007 | 並行64事前fixtureと別owner: 返却snapshotは全体fixtureの一つ/混合tupleなし、六Gaugeを同時transactionと誤認しない |
| WEBOBXMET008 | foreign Counter同name/labelをGaugeへ置換拒否、元identity/値/borrowed ownership不変 |
| WEBOBXDB001 | Repository: 固定SQL（technical tableのみ）/timeout1/JDBC4.2 UTC・順序違い三row→literal counts/age、全result/statement close・借用tx不変更 |
| WEBOBXDB002 | 空/欠statusの完全result→known0・asOf同時刻age0、未出statusだけ補完 |
| WEBOBXDB003 | 境界: MAX count/異offset同Instant・小数age/過去最大近傍、nanos変換overflow/丸めclampなし |
| WEBOBXDB004 | null connection/asOf、autoCommit/readOnly/isolation各不適合、prepare/query前拒否・設定/tx操作0 |
| WEBOBXDB005 | null/未知/空/小文字status・duplicate status、negative/zero/null COUNT、null/future MIN拒否・partial return0 |
| WEBOBXDB006 | prepare/timeout/query/next/getter SQLExceptionの元identityと取得済みresourceだけclose、借用close0 |
| WEBOBXDB007 | statement/result null・読取Runtime/Errorを異常のまま伝播、empty成功へ変換0 |
| WEBOBXDB008 | result/statement close故障とsuppressed順序、未close成功/元故障の紛失0、原SQL契約保持 |
| WEBOBXDB009 | 全row順序/完全性と呼出trace、余分なcolumn/payload/key/user/更新SQL/秘密取得0 |
| WEBOBXDB010 | 反復別Connection/独立asOf/完了前publishなしのreadonly helper、query/close各一回・ownership不変更 |
| WEBOBXCONN001 | Collector: read中未publication→取得後全六値/同一Observation返却、owner-local完全性 |
| WEBOBXCONN002 | 完全emptyとmissing区別、再取得後snapshot復旧/既別owner不変 |
| WEBOBXCONN003 | SQL/Runtime/Errorの元identity・既snapshotをmissing/NaNに、失敗をknown0へ変換0 |
| WEBOBXCONN004 | constructor/null connection/asOf/未知mode、STD repository/SQL/登録未呼出 |
| WEBOBXCONN005 | 取得済みresource close故障もmissing・元Throwable/借用Connection保持 |
| WEBOBXCONN006 | 後続workerが先行ownerを待つことの実確認、read→publicationまで直列・有限future/finally解放 |
| WEBOBXCONN007 | 64呼出前独立fixture/別owner、全観測整合・未知/成功の順序を事前固定、並行借用Connection共有資格は推定0 |
| WEBOBXCONN008 | SDK factory部分失敗でrepository未呼出/借用registry保持、constructor失敗を起動成功にしない |

上表は着手時の26新Test ID（Recorder8/Repository10/Collector8）。期待値はDDL/SSの固定literal・独立JDBC proxy/SDK/事前fixture/UTC時刻算出を使用し、Production methodからexpected生成0。既API実装は参考素材だけでWebからAPIへmodule依存させない。coverageが不足なら期待値を緩和せず、追加必要ケースを実績と分けて追記する。

次はsource固定→7942正常六Main/Test compile-package＋正規test classpath metadata（PT0）→7944明示safe10suite当Web77（新26＋必要既51）→7946独立20Java/実18＋metadata1/CRC0/四100/static→7948全1788physical（当Web19/歴史API35-Batch65）→7950全135delta/119追加physical→7952生成既16＋新record9＋Status2=27/raw全理由→7954公開scan。元API162/Batch261/Web51の別source成功を転用しない。1722結果へ全source/run/環境/日時/branch/command/exit/XML/入力/独立期待値/実際/counter/CRC/BUG/hashを結合する。

group1945/開始3-5-9pp上限10/fresh10残90/reset1793382075/PG7940fresh receipt。正式1964/53・原190新受入0/QA051final/PTALT0/whole451-native-CHR・全actualHOLD、原保全物/stash7/Scenario3/Currentbaselineを維持。原/v4/v5・旧markerlast27区間/共有累積/専有N-T/工数null/90再基底化0。1720の「既1730等」は既存477/478工程方針を指す文言誤記で、新しい資料/工程へ変更した意味ではない（原1720/hashを保全してここで訂正）。

## 2026-11-24 排他方式の是正

BUG-3745／YKT-2929。取得済み資源の解放から同ownerの完全値公開を私有ReentrantLockに保持し、正常・早期return・元Throwable再throwの全てでfinally解放。借用Connection、read-only契約、取得資源の順、公開後の値と既WEBOBXCONN001～008の独立期待を維持する。PG43812の局所scopeで元指摘と生四指標を照合。実DBを使用しない。

WEBOBXCONN006は自PT二workerのIDだけを使い、Connection代理の先行close待機中の保有者と後続待機先を一致確認する。後続文prepare 0、公開空、先行値、終端値と双方の回収を維持する。
