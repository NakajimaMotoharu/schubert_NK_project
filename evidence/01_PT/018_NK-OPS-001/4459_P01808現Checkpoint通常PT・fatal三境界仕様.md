# P018-08 現Checkpoint通常PT・fatal三境界

WBS66 A2-28.01（開始見積1.5/3.9/7.7pp、cap8、原費用一回）。所有P018-08、受渡し子.01/.02/.03。既PG15276/78/81のProfile/Terminal14は五physicalと原Test本文が現Rootへ一致する範囲だけ参照し、確認再演しない。CheckpointはBUG2803/75d0caで三catalogが変わり、旧PG17620/22/24の12件を新sourceのPASSにしない。

現Root477 compileのBootstrap200/Storage80 classdirs（四保留型を含まない二module全体）と、固定JUnit/annotation JARのみで原whole Checkpoint12＋新whole fatal3を一Unit source/runへ固定。標準javac release25/lint/Werror、原Main Root NullAway/Werror/全SBを参照し、Testのformat/Checkstyle/全PMDを実施してから独立JUnit実行。closed_host_profileの一般reflection禁止を変更しない。この対象は元PG17620で実行済みの公開provider/metadata・memory exportの通常PTであり、拒否操作の別経路再試行ではない。新製品sourceは変更0。

実作用は自己所有JUnit JVM/有限executorとpublic fixtureのreflection・自class resource byte読取のみ。原12は既認定のpublic getAgent/getVersion/getSessionId/getExecutionDataと固定CodeSourceのmetadata検査。実reserved agentのhash/read/export/起動・Root/鍵/VM/DB/ソケット/業務intent/失敗cohort処理を行わない。実nativeとRoot/HOLDを維持する。自己所有測定agentはtoolchain配下でreserved /opt profileと異なる。NativeCoveragePrivateFileとFixedServiceIdentity$NativeQueryが初期化されていないことを実class-init logから独立確認する。元whole7 StopHoldは実owned TERMを含む既HOLD、NativePrivateFile7は実native inode/FDを含む既HOLDとして今回は実行しない。

|Test ID|入力・操作|独立期待値|
|---|---|---|
|NCHECK-FATAL-001|PublicAgent constructorのsource検証IO又は公開invoke wrapperへ、固定Errorをcause/suppressed/SQL-next経由で与える|元Errorと同一objectをthrow。通常IOExceptionへの変換0、constructor以後getter呼出0|
|NCHECK-FATAL-002|version/sessionの公開invokeへ同じ独立graphと非fatal循環を与える|Error graphは同一Error。非fatalは固定IOException message、cause null/suppressed0。成功getterの固定version/sessionは元12で確認|
|NCHECK-FATAL-003|executionDataWithoutResetのinvokeへ同じgraph|同一Error又は非fatal固定IO。reset引数はfalse、再呼出による成功扱いなし|

Errorは固定AssertionErrorであり実heapOOMEを起こさない。期待値は製造preserveFatalで計算せず、fixtureが保持する元object/固定literal/counterをassertする。三JUnit定義内のgraph matrixを件数へ水増ししない。旧12の全Testfile・独立GOLDENとassertを不変に保持する。

結果は当sourceの15実行/F/E/S/not-runと別に、全Main物理counterを未filterで測定する。実native配線など未hitがあれば四100未達のまま残す。旧14/旧12/他execを合成しない。明示したsource/run・TestID・command・開始終了・exit・hash・静的レビュー・全coverage・BUG2803/YKT2359をmanifestへ残す。F02/F03終了依存と全9子criteria未成立の間は元P018-08を正式受入にしない。
