# ApplicationStopGate 固定状態callback単体仕様

Program NK-OPS-001 ApplicationStopGate create/constructor/requireStopped/checkInterrupt、RD OPS009/AVL/UI251/SS341343/元007。開始4088原1/3/5 cap8固定。source owner親P01804保持、実費主leaf P01804.02＝identity/info再読の独立fixture（7field Unit Id/PID観測制御だけ）、socket/generation/cohort/親受入を含まず親費重複0。最初の親id startはwriterが実leafでないとして拒否・event0/Unit0、元script/receipt保全し既leaf02へ内部配賦を明示してfresh開始、品質guardを迂回しない。

最新program manifest lookup/旧strict pin/seedを照合、当gate全coverage証拠無し。followup3592/007のparser単体6は既完了で再試験0・依存利用のみ。Main/callee SystemctlStateSource/UnitStateParser/ApplicationUnit/StopGateException全review、既仕様実装あり製品変更不要。全requireStoppedは注入memory StateSourceだけを使う。public createはdefault sourceのconstructor・不活性start lambdaを作るだけでreadを呼ばない、元execのSystemctlStateSource method witnessで二constructorだけ、NativeProcess/init/read/ProcessBuilder/start/実systemctl0を確認するまで合格にしない。実OS状態/VM/Root/Unit/サービス停止/配備/DB/秘密/held四無し。

|Test ID|method|
|---|---|
|PT-OPS-STOPPORT001|constructorsRequireSourceAndFactoryOnlyBuildsIndependentDormantGates|
|PT-OPS-STOPPORT002|everyCheckReadsBothFixedProjectionsInApiThenWebOrderWithoutCaching|
|PT-OPS-STOPPORT003|sourceFailuresAndInvalidBytesRejectBeforeLaterUnitWithoutNormalizingFailure|
|PT-OPS-STOPPORT004|existingAndCallbackInterruptionsRetainFlagAndStopAtEachOwnedBoundary|
|PT-OPS-STOPPORT005|failedProjectionDoesNotBecomeCachedSuccessAndLaterCheckReadsFreshBothUnits|
|PT-OPS-STOPPORT006|sharedGateUsesSixteenIndependentWorkerProjectionsWithoutSharedCache|

独立期待は元007のAPI/Web固定7行 Id=schubert-nk-(api|web).service、LoadState loaded/Active inactive/Sub dead/Job空/MainPID0/ControlPID0。Product生成expected無し。001 source null拒否・public factoryは別instanceだけ作りrequireを一度も呼ばない、002 API→Web二回・fresh配列/内容不変でcache無し、003 source Runtime/Error同一性/API失敗ならWeb0/null配列NPE/malformed又はnonstoppedの固定reasonで失敗、004 呼出前及び各callback後の割込はINTERRUPTED・flag保持/後続read0、Testfinally自分のflagだけ復帰、005 最初失敗の後もAPI→Webをfresh再読、006 shared gateに二worker16件×各二回の独立順序・cache無しを検査、全Future10秒/workerTWR。Unit stateは自己所有byteで現在hostのstateに読み替えない。

input130 prepare/static/run <frozen source>/post、JDK25.0.4/通常Main4217-20990CRC/六NullAway-SB20992同byte。CPは既normal protocol/storage/batch三jar＋固定JSpecify/JUnitのみ。Main/Test静的raw13はBatch caller割込読取1/host Test flag操作・検査9/ownworker3で各適用性記録、適用0CS0/SB0、抑制追加無し。単一JaCoCo0.8.15・全line/method/class/branch100・手動除外旧exec合算無しを要求、当単体は実停止確認/保守権限/lease取得を認定しない。元argv/exit/XML/Test ID/OS-JDK/入力実際/全hashとcaller/native未実行はstrict・独立postへ。結果3595、失敗なら915/916修正前。実Root/VM/Unit/read/新native/CHR/QA051final/全451・正式1964-53/個別17-190/新leaf/工数nullは別未完。
