# PG309 固定backup worker実接続 PT仕様（実装前）

NK-OPS-001、BAK/BKO/OPS009/UI251/SS3416.1/3436.6/SSC092/BUG271/YKT205。本単位はrequest配布・専用worker・fresh Unit結果回収を一体で実接続する。request codecだけの完成で単位を受入済みにしない。

PT-OPS-BREQ001～008：BackupWorkerRequest encode/consume/directoryName。PT-OPS-BREQFILE001～008：root-only BackupWorkerRequestFiles prepare/read/retire/全所有IO。canonical公開literal version/run UUID/内容生成開始時刻byteと既存規則の独立dirname vector、null/非zeroUUID/年0001～9999/micro/未知・欠落・重複・ASCII/size/改竄/不一致・全byte消去・並行・新only衝突・root metadata/ACL/readonly/tmpfs/同device/全IO/force/close/sync/名前原本再照合。source request600/root700とsystemd runtime0440は別、既存reader policyを緩めない。

PT-OPS-BWORK001～008：BackupDatabaseWorker.run/必要固定admission/入口と終了、真の固定NSS backup専用UID/GID/groups、自己kernel/Unit/Invocation/MainPID・DB専用材料・backup/runtime root、公開requestと原本dirname。new-only child700/新dump600/既存part衝突保全、byte消去→dump/list→copy消去→全close成功のみ0。全失敗位置・null・unknown・割込・並行・起動途中不明隔離・終了後条件。literal public bytes/UID/group/request/query/SQL後条件を独立oracle、未知値は起動許可へ補完しない。

既存SERVICEID001～008/BACKCRED001～008と新backup-only request固定読取（BREQUESTCRED001～008）、InspectorUnitSnapshot/Probe UNIT001～016の固定BACKUP追加を横展開。Inspector receipt10許容を維持、backup10拒否/0のみ/freshInvocation/全cgroup空/前後stable/未観測・旧結果・timeout拒否。固定backup start/stop controllerはshell/任意Unitなし、M/A保持markerとrequest lifetimeを独立latchで確認。外部Unit native試験で専用worker入口→request→実dump/list→fresh結果回収、親M/A/総budgetは未接続を成功へ代用しない。

新・変更classのline/method/class/branch各100%、全counter0、NullAway/SpotBugs0、全null/境界/例外/並行/再送（new-only再実行拒否）と独立期待値。共有credential/NSS/probe変更は保存source固定の全Production6回帰、105canary/owner/JUnit/必要XMLを先に照合。Failed/flaky/skipped/not-runは合格禁止。source/試験/collector固定中は変更を混入しない。期待値をProductionmethodで生成しない。

実行command Java25.0.4/Maven wrapper/offline repo、限定`test -Dtest=<対象group> jacoco:report spotbugs:check`、共有security結線後6module `clean test`＋完全指定report/check、Node絶対path。対象branch/source/日時/exit/実値/coverage/BUG/SSC/証跡hashは139以降/provisional PG309へ保存予定。実DBdump・秘密/rawtoken/session/privatekeyはGitへ保存しない。正式run24/48.3%を限定成功で更新しない。
