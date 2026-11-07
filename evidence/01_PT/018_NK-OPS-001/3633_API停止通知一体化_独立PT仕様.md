# API停止通知とbudget初回claimの一体化・BUG2416/YKT2161

NK-OPS-001、ApiStopBudget.begin/stopping/remainingNanos/time、ApiProcessLifetime.stop/stopping/remainingStopNanos。既RD171/UI252/SS342351・1870/PG-D637/638を維持し、内部判断PG-D1143を適用。P01805共通費一回、開始.5/2/5cap6を保持。上位仕様・60秒/親30分/Unit期限を変更しない。

元静的反例はA.stopのretainedStopping=trueとbudget.beginの間でBが停止を観測し、未開始budget例外へ到達すること。実サービス再現はHOLDのため行わない。ApiStopBudget自身のAtomicBoolean begunを唯一の停止通知stateとし、既lock内のclock前claimをそのまま公開する。ApiProcessLifetimeはそのstateへ委譲し、別flagを無くす。remainingNanosは既同lockを取得してから読むため、停止公開後に未開始stateを読まない。clock失敗時は停止true/expiry0で復活させず、元Throwableを保持する。

PT_DEFAULT対象は既whole ApiStopBudgetTestの同Fixture/await/own有限latch/poolとJDK AtomicLong/AtomicBoolean/例外だけ。ApiProcessLifetimeTest全体はTIE/実hook等の既HOLD graphを含み、部分抽出/新fixtureで実行しない。Callerの新委譲と別flag消滅は正常Mainのjavap metadataで照合する。これはcaller動的試験・実TERM/終了/親budget/資源帰還の代替合格ではない。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| APISTOP019 | 元Fixture clock=37ns、初回clockだけlatch保持。別workerはstoppingを観測しremainingを取得。first-clock保持中のFuture.getは50ms timeout、その後release/join各10秒 | 未開始stopping=false、初回claim後true。remainingは初回clock確定まで待機、解放後は経過0なので60,000,000,000ns、総clock2回。Test own JVM timeout180秒。実外部thread/jobへアクセスしない |
| APISTOP020 | 元Fixtureで初回clockを同じISEで失敗させ、故障解除後に再begin/remaining | 元ISE同一、停止true維持、remaining0、再beginで時計再読せず総1回 |
| APISTOP001..018 | 元whole全body、独立literal/identity/並行/境界を維持 | null、未開始拒否、初回60秒、一回claim、0/1/期限前/一致/超過/後退/20ns正当wrap/半周不明、clock失敗/Errorとsticky0、二begin/八read、expiry後再読0 |

元2575/2576のwhole18は成功済みで確認再演しない。今回の20件は実Main状態変更後に必要な新source回帰。新規unique2と既18の再資格を分離する。期待値は元固定表と上の独立60秒/37ns数値、Production methodでexpectedを生成しない。全Source physical一classのline/method/class/branch全100、旧exec合算/除外無し。ApiProcessLifetimeの部分counterを当sourceへ加算しない。

PG22080のpreflightではApiStopBudgetの符号折返しは既差分演算/既010で正しく、Web BUG2409と同じabsolute比較不備ではなかった。LongSupplierを持つ22Mainの時間取得/期限判定の指定spanも点検したが、その22は旧2564のPMD synchronized22rawとは別集合。関連資源やnativeを実行せず、未読callee/全sourceの正当性へ昇格しない。今回の新原因は停止状態の別公開である。

正常Main-only六module/NullAway、六静的、3sourceのPMD/Checkstyle/format、whole20/四counter/CRC/session/全source・Test・command・OS/JDK・真正exit・BUGを3634へ記録する。実caller/HOLD/CHR/native/451/正式1964-53/工数nullは別未完、BUG/YKTは必要動的callerが無ければOPENを維持する。
