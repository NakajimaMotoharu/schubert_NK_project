# 2841 API標準SDK三whole44 単体テスト仕様

NK-OPS-001/WBS-P018-09/RD171/UI252/SS351/1779/1785/1789、Production6b53/normal14216固定、dev-foundation。event3237で着手前1/4/8pp cap8固定。API GC16/JVM14/System14全44 Test IDは以下。current1467に各suite未選択を照合し再演0。

三Main全bodyを直接読了。原Test全1381行は既全読Web counterpartと全文を明示正規化比較し、全差分なしを確認した：package web→api、Web/WEB→Api/API、webgc/jvm/sys→apigc/jvm/sys、参照1787/1781/1791→1785/1779/1789、unknownエラーinvalid monitoring mode→CONFIG_INVALID。自己SDK/latch/finitejobs/fixture/cleanup本文も全同一。API実hashはmanifestに固定し、Webの成功をAPI成功へ流用しない。

独立oracleはRuntimeMXBean uptime/start時刻bracket、OSMXBean CPU時刻bracket/FD上限とRuntime CPU数、固定APIタグ、4/2 binder snapshot/順序/長境界・null/Runtime/Error identity。GC FACTORY→OWNER→BIND・拒否/失敗後caller保持と明示close/各独立scope、有限64job/4workerでGC64/JVM256/System128 callback。unknownはCONFIG_INVALID、STANDARDはfactory/owner/sourceを読まずlazy。GC listenerは新規ownchildの保持handleだけclose、forcedGC/heapdump/attach/targetprocess/VM/Root/実DB/鍵/ネットワーク/配備0。既拒否の再演や境界探索ではない。

command: `env PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15096_api_standard_forty_four_pt.py`。freshjavac -proc:none -Xlint:all -Werror/Java25.0.4/六normalJar、親180秒・各Future10秒/解放finally。post15098は同一exec/CRC/全三Source Jar closure・四counter、独立15100はSS351/元宣言44/XML/Code/ownerを別読照合。元OS/JDK/時刻/command/exit/source/hash/input/XML/exec/coverageを2842と公開manifestへ。実測前は未確認、除外0/公式filter維持/自然0はN/A。Failed/flaky/skipped/not-run加点0。BUGは修正前915/916。

全体451/正式1964-53/17-190/工数null/QA051final/全安全HOLD維持。SDK自己観測を外部readiness/nativeへ変換しない。

## 原Test ID

### ApiGcMetricRegistrationTest

- `apigc001DefaultSdkIsOwnedAndClosedBeforeBorrowedRegistry`
- `apigc002StandardIsLazyForSourceFactoryAndOwner`
- `apigc003FactoryOwnerBindOrderAndSameHandle`
- `apigc004NullBoundariesFailBeforeActivation`
- `apigc005UnknownModesNeverInspectSourceOrCallbacks`
- `apigc006ClosedDebugFailsBeforeFactoryAndOwner`
- `apigc007NullFactoryResultIsNeverAcknowledged`
- `apigc008FactoryRuntimeAndErrorIdentityRetained`
- `apigc009OwnerRejectMeansNoBindOrImplicitClose`
- `apigc010OwnerRuntimeAndErrorNeverActivateOrAutoClose`
- `apigc011BindFailureLeavesExactHandleInAcknowledgedOwner`
- `apigc012SameInstallerDoesNotMixTwoOwnerScopes`
- `apigc013FiniteIndependentConcurrentOwnerScopes`
- `apigc014RetainThenRejectOrThrowKeepsCallerCleanupWithoutActivation`
- `apigc015ConfirmedFixtureCloseIsNotRepeatedByCleanupGuard`
- `apigc016FailedFixtureCloseRemainsUnconfirmedUntilExplicitRetry`

### ApiJvmMetricsTest

- `apijvm001ActualFourStandardBindersWithIndependentRuntimeClock`
- `apijvm002StandardIsLazyAndDoesNotReadRegistry`
- `apijvm003ExactlyFourOrderedPortsSeeSameBorrowedOwner`
- `apijvm004NullBoundariesRejectWithoutBinding`
- `apijvm005UnknownModesNeverReadSourceOrFactory`
- `apijvm006ClosedDebugFailsBeforeFactoryAndDoesNotReopen`
- `apijvm007NullFactoryListOrElementFailsBeforeAnyBinding`
- `apijvm008WrongBinderCountIsNotPartialSuccess`
- `apijvm009FactoryRuntimeAndErrorKeepIdentity`
- `apijvm010EachBinderRuntimeStopsLaterPortsAndKeepsPartialOwner`
- `apijvm011EachBinderErrorIsNeverNormalized`
- `apijvm012StandardOnClosedOwnerDoesNotInspectOrCloseAgain`
- `apijvm013SameInstanceUsesDistinctRegistryOwners`
- `apijvm014FiniteConcurrentPortsDoNotShareSourceState`

### ApiSystemMetricsTest

- `apisys001ActualStandardCpuFdAndIndependentCpuTimeBracket`
- `apisys002StandardIsLazyAndDoesNotReadRegistry`
- `apisys003ExactlyTwoOrderedPortsSeeSameBorrowedOwner`
- `apisys004NullBoundariesRejectWithoutBinding`
- `apisys005UnknownModesNeverReadSourceOrFactory`
- `apisys006ClosedDebugFailsBeforeFactoryAndDoesNotReopen`
- `apisys007NullFactoryListOrElementFailsBeforeAnyBinding`
- `apisys008WrongBinderCountIsNotPartialSuccess`
- `apisys009FactoryRuntimeAndErrorKeepIdentity`
- `apisys010EachBinderRuntimeStopsLaterPortsAndKeepsPartialOwner`
- `apisys011EachBinderErrorIsNeverNormalized`
- `apisys012StandardOnClosedOwnerDoesNotInspectOrCloseAgain`
- `apisys013SameInstanceUsesDistinctRegistryOwners`
- `apisys014FiniteConcurrentPortsDoNotShareSourceState`
