# 606 SSC240 DONE後参照：単体テスト仕様・限定結果

## 全六host資格（2026-10-10、正式受入ではない）

Sourcee01612fcd7f2752df5ae0836b78538fd5e87f120、PG857-command `python3 -B tools/quality/vm/050_s1/pg857_completed_reference_full.py`、actual0/1081.424303s。PG858独立command `python3 -B tools/quality/vm/050_s1/pg858_completed_reference_collect.py` actual0、全3541PT/522suite/1632main、FESflakyNotRun0、静的6module0・formatter0・NullAway compile0。全source/run XML/session/JAR/sourceguardを照合、全計数は新fullrunのみ（旧305a98PTは診断/byte参照）。manifestSHAfcc7df91f91af8867e2c911fd54e7a834c6d3ef313fc028be0d8c9f417e0d6c6、私有PG379/pg857-completed-reference-six-host-v1。hostmissL3818/M631/C40/B1135、global100未達。旧2a/830との差は+7PT、三Source family既class15byte差/追加削除0。scopeGenuine/newnative/実ALREADY再試験は未了でBUG968/YKT737未閉鎖、正式24-1964-53/ITSTは更新0。

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

PG854v4/source305a0e21f9802f3020eb4ba22b000b8eccef36ed、actual0、9suite98PT/FESflakyNotRun0/static0/formatter0。prior DONE終了がhistorical observed後である実独立byte反例まで拒否を確認。新三wrapper/private methodと二reference lambdaの全適用counter miss0。これは当該method範囲の限定品質で、MaintenanceRunFiles class全体/global四100とは区別する。新full857で全テストを同source/runから計数し、旧限定結果を正式coverageへ混入0。設計のみPR78/main8d5bへ公開済、実VM候補未配備。

v2独立照合：actual0、九suite97PT、F/E/S/flaky/not-run0、SpotBugs0、formatter0。原本lookup新wrapper三methodはmiss0、lambdaに3branch残（未受入）。pending graph・current cutoff不一致を独立byteで追加し、prior pending禁止の重複条件はwholeGraphの「唯一pending＋active current」又はcompleted「pending空」が既に証明するため削除。prior DONE/終了<=observed判定と全Graph二読は維持し、prior pendingの実反例は入口で拒否をassertする。coverage除外/人工到達0。新v3で変更後sourceを別run検証、v2を新sourceへ流用0。

PG854v1はroot plugin prefixで拒否/BUG971、PTnot-run。v2はbatch-onlyの影響九suiteを所定formatter/test-compile/test/SpotBugs/JaCoCo/JARで実行、source da5eba19b（Production候補b926の三classと同bytes）、command `python3 -B tools/quality/vm/050_s1/pg854_completed_reference_selected_v2.py`。終了/XML/counter/hashの独立照合は後記まで未認定。私有保存=`/home/mini/codex/project1/work/pgpt-runs/PG379/pg854-completed-reference-selected-v2`。OS/JDK/command/source/hashはrun.safe.json、rawログ非Git。VM現Production2a/832に候補未配備、全回帰/native/global100/正式24-1964-53は未完。
