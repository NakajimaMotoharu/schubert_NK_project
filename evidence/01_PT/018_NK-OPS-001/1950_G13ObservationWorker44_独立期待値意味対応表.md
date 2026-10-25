# G13 OBSOWN44・現在methodと独立期待値の意味対応

1949に基づく親review記録。Production/fixture/Test本文/元1864期待値の変更0。下表は実行結果でなく、現在sourceのassertionと既仕様行の意味対応である。全行の`obsOwnNNN`、source位置/compiled descriptor/hash、原OBSOWN ID/1864行/hashは9610/9612の公開証跡へ結合する。NPEは内部constructor/factoryの即時precondition又は異常通知であり、業務成功にcatchしていない。

| ID | 対象Main経路 | 独立期待値・確認したassertion/fixture根拠 | 観点 |
|---|---|---|---|
| OBSOWN001 | constructor | 五null portのNPE、factoryReads=0/starts=0。未取得のportをexpected生成へ利用しない | null/取得前 |
| OBSOWN002 | constructor,awaitStopped | starts/clockReads/factoryReads=0・actor=null、await null拒否。単にThread NEWを資源完了証拠にしない | null/未起動 |
| OBSOWN003 | constructor,start,requestStop,awaitStopped | 固定thread名/daemon=false、close後alive=false、独立callsでopen/rollback/close=1、pump欠測 | 正常/完了 |
| OBSOWN004 | start,awaitStopped | 二回目IllegalStateException、注入starter呼出し1、元workerだけ回収 | 重複 |
| OBSOWN005 | requestStop,start,awaitStopped | start拒否、未起動budget supplierを読むとAssertionError、starts=0 | 順序/未起動 |
| OBSOWN006 | start,awaitStopped | 固定starter RTEの同一性・再start拒否・未起動budget未読/factory0 | 例外/再実行拒否 |
| OBSOWN007 | start,awaitStopped | 固定starter Error同一性・未起動budget未読/factory0、fixture回収はowner正常化と分離 | fatal |
| OBSOWN008 | start,awaitStopped | fake starter NEW帰還をIllegalState拒否、budget/DB0。未起動が成功startではない | 境界/偽成功拒否 |
| OBSOWN009 | start,requestStop,awaitStopped | 真start後の元RTE同一性、SQL保持latch解放後にalive=false/cleanup(1,1) | partial start |
| OBSOWN010 | run,awaitStopped | 固定InterruptedExceptionをfailure queueでsame、通知時IRQ=true、uncaught=null | 未知割込 |
| OBSOWN011 | run,awaitStopped | first SQLException後fake nanoを15秒へ進め、factoryReads=2/failure空、各fixture cleanup(1,1) | 一時例外/次tick |
| OBSOWN012 | run,awaitStopped | SQLExceptionの固定cause Errorがfailure/uncaughtのsame、SQLを正常一時扱いしない | graph fatal |
| OBSOWN013 | run | asynchronous helperで元query RTEをfailure/uncaughtのsame、pump空/quiescent | Runtime |
| OBSOWN014 | run | 同helperで元query Errorをsame、欠測/quiescent。実VM障害耐性は認定しない | Error |
| OBSOWN015 | run | helperの元query RTE同一性と固定notification RTE一件のsuppressed配列 | 二次例外 |
| OBSOWN016 | run | notification Errorのuncaught優先、元primaryへの同secondary配列保持 | 二次fatal |
| OBSOWN017 | run | 固定IRQ primaryのqueue同一性/IRQ保持、notification RTEがuncaught・suppressed | 割込/二次例外 |
| OBSOWN018 | run | notification Errorがuncaught、元IRQのsuppressedに同Error。共通通知経路は010/017と併読 | 割込/二次fatal |
| OBSOWN019 | run,requestStop | beforeWaitでstop後のIRQはfailure空/uncaught=null、未知割込と区別 | stop競合 |
| OBSOWN020 | requestStop,awaitStopped | 自己worker alive=falseとpump.quiescent=trueを別々に要求 | 完了二条件 |
| OBSOWN021 | requestStop,awaitStopped | SQL保持中quiescent=false、解放後trueとcleanup(1,1)、TWRの自己thread回収 | 並行/保留 |
| OBSOWN022 | run,awaitStopped | fake connection close SQL失敗はIOException/非quiescent/欠測、Thread終端だけで成功しない | UNKNOWN |
| OBSOWN023 | awaitStopped | 初回budget0でIOException、worker alive/非quiescentのままfixtureだけ解放 | 零/UNKNOWN |
| OBSOWN024 | awaitStopped | -1/MIN→後続MAXの固定入力、budget読取1、clockを読むとAssertionError | 負/overflow防止 |
| OBSOWN025 | awaitStopped | 独立2ms-1ms=残1ms、以後50秒でも一回join timeout、clock/budget各2読・alive維持 | 上限更新拒否 |
| OBSOWN026 | awaitStopped | 固定時計1→0の逆行をIOException、元budget5秒を延長しない | 逆行 |
| OBSOWN027 | awaitStopped | remaining supplier固定RTEのassertSame、queryはfixture finally解放 | budget例外 |
| OBSOWN028 | awaitStopped | remaining supplier固定ErrorのassertSame、正常完了へ変換しない | budget fatal |
| OBSOWN029 | awaitStopped | stop nano supplier固定RTEのassertSame、所有frameの結果とfixture回収を分離 | clock例外 |
| OBSOWN030 | awaitStopped | stop nano supplier固定ErrorのassertSame | clock fatal |
| OBSOWN031 | awaitStopped | 私有waiterを既割込にし第三budget読取latch後SQL解放、結果true/IRQ復元、budgetReads>=3 | 割込/同予算 |
| OBSOWN032 | awaitStopped | 私有waiter既IRQ＋固定2ms満了、IOExceptionとIRQ復元を同時要求 | 割込/期限 |
| OBSOWN033 | start,awaitStopped | starter保持中state NEWだがstarting未完、短budgetでIOException、解放後DB0 | start競合/UNKNOWN |
| OBSOWN034 | start,awaitStopped | 独立latchでstart帰還/worker停止双方を待つFuture、DB0。5秒はfixture残予算でUnit期限でない | start競合/完了 |
| OBSOWN035 | run,awaitStopped | worker自身のawaitはIOException、私有handleでjoinしてもowner再awaitはIOException | 自己join/UNKNOWN |
| OBSOWN036 | requestStop,awaitStopped | 未起動二重stopでもsignal.releases=1、budget0が無期限waitにならない | 冪等/未起動 |
| OBSOWN037 | awaitStopped | 真Thread停止後再awaitはbudget supplier未読、alive=false。最初の正常確認を前提にする | 正常再確認 |
| OBSOWN038 | awaitStopped | timeout後の私有Thread終端を確認してもowner再awaitはIOException/budget未読 | UNKNOWN非正常化 |
| OBSOWN039 | run | resource-free factoryがnullならNPEをfailure/uncaught sameで通知、fixture取得空 | null/異常通知 |
| OBSOWN040 | run | pump nano固定RTEがfailure/uncaught same、factoryReads=0 | 取得前RTE |
| OBSOWN041 | run | pump nano固定Errorがfailure/uncaught same、factoryReads=0 | 取得前fatal |
| OBSOWN042 | run | signal RTE/Errorは元same、stopなしsignalはIllegalState/failure same、通常tickへ読替0 | 通知異常 |
| OBSOWN043 | requestStop,awaitStopped | stop signalの固定RTE/Error same、その後再awaitはIOException/残budget未読 | 永久UNKNOWN |
| OBSOWN044 | run | 使用済み一回attemptを返すfactoryはIllegalStateのfailure/uncaught same、row cleanup(1,1)のまま | 一回owner/重複拒否 |

