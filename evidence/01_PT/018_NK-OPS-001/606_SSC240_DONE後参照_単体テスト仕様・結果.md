# 606 SSC240 DONE後参照：単体テスト仕様・限定結果

対象=NK-OPS-001 / MaintenanceRunFiles.Session.successReferenceRun/completedSuccessReferenceRun、MorningNewRunAdmission.OriginalProof.referenceRun、MorningResumeAdmissionの同Session adapter。関連NK-OPS-001/009、UI251、SS341/343/354、SSC200/203/240、QA047、BUG968/YKT737。Production配置はsrc配下のみ、characterization基準不変更。

|Test ID|目的・入力/操作・fixture|独立期待値/根拠|
|---|---|---|
|RLOOK852001|固定RUN/activation、historical cutoff、同Session start→pendinglookup→complete→completedlookup|手書きNKRUN1/NKACT1/NKDONE1 byte、active無し、旧pendingはIO、新typedは固定RUN、write/unlink/sync増分0|
|RLOOK852002|DONEのoutcome/time/activation違い、未完了、unknown、null、observed下限/microsecond/上限|完全tuple違いと不正時刻はIO、nullは境界拒否、原値書換0|
|RLOOK852003|既DONEと同scope発行のWARNING10、historical SKIPが当DONE前、prior固定終了済|pendingへ戻らずtypedcompleted reference、原publication回数既0/新1、固定prior cutoff値、WARNING維持|
|RLOOK852004|completed参照IO/Runtime/Error、owner失効・異thread、adapter欠落|同例外identity/固定IO、値非返却、publish0・foreign callback0|
|RLOOK852005|全Graph二読のunrelated/prior/namespace/listing/close/interrupt変化、正常|全6listing、2scan正常は固定RUN、競合は拒否、原本書込系0|

fixtureはProduction期待値生成を使わず、固定UUID/UTC/JST境界と手書き原本bytes、独立event順序/回数を利用する。正常・境界・null・異常・例外・並行/owner・再送/既DONEを含む。DB prior成功条件はCleanupTerminalRepository既独立suiteで保持し、所定全回帰と実DONE_AFTERは後続。

## 修正前再現

PG853v3、凍結Production2a0d5aa392c85a1dc12a1cdb423978e8500895b8の六JAR/当Git Fixture、Java25.0.4、Ubuntu host。command `python3 -B tools/quality/vm/050_s1/pg853_before_fix_reference_v3.py`、actual0、同Session pending参照/complete/active無し/旧pending参照IOを確認。これは修正前再現成功でProduction合格加点0。私有log SHAaee62d1e54ec9dd4d38f55722e4c31ac31217c1359949466a463161233aff293、oldFixture SHA c72948a1c7443354ca4129dd4d8f12320ed8de7ff4d51fbabf03d67fbf781cec。v1 XML階層拒否/BUG969とv2 callbacknull拒否/BUG970は保存・非合格。

## 候補選択（正式受入ではない）

PG854v1はroot plugin prefixで拒否/BUG971、PTnot-run。v2はbatch-onlyの影響九suiteを所定formatter/test-compile/test/SpotBugs/JaCoCo/JARで実行、source da5eba19b（Production候補b926の三classと同bytes）、command `python3 -B tools/quality/vm/050_s1/pg854_completed_reference_selected_v2.py`。終了/XML/counter/hashの独立照合は後記まで未認定。私有保存=`/home/mini/codex/project1/work/pgpt-runs/PG379/pg854-completed-reference-selected-v2`。OS/JDK/command/source/hashはrun.safe.json、rawログ非Git。VM現Production2a/832に候補未配備、全回帰/native/global100/正式24-1964-53は未完。
