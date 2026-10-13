# NK-OPS-001 通常reload・限定回収の独立PT

関連OPS009/UI251/SS343・353/SSC283/QA047。Production候補source `0fd734195b4d5338f6b7e860e087cce561d49562`、releasePG1846/BOMee75。外部工具source開始c3999f79a、回収8f6bfb67d。正式1964PT/53scope・四100/native/実新UnitWARNING受入は未更新。環境Linux guest boot3d69/JDK25.0.4/Python3.14.4/systemd・DBは既PG1846署名設定を保持、raw情報は私有に保全する。

| Test ID | class/method・操作 | 独立期待値・実結果 | 証跡 |
|---|---|---|---|
|PT-OPS-PG1938-STAGE001|1938.main stage|新externalarchive/remote、当qualified1926byteのみnew-only配置。actual0/sourceQualifiedtrue。旧archive上書き0|PG379/pg1938-stage-v1.safe.json、logSHA6db9cef4…|
|PT-OPS-PG1938-RELOAD001|Pg1925PartialReload.main/References.reload|一回通常reload→全正常closeを期待。reloadは発行済み、8Unit補助表現差へ拒否。actual143、source開始c3999→終了8f6b、UNKNOWN/sourceQualifiedfalseを保持。合格算入0|pg1938-finish-reload-v1.safe.json、logSHAd53ff0c2…/BUG1193|
|PT-OPS-PG1943-DIAG001|1943.owner/PAYLOAD|現在101/9FD・同boot/current・reload予約・当solehostgateをreadonly取得。actual0、宣言・DB・原本変異0|pg1943-reload-retained-diagnosis-v1、payload147ef175…|
|PT-OPS-PG1945-CONFIG001|1945.read|32field全部。actual1・ExecStop省略へ拒否。未合格、旧slot保持|pg1945-reload-configuration-delta-v1/BUG1194|
|PT-OPS-PG1947-CONFIG001|1947実complete_configuration|実DBus空ExecStop確認、Requires/Afterだけset順序。actual0、8ExecStart補助五値のみclosed、全宣言同一/全state18不変/parent設定10|pg1947-reload-configuration-delta-v1、payload3d45c1a4…|
|PT-OPS-PG1948-CONTRACT001|reload_configuration_same|literal宣言tripleとclosed=(n/a,n/a,0,(null),0/0)のみ。8対象正常、31他field・8tuple各変更・foreign/2対象外/None/欠落/余剰/unknown拒否。独立test1PASS|pg1948_reload_closed_configuration_test.py|
|PT-OPS-PG1949-PROOF001|1949.payload current pair|当101/9FD・二OFD・管理DB soleTCP/advisory・全原本24表/32設定/署名187/十kernel/旧Unitinode/canonical6phase/旧Root13state・native26二読保持。actual0/signals0|pg1949-reload-retained-full-proof-v1、proof719017d92688423a588a109c0352317a20a89876c51303fd5f13ccccaec38d7c|
|PT-OPS-PG1950-GUARD001|1950 actual emitted payload|当pid/ticks/knownpipe/Ref→Java一回TERM、旧世代なし/reload-start0。独立test1PASS、generated/static0|pg1950_reload_pair_once_handoff_test.py|
|PT-OPS-PG1950-RECOVER001|1950.main QA047|同connection fresh全proof→一回ownedTERM→有限reap・資源0→同inodehostgate正規継承。actual0/新回収scope正常、旧工具closeはUNKNOWNのまま|pg1950-reload-pair-once-handoff-v1、payload6971de92…、freshproof3ef4d780…|
|PT-OPS-PG1953-POST001|1953.payload|別全scope閉鎖を期待。actual1・Ref取得前のconfiguration資格へ拒否、全post合格0|pg1953-reload-recovery-full-post-v1/payload af1579af…/BUG1195|
|PT-OPS-PG1955-DIAG001|1955 closed readonly|actual1/NoSuchUnit、Refなしの診断接続不備。reload/start/DB変異0|pg1955-closed-reload-configuration-diagnosis-v1/BUG1196|
|PT-OPS-PG1960-DIAG001|1960 fresh十Ref内readonly|actual0、全32設定は補助closedのみ/宣言同一、全18状態不変/設定10、全Ref逆解放/normalbusclose|pg1960-closed-configuration-ref-diagnosis-v1/payload785bd516…|
|PT-OPS-PG1963-SCOPE001..002|1963actualpayload/1960actualpayload|ASTからqualificationが十Ref取得後・同try内、finally逆Unref/busclose。独立2PASS、未知scopeを模擬fixtureで補わない|pg1963_reload_ref_scoped_full_post_test.py|

実command：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<private pyflakes runtime> python3 -B tools/quality/<各script>.py`、独立testは`python3 -B -m unittest <上表test files>`。source全体Mavenは候補1844/1845の同source3618・536suite/1643Main/static6zero資格を保持し、tool/doc-onlyの不要再Maven0。全体coverage100/CHR・正式gate未完のため当工具成功を工程完了へ加算しない。

次：source固定後1963別新slot全post。旧failed/143・途中269等から成功を補完しない。新Unit実WARNINGは後続合法fresh一回resumeで別受入、現Root13/Backup/通常reload再演禁止。私有証跡root=`/home/mini/codex/project1/work/pgpt-runs/PG379`、guest=`/var/lib/pgpt-s1-preservation`。Gitには秘密/rawFD・DB行・電文/tokenを格納しない。
