# 1668 API OutboxMetric結線 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171-MON005～013/UI252/SS331351/PG-D548/group1887。OutboxMetricCollector constructor/collect/snapshot、既OutboxObservationRepository・Rows/Age recordersの同owner結線。実DB/driver/source/asOf/外側有限期限を試験済みとせず、own JDBC proxy/SDKのみ・actual VM/Root/network/keys操作0。

| Test ID / outboxConn対応method | 入力・操作・独立期待値 |
|---|---|---|
| OUTBOXCONN001 / 001BothFamiliesPublishOnlyAfterAllSuccessfulClose | 3/5/7件・2/4/6秒、PS close前hookは全6gauge未知、全close後だけ全6値/同immutable snapshot/registry close0 |
| OUTBOXCONN002 / 002FailureClearsBothFamiliesAndTrueEmptyQueryRecovers | 旧9件8秒→execute SQL失敗同一throw/両familyNaN・snapshot空、旧値immutable/一発行/PSclose、次空query全6gauge既知0 |
| OUTBOXCONN003 / 003EveryObservationFailureIsUnknownAndPropagatesUnchangedOnce | 13箇所（tx三/prepare/timeout/execute/next/status/count/wasNull/oldest/RSclose/PSclose）×SQL/Runtime/Error、全未知/元同一throw/再試行0 |
| OUTBOXCONN004 / 004StandardDoesNotReadRegisterOrRetainButChecksBoundaryNull | STD getterにthrow fixtureでも呼出0/登録保持0/null conn-asOf拒否 |
| OUTBOXCONN005 / 005ConstructorAndBoundaryNullCannotErasePreviouslyAcceptedObservation | repository/registry/mode null・未知mode/登録0、正常後の境界null拒否は旧3件4秒/snapshot不変 |
| OUTBOXCONN006 / 006OneOwnerSerializesReadCloseAndBothPublications | latchで第一prepareを停止中に第二callerを開始し第二prepare未到達・全未知、release後1→2の両成功・最終2件4秒、全RS→PS各一回 |
| OUTBOXCONN007 / 007ParallelCallersAndSeparateOwnersCannotCrossState | 同owner64callerの各counts/age1～64・結果対応/全close、別owner222件333秒/6seriesが混線なし |
| OUTBOXCONN008 / 008PartialConstructionFailureRetainsCallerRegistryAndExactProblem | Rows3登録後Age初登録でRuntime/Error同一throw、既3meterはcaller保持/4registration一発/closeはcaller一回 |

expectedはTest固定件数/秒・独立元Fixtureの固定SQL/列名/型/close oracle（1664）で生成、production.getGauge等をexpectedへ用いない。record生成32契約は当sourceの既GENMET8/OUTBOXAGE8/OUTBOXDB010で必要回帰し、数値coverageへ足さず明示保持。既Fixtureのoracle/sourceを変更せずpackage共有を再利用、返却Snapshotはimmutable。private lockはread-close-publication全体だけ、別gauge/family scrapeの同時整合は保証しない。caller registry/connection/tx/asOf真正性やscheduler/外側timeoutの所有を移譲しない。

新8＋必要既90→当98PT12suite/全24Java・実20＋metadata1予定、7462等の旧成功を算術加算0。run7476/独立7478/正常六compile7480/全Jar7482/trace7484/review7486、branch/source/command/time/environment/actual exit/input/output/XML/four100/static/BUG/hashは原manifestと後続結果へ。全分岐/null/異常/例外/並行/provider部分失敗とNPE静的解析を確認、fail/flaky/skipped/notrunはPASS0。開始3/5/9pp上限10/原-v4-v5固定、元製造新8・既90当再資格/tool費を分離、正式1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/native/CHR/actualHOLD不変更。

## 2026-11-24 排他方式の是正

BUG-3744／YKT-2929。取得済み資源の解放から同ownerの完全値公開を私有ReentrantLockに保持し、正常・早期return・元Throwable再throwの全てでfinally解放。借用Connection、read-only契約、取得資源の順、公開後の値と既OUTBOXCONN001～008の独立期待を維持する。PG43812の局所scopeで元指摘と生四指標を照合。実DBを使用しない。
