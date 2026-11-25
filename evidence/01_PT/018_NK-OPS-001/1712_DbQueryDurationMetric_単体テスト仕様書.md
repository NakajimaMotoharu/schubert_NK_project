# 1712 DB query duration metric 単体テスト仕様書

2026-10-24 BUG1676/YKT1427是正追記（下記開始計画を履歴保持）: 元source a2d/7830は真正verify1・138中6failure、7834compile0/PT0。fixed-boundaryのceil(long)量子化を避けるためpublishPercentiles(.95)を明示しdouble histogramを選択する。DBTIME002の独立小数CDF/秒sum/max/2MAX期待値は不変更。DBTIME001/005は四primary SummaryとSDK補助Gauge（各五le＋一phi=.95）を全量検証し、部分登録もprimary1＋補助6を厳密確認する。p95設定要求/自己所有SDKの表現は確認するが実exporterの公開/p95品質は未受入。変更後7844当138/17→7846独立/7848正常六compile→7850物理→7852trace→7854review→7856scanで1713へ記録する。元失敗/元工具はb3c8e7449へ保全、群1934/3-5-9pp上限10の手戻りで見積付替え0。

NK-OPS-001/P01809/C07/RD171 MON006・010～013/UI252/SS331332351/PG-D568。DbQueryDurationMetricRecorder constructor/record/detailedMetricsRequested・Query/Outcome parse/values/valueOf。query_idは既AsyncJobCountRepository.readのSTATE集計をASYNC_JOB_STATE_COUNTS、既OutboxObservationRepository.readのstatus件数/最古をOUTBOX_STATUS_COUNTS_OLDESTとする内部閉二値。outcomeは供給SUCCESS/FAILURE二値。SQL文字列/parameter/任意ID/例外をlabelへ受けずDEBUG固定4series/STD詳細登録0。これ以外の業務SQL/全DB監視や実query hookは本群未受入。

Micrometer1.17.1のDistributionSummaryをbaseUnit seconds/percentile histogram要求true、観測bucket .001/.01/.1/1/1.5秒として使用する。bucketは低遅延観測点と既1秒query timeout/1.5秒query budgetの参照点であり、新しい応答合否/alert/SLO制御ではない。long nsをdouble除算で秒へ変換、long ns累積のoverflowを導入しない。実Prometheusのhistogram exposition/bucket/default追加分・p95/clock/asOf/DB/tx所有は別未受入。使用SDK APIは既pinned Jarの非初期化javapで確認、導入/依存変更0。

| Test ID | 目的/fixture・操作/独立期待値 |
|---|---|
| DBTIME001 | 手書Query二×Outcome二の4series/SDK summary型・baseUnit seconds/label key2・初期count/sum0、histogram flagと固定五bucket設定を取得factoryで確認 |
| DBTIME002 | 各pairに0/1ns/0.5s/1.5s→count4/sum2.000000001s、五境界CDFを独立入力から確認。別fresh registryのMAX ns二回→count2/sum1.8446744073709553E10s finite、long wrapなし |
| DBTIME003 | 四typed enum literal/strict parsers・未知/空/lowercase/null、values配列独立/valueOf既知/未知/nullを直接検証、生成新4method |
| DBTIME004 | 両modeでnull query/outcome・負-1/MIN拒否/既値不変、STD全pair登録/record0、constructor null/未知mode CONFIG_INVALID |
| DBTIME005 | 第2summary factory Runtime/Error同一identity・呼出2/残1/close0、caller finally close1 |
| DBTIME006 | record前/増分後のRuntime/Error同一再throw・呼出1/partial count-sum保持/補償・retry・close0 |
| DBTIME007 | 64fixtureの整数ns/count/maxをproduction前に独立集計、全4series/有限future/別owner0.25s独立。浮動小数点sum tolerance1e-12は1ns差を検出可能な幅、時計は自己所有固定fixture |
| DBTIME008 | foreign Counter同seriesをSummaryへ置換せず例外・同一meter/値7/close0 |

新8＋必要既API130を当138/17予定、7830 ordinary→7832独立(34Java/実28＋metadata1)・7834正常六compileを別snapshot→7836全1777(当API29physical/歴史Batch65-Web14)→7838全123delta/108追加physical/歴史元Stepのcurrent移転0→7840生成新4＋既41=45/current ordinary/raw全理由→7842公開scan、1713結果へsource/run/実日時/OS-JDK-tool/branch/command/exit/XML/input/期待/実際/CRC/四coverage/BUG/hashを結合。SQL/接続・実時計/DB/Root/VM/配備等操作0、SDK4＋API専用2/既protocol依存は既版を再利用・変更0。

開始3/5/9pp上限10/fresh receipt→event1934、原-v4-v5/旧markerlast27区間/累積・専有N-T/工数null/元90再基底化0。期待値は固定literalとfixture整数nsの独立算出、production methodでexpected生成0。正式1964/53/原190新受入0/QA051final/PTALT0/whole451-native-CHR/actualHOLD維持。

BUG-3882／YKT-2997。DbQueryDurationMetricRecorderTest#dbTime007の整数期待・8worker／64件・元期限を維持。workerの有限終了の失敗を一次例外に付随させ、fixtureが所有する二registryは逆順で閉鎖。現版3件の終了は[PG45498](evidence/PG45498-current-duration-and-message-fixture-owners/manifest.json)。実監視は別。
