# 有限既定policy単体試験仕様・477着手判定

NK-OPS-001/ServiceProcessResources、SYS002004/SS333342343354/SSC318、WBS-F03（費用主担当）/P018-04.03参照、既実装PG-D472/sourcee45の診断・有限観測factory。実装は既にあり、新PG変更が必要か試験/レビューで判定する。Root実操作/拒否PTの代替ではない。

候補比較：ApiApplicationPreparation.prep004は既に公開wrapperのnull/欠落を検証しているため重複追加0。WebManagementServer.openの未実測70行はstart失敗後close呼出が例外終了する地点で、SS317のunstarted UNKNOWNを正常closeへ変更してhitを作らない。未網羅は保持し、除外/到達不能による100扱いはしない。

|TestID/新method|独立期待|
|---|---|
|PT-NHOLD318004/hold318004PreparedDiagnosticUsesLiteralAndChecksNullBeforeSink|既定ConsumerへIOException/Errorのsynthetic非公開文字列を渡しても、UTF-8固定 `service resource release unconfirmed`＋行末だけ各一回。nullは取得前契約のNPE/固定message、出力増分0|
|PT-NHOLD318005/hold318005PreparedDiagnosticContainsRuntimeAndFatalSinkFailures|public stderr portがRTE/Errorを返しても有限policyは帰還。実渡しmessage/一回callをcallback外でassertし、callback内assertが保護catchに飲まれる偽合格を防ぐ|
|PT-NHOLD318006/hold318006PreparedObservationIsFiniteAndConsumesNotificationOnly|既定Runnableは通常tick一回で有限帰還し、自己workerの先行割込通知も消費して帰還。これは保持loopの完了やresource releaseではない。elapsedをproduction methodからexpected生成しない|

fixtureはown Surefire JVMのByteArrayOutputStream/二fault PrintStream/自己workerだけ。SYSTEM_ERR ResourceLock＋必ずfinally復元、実credential/DB/JMS/files/VM/services/Root/A/permit/intent/cohortは0。非復帰retainUnknownRelease/unknownReleasePolicyを実行しない。観測factoryはSS318の既定有限tickであり、5秒のown worker上限を持つ。Test側sleepを同期に使わず、業務時刻・Root deadline・権限を変更しない。PT_DEFAULT、unknown-refusal範囲へ依存0/安全条件既知。残49%・原全job終了から開始。

ServiceResourceRetentionTestの既5@Testは期待不変更で新3を追加、選択6512はbaseline12/7＋当8/1=20/8。format→全六test-compile（動的PT0）→選択PT/型null/SpotBugs/JaCoCo。真正0後6514は原archive/JUnit/全8511667/六Jar/PMD raw1361/CS0を回収・同Main全byte不変更を確認。新Test-only sourceの結果を旧4064へ算術合算せず、必要まとめ全体までglobal/正式へ加点0。少なくともline/method/class/branchをraw保持し未達を100としない。

実行予定commandは固定PYTHONPATH/JDK25.0.4/Maven3.9.12で `python3 -B tools/quality/pg6512_finite_policy_factories.py`、原0後 `python3 -B tools/quality/pg6514_finite_policy_qualification.py`。新only slotを使い元success/失敗/原本を上書きしない。群開始.1/.3/.9ppを固定、v4/原見積/実N/Tnull/専有費null/工数nullを維持。結果/対象commit/実行日時/hashは後記。
