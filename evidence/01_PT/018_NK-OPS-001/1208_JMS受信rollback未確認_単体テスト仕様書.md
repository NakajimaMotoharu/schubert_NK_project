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

## 是正後green着手前追補

元API red三/10-6と未実施Web red一/9-7が予定assertだけで成立、Main2bbb/全849source・実classは旧同byte、元snapshotは不変更。PG-D441に従い、原失敗を同一cause、rollback失敗を直接suppressedにも残す型付き未確認境界を追加する。旧PRE001/002、SyncRequestListenerの隔離rollback失敗、Webの読取/commit＋rollback失敗では、従来の原Throwable保持assertionを維持した上でtyped wrapperのcauseへjoinする。実装結果から期待値を作り替えるのでなく、既SSの未確認transaction再利用禁止とJDK identityから期待を定義した。

| Test ID | class/method・独立期待 |
|---|---|
| UNC005 | protocol.transport.UnconfirmedJmsRollbackExceptionTest.primaryAndRollbackMustBothBePresent：null二境界をfactory前拒否 |
| UNC006 | 同.sameNodeIsRetainedOnceWithoutSelfSuppression：同一cause保持、追加suppressed0、固定診断 |
| UNC007 | 同.distinctEqualValuedNodesAreBothRetained：equals-trueでも別nodeのprimary/causeとrollback/suppressedを同identityで保持 |
| UNC008 | 同.disabledPrimarySuppressionDoesNotHideRollbackFailure：primaryのsuppression無効でもwrapperがrollbackを保持 |
| UNC009～011 | API新fixtureのsync/question/webLogConfirmedRollbackKeeps*：通常rollback二回以上はready維持・fatal0・commit0、既再配送を壊さない |
| UNC012 | web.messaging.ReplyRollbackSignalContractTest.unconfirmedRollbackSignalsInfrastructureOnceAndNeverCommittedFatal：fatal一回/再入0/commit0、closeは外側まで0 |
| UNC013 | 同.confirmedRollbackRemainsRetryReadyWithoutFatalSignal：通常二回/readytrue/rollback2/fatal0 |
| UNC014 | 同.errorIdentitySurvivesConfirmedOrUnconfirmedRollbackAndOwnerStaysHalted：読取Error＋rollback正常/Runtime/Errorを各確認、同Error・fatal1・次読取0/commit0 |
| UNC015 | 同.priorProtocolTerminalIsNeverRenotifiedOrReclassifiedAsUnconfirmedCommit：原protocol DLQ commit一回後の未確認Runtime/Errorで再通知しない・以降処理0。元一commit以外ACK0 |
| UNC016 | 同.nullFatalSignalIsRejectedBeforeAcquisitionOrListenerStart：static開設前/owned start前のnull拒否、取得0・listener未登録 |

実command `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes-runtime> python3 -B tools/quality/pg5800_rollback_green.py`。六module/15suiteの明示54case=protocol7/storage1/bootstrap1/API21/Web22/batch2。全16追加caseと原例外・隔離・通常処理/実in-process Artemisの既独立oracleをまとめる。既EmbeddedActiveMQは自己temporary root/vm transportのみ、実guest/サービス/配備/failed-cohort/permit/原本DBBackup/鍵へ非接続。MavenのNoTestsを維持、TempDir注入を持つ通常@TestのXML名は一意なsource method名へ対応し、parameterized/skip/別名の算術加算を拒否する。

Sourceをclean commitで固定、Main1665（新一）と全850 source、target七型の実line/method/class/branchを出力する。限定54の成功やcounter不足を全体100へ広げず、必要fresh whole・当source native/CHR/451・正式は別未完。新型/例外/並行はAPI既terminal remainderの独立順序/実in-process配送試験を含む。外側WebNativeRuntime/WebLogApplicationRuntimeのfatal signal接続はsource/必要wholeで点検し、実native所有確認は保留のまま。

PG5800-v1/source1fe/47590はserialVersionUID欠落によりcompile1・PT0、BUG1491/YKT1251へ修正前起票。元runを保持してnew-v2へ移行、抑制でなく新Main/fixture三例外へ既規約1Lを付与する。全PT未実行からの必要再試験であり、成功済全回帰の再演ではない。
