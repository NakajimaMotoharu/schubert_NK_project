# 1208 JMS受信rollback未確認：単体テスト仕様書

Program NK-MSG-001/NK-WEB-002、SS312/321§6–9/352、UI212/231、RD MQ004–010、BUG1489/YKT1249/PG-D441/PTPRE013。Main基点2bbb85a29/元3939の結果は保持し、新sourceへ加算しない。

| Test ID | class/method | 入力・操作と独立期待 |
|---|---|---|
| PT-JMS-UNC001 | api.messaging.inbound.ConsumerRollbackUnconfirmedContractTest.syncRollbackUnconfirmedStopsAllFourContexts | 四context登録後、最初のBytesMessage読取Runtime→rollbackもRuntime。ready=false・fatal一回・protocol通知0・commit0、同/別contextの次callbackは読取に入らない |
| PT-JMS-UNC002 | 同.questionRollbackUnconfirmedStopsFurtherWork | 単FIFO context、同じ失敗と次callbackでready=false/処理再入0/commit0/通知一回 |
| PT-JMS-UNC003 | 同.webLogRollbackUnconfirmedStopsFurtherLogs | Log専用context、同条件でready=false/処理再入0/commit0/通知一回 |
| PT-JMS-UNC004 | web.messaging.ReplyRollbackUnconfirmedContractTest.rollbackUnconfirmedMakesReplyOwnerUnreadyAndStopsFurtherDecode | reply専用context、同条件でready=false/再decode0/commit0、CommittedFatal通知0。fatal signal接続は是正後の追加PTで確認 |

fixtureは許可済method以外をAssertionErrorで拒否し、固定合成例外/Clockを使用する。期待値はproduction helperを呼ばず、SSのrollback確認/所有・Messaging3.1§8.7から明示した状態値・呼出回数で作成する。provider内部がrollback済みかは未知であり、proxyは状態変更前throwの反例だけ。成功時再配送、same/distinct Throwable・suppression無効、null、Error、隔離失敗・外側signalは後続仕様追補で先に定義する。

実行予定：clean test-only sourceを新snapshotへ固定し`tools/quality/pg5794_rollback_unconfirmed_selected.py red-api`、未実施Webは`red-web`。format→六module有限selector/package/JaCoCo/既null・SpotBugs、元NoTests guardは維持。赤は正確な予定assert failureだけで目的成立、skip/not-runをPASSにしない。元Main全1664が2bbbと同byteであることを別照合する。是正後greenと必要同source wholeは別run、四counter100/全体/実provider/nativeは実測まで未受入。

実環境JDK25.0.4/Maven3.9.12、専用local work snapshot、元source/branch/開始終了/command/exit/XML/counter/hashはprivate manifest、allowlist結果だけ公開する。rawlog/credential/token/session/DB dumpは保存対象外。実行結果・commit・証跡hashは後記。