## 共通fixtureと独立性

Fixture.startは注入starter/actual Threadの記録、Harnessは固定row3/5/7・age2/4/6/Clockを独立保持する。ApiReadOnlyObservationAttemptTest.Fixtureは型付きJDBC proxyだけでgetConnection/read-only/READ_COMMITTED/autoCommit(false)/rollback/closeを記録し、予期しない操作をAssertionError拒否する。cleanup(1,1)はProductionの返値でなく独立callsのopen/rollback/close回数を数える。OutboxObservationRepositoryTest.FixtureのSQL/timeout1秒/RS→PS順序は別literalであり、実DBはない。Signalは注入したSemaphore doubleで回数/割込/待機点を記録する。同期はlatch/futureの有限待機とfinally解放・自己Thread回収で、Thread.sleep同期はない。

仕様1864の期待値と現在のTest assertion/fixtureは上記44行で対応し、当範囲の新しい仕様違反は確認していない。これは全fault組合せ/全VM障害の証明や全assertionのmutation完全性ではない。OBSOWN018等の共通通知経路は他case/helperの固定同一性assertionと併読し、各case一つだけで全契約を担保すると記載しない。partial/timeout/自己join/close UNKNOWNをfixture finallyで回収できても、製品ownerの正常完了へ変更していない。

## 残る条件

原44実行/四counter100は別sourceの1865の歴史記録であり、新しい実行/coverageへ転用0。実API caller/Pool/Root/native/権限/本当の資源終端/同source全scope/CHR/451は未受入HOLD。初期method→TestID→独立oracle意味対応44を保存するだけで、正式/個別受入/全trace完了へ算入しない。現sourceにはfake signalの異常注入やworker運転を新実行せず、レビュー・metadata validatorだけを動かす。
