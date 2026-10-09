# 当e016保持Inspector：起動済み証跡の独立照合

Program NK-OPS-001/NK-DAT-001、対象InspectorLauncher/InspectorApplication.executeNative、ChildStartupContext.verifyInspector、InspectorCredentialLoader.readMaintenanceOwner、CleanupMaintenanceWork.inspect、独立906/907/908。RD DAT-009/OPS-009/FIL-006、UI212/241/251、SS341§7.3/343§6.7～6.11/352/354、SSC119/196/234。Production e016/current862/BOM20b99/schema028、hostはPG857/3541PT/522suite/static6zero。既起動PG872/真正PG875/ownedStop877に属する保持ファイルだけを使用、新Unit/fixture/source変更0。

| Test ID | 入力・操作 | 独立期待値・根拠 | 結果 |
|---|---|---|---|
| INSP906001 | 870起動前、875真正DONE後・停止前、895第二run後、901現在 | capture phaseを区別。初期4→first5/current5のprogress、旧4保持・first新一件のみ、固定Root1902/cutoff18:28:14.612111Z/counter0・completed有。別run/null/余剰/phase混同拒否 | v1全表同値仮定1保持、BUG995/YKT764、独立epoch試験0・v2実0 |
| INSP906002 | 保持Inspector inv244830…のPID1 journal | 同boot/UID0/PID1、startjob189749 started→done、stopjob189896 done、全時刻が真正親183192933299～184317014132µs内。GC後の空履歴からnot-run又はsuccessを推定しない | 906v2独立0/3.078983s |
| INSP906003 | 870 native-beforeと現在file | 当二TERMINAL/CLOSINGのみ初期不存在、同保持metadata/専用NSS UID/GID0600/link1/hash、同187署名source/全24現在原値・原本Backup/資源0 | 実0、snapshot4aa97f5a…保持、追加起動0 |
| INSP907001 | 各raw execをprivate限定転送、PID1から窓算出 | 各単一session/window、同Inspector processの二dump/start同一・closing後、既current18と別process、同857各mainclass byte/旧source0 | 907実0、20stream/18process、classByteMismatch0 |
| INSP908001 | host六exec＋限定当20nativeだけ | XML全counterが907と完全同値、source/JAR/hash一致、除外0 | 908実0、bootstrap4/API2/batch117未網羅family |

期待値はSSの固定Unit/owner/終了契約と手書きRoot/cutoff/counter/epoch fixture、PID1の実時刻差、独立SHA256から作成する。Production methodでexpectedを生成しない。Inspector rawUnitのlive exit statusは独立capture無し（null相当/未証明）であり、DBのnormal0・PID1 start/stop done・正規保持nativeを限定証拠とする。元875親真正1124.080833s/1800内は別の実証明、GCをその代替にしない。Inspector全例外/実native全受入/global100を宣言しない。

実command：`python3 -B tools/quality/vm/050_s1/pg906_progress_epoch_test.py`、`pg906_retained_inspector_v2.py`、`pg907_inspector_native_counter.py`、`pg908_current_gap.py`（後三件もpython3 -B、当treeから、全0）。private `/home/mini/codex/project1/work/pgpt-runs/PG379`/guest `/var/lib/pgpt-s1-preservation`、各source/command/exit/tool versionはsafe manifest、公開版はPG906-908-retained-inspector-v2 manifest。rawexec・DB行・cursor・credential/秘密はGit不格納。

907 manifestSHA250d575bcd57a6eb52401c6abe5f274b53e30b39240f009b14f1d89a540866d5、908 gapSHAaacb229138785b503d26571b47d927f92cd4f0de8141608adb9a65a362f987be。前903比18L3M2B追加、未網羅839L162M12C756B。計画上の「Inspector未起動」はGC空からの誤推定なので撤回、新fixture依存をまず作る順序を保持済み証拠照合へ是正した。正式24/1964/53・WBS受入/工数率未更新、同source残host条件/実Log/CHR/四100/正式引継ぎへ継続する。
