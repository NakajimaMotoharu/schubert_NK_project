# 1289 Web受付・worker・trace：10箇所のPG個別適用性

source acb/SS313314324342351352354・UI212226242243253・AUT002004/MON003/MQ008/SYS004・PG-D369/364/226/354/411、WBS-F03。通常1939待機中の変更無しPGレビューで、PTALT未特定の拒否動的試験を代替したとの認定ではない。開始見積0.25/1/3pp、専有費/N/T不明null。対象10は旧rawで未review確認、current raw/source/Jar/原XMLへ接続するまで未完、旧成功の移植0。

| class/行/rule | 個別契約・独立oracle |
|---|---|
| WebHttpAdmission34 synchronized | admitのstopping/既admit/ownerStopping検査とaccepting書込を同private final lockで不可分。STOP005/001002の二重admit・先行停止拒否。 |
| 同42 | acceptingの二条件読取は同lock、ownerStoppingは別owner通知supplierでsnapshotを保証せず即時拒否を優先。STOP005。 |
| 同48 | acquireの受付検査とactive++は同lock、refuse/drainと競合しても拒否後にleaseを新規作成しない。STOP001002/003。 |
| 同56 | active下限確認/減算/notifyAllを同monitorで行い、未取得completionを拒否・待機drainを起こす。STOP001002/003。 |
| 同65 | refuseは停止と受付offを同lock、既leaseを破棄せずcompletedまで維持。STOP001002/003。 |
| 同76 | drainの停止/active loop/waitは同monitor、waitはlockを放してcompletedへ進める。0/負/30秒超/割込復元・実async terminalまで保持、STOP001002/003。private final lockでありthis/classの公開monitorではない。 |
| WebLogReplayWorker26 volatile | workerから監視threadへのimmutable Report参照を公開、他counterはAtomicLong。snapshotは各aggregate値で原子的な複数値snapshot保証ではない。W01/temporarySqlAndRuntimeFailuresRecoverWithoutLeakingDetails。 |
| 同70 generic Runtime | SQLException/Runtimeをfatal graph検査後に失敗cycleとして記録、provider/cause非出力・永続rowのlease/backoffが再送oracle。hiddenFatalはterminalへ・failed/completed加点0。rerun008HiddenFatalStopsWithoutFailedCycleAndSelfJoinRejects/temporarySql...。 |
| RevocationRetryWorker62 generic Runtime | fixed transient failureだけfailed++、preserveFatalが内包Errorを再throwしてuncaught handlerのterminalへ。due/backoffはDB rowが正でscheduler cadenceを業務再送間隔にしない。rerun008bTransientFailureRecoveryAndFatalTerminalNeverExposeProvider。 |
| WebRequestTrace63 volatile | request/async観測間でimmutable Optional<TopBarViewModel>参照を公開。認証principal/token/sessionを保持せず表示snapshotだけ、route/message/completionは別Atomic。REQ007安全射影/empty/null/REQ008隔離・順序。volatile可視性の正当性はJMM静的根拠であり実native競合を計測したとの主張ではない。 |

反証点検=全lockがprivate final・全対象state同lock、wait/notifyの同monitorとfinally release、actor/reportの全writer/reader・immutable投影、worker fatal graph/不成功counter/actual joinとstop通知の相違をactual source/JVMで確認する。汎用catchを一括必要分類しない。全原1939XML・独立Test全文hash/全宣言ケース・実outer/nested四counterをsource/hashでjoinし、欠落branchを0へ補完しない。current全体3988へは真正結果後に改めて接続、10レビューを新10PTやcoverageへ加点0。raw PMD警告/ルールは保持し、抑制/除外0。未確認実Root/VM/DB/native/CHR/451/traceと正式終了依存は未完のまま。
