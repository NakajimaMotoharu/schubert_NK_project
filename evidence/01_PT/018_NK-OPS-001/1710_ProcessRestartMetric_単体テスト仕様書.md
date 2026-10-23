# 1710 Process restart metric 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171 OPS012/MON008・010～013/UI252/SS342351/PG-D567。ProcessRestartMetricRecorder constructor/record/detailedMetricsRequested、Reason.parse/values/valueOf。既AlertLifecycle.Service六値と内部閉Reason NONZERO_EXIT/SIGNAL_EXIT/OOM/UNKNOWN四値だけでDEBUG24counter/STD詳細0、metric `nk_process_restarts_total`/label service,reason。UNKNOWNは**restartが起きたという供給eventの原因不明**だけで、process/観測欠測からrestartを推論しない。rate-limit到達は再起動抑止であってrestartを意味せず、このcounterを自動発火しない。実source/Unit/boot/Invocation/原因同定・exactly-once/永続値は未受入。

| Test ID | 目的/fixture・操作/独立期待値 |
|---|---|
| RESTARTMET001 | 手書reason四×service六の全24series・Counter型/label key2・初期0、PID/ID/path/例外文面なし |
| RESTARTMET002 | 全pair一回＋三回→各4、NONZERO_EXIT/WEBだけ追加→5、他4/系列不変 |
| RESTARTMET003 | 四literal→typed定数/strict parse、空・小文字・未知/null拒否、全values/配列分離/valueOf/未知/null、生成2独立直接契約 |
| RESTARTMET004 | 両modeのnull reason/service拒否・既値不変、STD全pair登録/増分0、constructor null/未知mode CONFIG_INVALID |
| RESTARTMET005 | 第二factory Runtime/Error同一identity・呼出2/残1/close0、caller finally close1 |
| RESTARTMET006 | increment前/後のRuntime/Error同一再throw・呼出1/partial増分保持・再送/補償/close0 |
| RESTARTMET007 | 64caller fixture pairをproduction前に独立集計、全24期待値・有限future/別owner7/系列24不変 |
| RESTARTMET008 | foreign Gauge同seriesをCounterへ置換せず例外、同一meter/値7/close0 |

ReasonはSS351のSystemd/Java異常の内部供給分類でraw code/message/PID/Unit名を受けず、実cause解析や新しいsystemd動作を追加しない。Service六値は既pure enumでsource読取済み、既health/metric mode/閾値・再起動rate-limitを変更しない。既Repository BatchStep一依存は前群で明示済みのまま残し、原1669内を追加physicalへ加算しない。provider故障をcatch/format/graphwalk/retry/正常化せずborrowed registryはcaller所有。

新8＋必要既Batch253を当261/34で普通実行予定。7814 ordinary→7816独立(69Java/監視64＋元依存1=65exec)・7818正常六compileを別snapshot→7820全1774/元1669→7822全121delta/105追加physical＋元依存別trace→7824生成新2＋既124=126/current ordinary/raw全理由→7826公開scan、1711結果へsource/run/実日時/OS-JDK-tool/branch/command/exit/XML/input/期待/実際/coverage/BUG/hashを結合。期待値はRD/SSの低cardinality規則/供給fixtureと本書の固定literalから独立、production methodでexpected生成0。

開始3/5/9pp上限10/fresh receipt→event1932、原-v4-v5/旧markerlast27区間/累積・専有N-T/工数null/元90再基底化0。実process/Unit/systemd/read/再起動/VM/DB/key/Backup/Root/配備操作0・actualHOLD/正式1964/53/原190新受入0/QA051final/PTALT0/whole451-native-CHR未受入を維持。
