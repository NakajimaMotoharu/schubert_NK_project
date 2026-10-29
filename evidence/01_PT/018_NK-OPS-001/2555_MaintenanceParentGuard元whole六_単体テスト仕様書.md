# 2555 MaintenanceParentGuard 元whole六 単体試験仕様

2026-10-29/PG-D843/event2940/source0061/HEADd16bd77f5。着手0.5/2/4pp cap10、費用leaf WBS-P018-03.02、sourceのcanonical P018-03は親参照のみ追加0。Testの485 canonical ownerはUNKNOWNを保持し、作業担当から捏造しない。原551/PT-COWNER678001～006・RD OPS009/DAT009/SYS/UI251/SS341§7.3/343§6.17/SSC119に対応するが、旧PG678成功を当sourceへ転用しない。

PT_DEFAULT。既存MaintenanceParentGuardTest全六methodを無変更で選択。Main MaintenanceOwnerFrame229行/Parent ctor/Clock・ParentProbe/ChildStartupContext.MaintenanceParent enumを確認し、static初期化はNIL/KEYSだけ。native overload parentsGuard()やnew ChildStartupContext/LinuxMonotonicClock.createには到達しない。全六のliteral clocks/probes・JUnit current thread interrupt/clearだけ、外部DB/Unit/FS/VM/鍵/Root/native/permit/intent/既Graph9操作0。保留のMaintenanceOwnerFrameTestを切り出さず、元から独立した全suiteを実施する。

| Test ID | 原method・入力 | 独立期待値 |
|---|---|---|
| COWNER678001 | twoClockObservationsBracketExactBorrowedParents/100→200・期限500/cleanup有無 | 残300、clock0→MORNING→任意CLEANUP→clock1 |
| COWNER678002 | deadlineEqualityAndPastRejectBeforeParentObservation/500・501/前read IO | 期限拒否・親0、IO同identity |
| COWNER678003 | backwardEqualityDeadlineAndExpiredPostClockNeverReturnBudget/後99・500・501/正常後100 | 拒否・残0成功にせず、100→100は残400 |
| COWNER678004 | eachParentFailureAndSecondReadFailurePropagateSameException/各親IO・後clock IO | 同IO、失敗以降の親呼出し0 |
| COWNER678005 | preAndPostInterruptAreRetainedUntilCallerClearsThem/前後割込 | IO・割込保持、caller finallyだけclear |
| COWNER678006 | nullObservationPortsNeverReadOrProbe/null clock/probe | IAE・無read/無probe |

期待値は期限差の独立算術/literal call列と元例外object。製品methodからexpected生成0。境界・異常/null/例外・割込は上表、並行parent liveness/再送/実所有は本suite対象外・既依存HOLDを維持する。

commandはchecked entry14012→fresh javac/JUnit（一selected6、単一Jacoco session/appendfalse）、14014は元XML/全source/六Jar/dependency/CRCの独立post。normal13832 compile-only原証拠/静的13838は全input同byte時だけ参照し再実行しない。Main完全Source五physical（outer/Parent/Guard/Clock/ParentProbe）のclassfile Codeを解析する。Guard default二methodにもCodeがあるため三executable・Clock/ParentProbe二no-Code interfaceであり、今回はouter/Parent二classの測定だけ、Guardは未測定/source gate1を保持する。interface名だけでcoverage対象外にはしない。guard subset100を親source100や実nativeへ拡張しない。正式1964/53・17/190/工数null/QA051finalは不変。結果/command/退出/OS-JDK/hashは2556と公開manifestへ保存する。
