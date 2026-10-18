# NK-OPS-001 / SSC307 Root待機の独立仕様

主担当WBS-P018-03.02、RD/UI既NK-OPS-001/SYS002004/OPS009/UI212251・SS343/354/SSC137143307。RootStartupPending.awaitLaunch(self,deadline,WaitIo)、readLaunch(LaunchRead)、既native入口/verifySelf。SS307設計only429594a15→main反映を先行。event1174着手見積低.4/標準1.5/高4共有週次pp固定、専有費/実N/T/消化率null。

fixture：boot31100027-3333-4333-8444-555555555555、invocation22222222222222222222222222222222、pid300/ticks200、API又はWEB、epoch31100027-4444-4333-8444-555555555555、permit=a×64/owner=b×64。public識別literalで、実OS権限なし。deadline100、期待順序は製造methodで生成せず以下literal列へ固定。fake clock/pauseは時間待ち不要、独立入力portの成功をnative起動成功へ算入しない。

|Test ID / RootPendingWaitTest method|観点・入力|独立期待値|
|---|---|---|
|PT-ROOTWAIT-SSC307-001 / pending001ImmediateBothServicesHaveExactObservationOrder|API/WEB即launch、clock10/11|clock10,owner1,read1,owner2,clock11の順、pause0。全自己identity一致|
|002 / pending002MissingTwiceUsesSameDeadlineAndExactOrder|empty二回→launch、clock1/2/3/4|各loop clock/owner/read、emptyの後だけpause各一回、成功後owner4/clock4。deadline延長なし|
|003 / pending003EqualOrPastDeadlineRejectsBeforeOwner|clock100又は101、deadline100|固定storage UNAVAILABLE拒否、clock一回のみ・owner/read/pause0|
|004 / pending004MissingCannotRestartOrExtendDeadline|clock99でempty→pause→100|二回目clockで拒否、owner/read各1/pause1。新期限の起算禁止|
|005 / pending005FinalDeadlineIsStrictAndAfterOwner|clock99でlaunch→owner2→clock100/101|最終clockで拒否。owner再検証を省略しない。成功99/99は001の補助境界|
|006 / pending006EitherOwnerFailureStopsWithoutLaterObservation|owner1/owner2から同一IO|同一object、当時点以後read/clock/pauseを呼ばない|
|007 / pending007UnknownClockOwnerReadAndPauseFailuresKeepIdentity|clock/owner/readでIO/Runtime/Error、pauseでRuntime/Error|同一object、成功化/固定例外への変換なし|
|008 / pending008WrongChildGenerationStopsBeforeSecondOwner|launch pid301、self300|storage拒否、owner/read1のみ、最終clock/pause0。既verifySelfの全欄負例も再実行|
|009 / pending009InterruptedPauseRestoresFlagAndRedactsCause|empty→pauseでInterruptedException|IOException literal root launch unavailable、cause無し、interrupt=true、後続I/Oなし。test finallyで当threadの元状態を復元|
|010 / pending010NullBoundariesDoNotObserveNativeInputs|self/WaitIo null、read Optional null|NPE fail-fast。境界nullはclock0、返却nullはread以後owner/clock/pauseなし|
|011 / pending011OnlyMissingLaunchBecomesEmpty|LaunchReadがMISSING/COLLISION/UNAVAILABLE、又は正常record|MISSINGだけempty、他Reasonは同一object、正常record同一identity。start-intent前提とScope内catch位置は元sourceと照合|
|012 / pending012ReadIdentityAndNullContractsStayFailures|LaunchReadがIO/Runtime/Error、port null、record null|同一object又はNPE、unknownをemptyにしない|

PG/PTを同時に進め、Testを先に作成→内部port/既順序を実装→fixedsourceを一つにcommit→全六Production format先行→選択Root待機/既verifySelf・StartupLaunchFiles/Root ELF/実依存suite→compiler NullAway/SpotBugs/JaCoCo→元a2ecc/4970の三compile module physicalMainへ累積予定byte差を照合。元3791/署名/ABI/nativeを確認目的で反復せず、coherent変更群の必要freshwhole/当source nativeを別工程で実施する。

本仕様時点で製造/選択実行未完。実行command・日時・source・XML/TestID・期待/実結果・counter・static・hash・BUG/SSCを結果と秘匿manifestへ保存し、raw credential/session/DB/keysはGit禁止。TDD未実装の初回失敗は障害でないが、実装済期待違反は修正前915/必要916へ登録する。
