# 616 当source実body全六回帰：仕様・結果

Program: NK-DAT-001/NK-OPS-001、WBS-P004-04/P018-03.02、共通全回帰K01.01。関連SS341/342/343/352/451、UI251、OPS009/TST004、PG-D407～409。対象class/methodとTest ID、独立入力/期待値の根拠は612～615および各既存program仕様から継承する。期待値をProduction methodから生成しない。

変更mainのfresh全体回帰triggerとしてsource `40ef6e894573d2ffab1d1732124960f9c98d5f97` の全六moduleを一回実行。commandは `python3 -B tools/quality/vm/050_s1/pg926_body_full.py`、独立資格確認 `python3 -B tools/quality/vm/050_s1/pg927_body_full_collect.py`。全src/tools/pomのGit blob、実行中のclean/source不変、全XML・single-session topology/window、JAR byte、SpotBugs/Error0を照合済み。依存正常/境界/null/異常/例外/並行/再送観点は既存全523suiteを省略せず実行。

実終了0、3560PT/523suite/1632main、F/E/S/flaky/not-run0、静的六module0、NullAway qualified compile/format0、1099.819409秒。ChildStartupContext278L23M1C242B、Snapshot206L31M1C320B、Files131L26M1C38B、Publisher134L25M1C46Bは四counter100。実body/owner/daemonの限定結果は615参照。全体host残3799L630M40C1106Bで100%未達、旧915との残測定差は15L7B（source/構造差を含むので全て新試験成果とはしない）。InspectorApplication実native入口、NativeReader残4L等は未完。新candidate未配備、旧e016のnative成功は当結果へ合算しない。正式1964PT/53scope、wholeWBS未受入を維持する。

証跡は `evidence/provisional/PG926-927-body-full-host-v1/manifest.json`。実開始/終了日時、OS/toolversion、branch/source/command/終了code、各module XML/hash・coverage/exec/static/JAR/hash、私有原run/log/hash、独立期待値・結果・未達を収録。credential/password/session/token/native rawは出力しない。関連新BUGなし。PG925v1/v2、旧915/旧nativeは別source系列として保全する。
