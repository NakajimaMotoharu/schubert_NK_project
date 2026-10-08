# PG678 親guard期限・観測順序

NK-OPS-001/MaintenanceOwnerFrame.parentsGuard、RD OPS009/DAT009/SYS・UI251・SS3417.3/3436.17・SSC119/PG-D403。PT-COWNER678001..006は新MaintenanceParentGuardTestの順：正常二read/各親順、前期限一致/超過/IO、後退/後期限/同値正常、各親/後read IO、前後interrupt保持、null無観測。fixture nonzero literalUUID/同owner/二Parent/PID-ticks/期限500、期待残500-200=300・同時刻100残400を独立算術でassert。clock0→MORNING→任意CLEANUP→clock1をliteral列で確認。前期限は親0、各失敗以降call0、IOException同instance、割込はcallerfinallyでだけclear。

既MaintenanceOwnerFrameTest4の固定byte/parse/constructor/queryTimeout、ChildStartupContextTestのnative観測正常拒否/同親候補等と選択する。並行/再送は同owner guard再認証を既consumer suiteで担当しduplicate加点0。native defaultは実clock::nowNanos/context::verifyMaintenanceParent固定、syntheticportは実Unit権限を一切付与しない。

source/command/XML/exec/JAR/static/hashと各4counterは新PG678 selected/独立qualificationへ記録。未実行・別source・oldnativeを成功へ算入0。開始WBS-P018-03.02 .67/1.67/3.67pp/event0162、全残未較正90.9/269.8/642.6保持、共通K01/実N費と重複なし。内部contract後変更群全6/新実VMsource/native/正式必要。
