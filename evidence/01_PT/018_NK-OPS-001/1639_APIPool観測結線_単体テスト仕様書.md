# 1639 API pool 借用観測→metric結線 単体テスト仕様書

NK-OPS-001/P01809/共有C07追加費0、RD171/UI252/SS342351/PG-D543。DbPoolMetricObservation.observe/constructor、DbPoolMetricCollector.constructor/collect/snapshot。自己所有HikariPoolMXBean/HikariConfigMXBean proxy（製品7.1.0 interfaceの型だけ）とSDKだけ、実HikariDataSource/HikariConfig生成/JMX lookup/DB接続/management controls/VM/Root/配備/鍵等操作0。

| Test IDs | 独立fixture・操作 | 期待値 |
|---|---|---|
| POOLREAD001～002 | 固定active3/idle5/pending2/max8、真0/max1 | 三pool getterとconfig maxを順序固定各一回、counts原値/真0、他getter/control0 |
| POOLREAD003 | 四count各負/max0 | 四getter完了後Optional.empty、未知を0へ変換0 |
| POOLREAD004 | null pool/config | 全getter前拒否・partially read0 |
| POOLREAD005 | 全四getter Runtime/Error故障 | 同じ故障/再試行・format・cause graph走査0、後続getter0 |
| POOLREAD006 | 四int最大 | 原long2147483647、sum/wrap0/跨getter同時性を推測0 |
| POOLREAD007～008 | 64並行/後続値変更・別owner | stateless観測の値非混同/原snapshot不変・全control/close0 |
| POOLCONN001～002 | DEBUG初期→固定値→invalid→真0 | 全4series/API固定、初期/invalidはNaN、同complete返値を保持、真0別扱い |
| POOLCONN003 | 全getter Runtime/Error・循環/非formatable | 元故障伝播/全未知/次成功回復・再送0 |
| POOLCONN004～005 | STANDARD/null constructor/入力/未知mode | 詳細getter/登録/保持0・境界拒否、null入力で既snapshotを消去0 |
| POOLCONN006～008 | 二caller latch/64並行/別owner | owner内getter→公開直列、complete返値/四series固定・別owner値不変/close0 |

全rowのoracleは固定literal/getter call sequence/SDK名・key・NaN、productionからexpected生成0。未知invalidをOptional.emptyへ、provider故障は非成功で元throw。製品getterは非原子的のためactive+idleとmaxの同時整合/total getter等を追加しない。maximum>=1以外のpool上限や運用制御を推測しない。全getterはfakeへの通常Java呼出で実pool管理ではない。

既API POM Hikari7.1.0を再利用しProduction依存版変更0。既installed Jar SHA2be45c641b841e81df87292e181f2c203500c5f0e9a1676f135927387f3cf40b/POM SHA5b8df2699933ea898aa50d4def4fc2226b15e6f4d993e373a16070f7ed480216、M2 com/zaxxer/HikariCP/7.1.0・POM upstream https://github.com/brettwooldridge/HikariCP。取得/導入0。host harnessに当一dependencyだけ追加し、親/format/lint/Werror/NullAway/SB/coverage四1.0/実PTを厳密XML意味比較/負改変で保全する。既十二guardのharness旧byteを新byteへ読み替えない。

新16＋必要既API32=48PT6suite/全13Java/実10＋metadata1・全1733physical/75sourceは未実測予定。元PG7362/7364以降へsource/branch/OS/JDK/tool・command/time/終了/XML/実counter/静的/BUG-SSC/evidence path/hashを保存。SDK4Jar＋既Hikari一Jarは個別pinし、歴史Batch/Webの四SDK/旧成功は当sourceへ合算0。actual Hikari/DB/management/identity/sampling/outer有限collector/alert/Root/exporter/native/CHR/全体451は未受入HOLD、正式1964/53・歴史17/別source新7・原190新受入0/工数null/QA051final/PTALT0維持。

BUG-3736／YKT-2929再試験。POOLCONN001～008の既期待値を維持し、読取から公開までの一所有者の排他、失敗後の同一例外と全未知、後続成功回復、STANDARDの非観測を自己所有SDK fixtureで確認する。同期の実装をprivate ReentrantLockとfinallyへ変更。PMDの同期1指摘と広いcatch二指摘を個別評価し、原XML・source・単一execを保全する。
