# Clock・Poller・FakeStore 原26：一括待ちと所有終了の有限化

G03.05主/P01809関連追加0、REWORK原1/4/8共有pp cap10。後続2811/2815と2387の局所無期限記録を照合し、MonitoringPollerTest原8、MonitoringObservationClockTest原8、FilesystemHealthObservationTest原10の三whole26を凍結する。ClockがFixtureStore、PollerがFixtureClockを直接使うため全三原Test/helperを保持。Test method抽出/新fixture/別経路/旧57再演はしない。四owner（Poller007/Clock007/FS007・010）のinvokeAll(jobs)とTWR.closeが無期限であり、BUG2570を修正前起票。一括待ち10秒、単一finally.shutdownNow/awaitTermination10秒へ四組を変更し、timedInvokeAll後のterminal Future.get/原集合1..64/回数/全26期待は維持する。

対象完全Source/CodeはMonitoringPoller、MonitoringObservationClock、FilesystemHealthObservation、FilesystemHealthMonitorの四Source四class。関連RD171/NK-OPS-001/UI252/SS351§7、411§10、P01809。Context/HealthUsageRatio/AlertLifecycle/Thresholds/ContinuousWindow/TimedFilesystemMonitorとEvaluationは必要helperのみで親Source全受入を主張しない。全Main/Test/fixture/initializerを読了。全FileStore virtual methodをFixtureStoreがoverrideし、total/usable以外はthrowする。Clockも固定Instant/AtomicLongと明示Durationだけ。実FileStore・path・OS採取・Clock.system・管理API・DB/JMS/VM/Root/FFM/鍵/Graph操作0。IOException/Runtime/Errorは固定object identityと無formatをassertし、実障害誘発しない。

独立期待値はcallback17/23/7と回数1/2/64、signed long wrap5ns/Long.MAX=9223372036秒854775807ns、逆行・欠落・例外時非commit/次一回gap、固定0/80/90/100%、byte1/Long.MAX/ratio不正、80/90/95の1byte手前IEEE literal、300/60秒と600秒回復gap/null・不正/並行64。Production methodでexpectedを生成しない。

現normal22084/静的22086 Main同byte・最小batchJar/Console1.13.4/JSpecify1.0.1/JDK25.0.4/JaCoCo0.8.15を固定、Testだけproc:none/implicit:none/Werror。lint真正0後だけbody、format/static全指摘個別適用性/全sourcebody逆変換→Source固定通常push→元whole26一JVM一session一回180秒/owncwdtmp→全四CodeとXML/actualExit/実CRC/held四init0/独立固定vectorを別postで照合する。FilesystemHealthMonitorは純delegateで自然branch0となる場合はN-A/coverage null、他Source四100と区別し非空全Sourcegateを偽0にしない。個別XML/Source/method/環境/command/hash/BUGは3930と公開manifestへ。

未実行/不足/UNKNOWN/自然0を100へ補完せず、旧成功やexecを合算しない。新unique/leaf/正式更新0、unique520Java416/候補114pending12whole93暫定/正式1964PT53scope/工数null/QA051final・全HOLD不変。全2177/2565動的HOLDはOPEN、群末fresh/quotaと専有費/N/T nullを別結合し通常区切りで停止しない。
