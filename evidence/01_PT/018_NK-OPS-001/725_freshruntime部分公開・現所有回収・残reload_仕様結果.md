# NK-OPS-001 freshruntime部分公開・残処理

## PG2002/2003/2006 残reloadの実閉鎖

operator750dd1e512e8a001d36297c5de4f19a2da64d054/current0fd-PG1846/boot3d69。PG2002六ABI0（UTC00:40:58.591184→00:40:59.901313）、2003新immutable stage0、finish-runtime0/sourceQualifiedtrue（00:41:51.279656→00:42:29.797836）。既644B/SHA78f148…/元inode28-15250をNOFOLLOW保持し再作成・書換え無し、残runtime reloadだけ一回。logSHAf042c8a24726a568f743a859c1ce0a59c0d202d6585498b01f873e5039caffa7、全scope正常返却。旧1983actual143/UNKNOWNはそのまま。

別PG2006独立全post0（00:42:41.883192→00:42:50.752753）、payloadSHA4b43ebc56bf977b3dcb431ea16c0ab3a293727f882ba4819d8d91f86374a1be1、全beforefd6412f31de9af59219a0fe28f49ce0d073b074a7ff83ca3516a22e462568b83。全24DB/32config/187署名/旧原本Backup/旧Unitinode・全10kernel/管理0、native26/treeb9dc不変、cached同run明示resume/Success10を確認。新外部start/当source新activation真正DONE/owned停止/native/正式451は未実行。証跡はW/pg2002-frozen-v1.safe.json、pg2003-{stage,finish-runtime}-v1.safe.json、pg2006-existing-runtime-independent-post-v1/manifest.safe.json。限定成功だけで正式1964PT/53scopeや全leaf0を更新しない。

関連OPS009/UI251/SS3436.13/SSC259260283/QA047/BUG1198/YKT966。現在Production0fd/PG1846/BOMee75、正式1964PT/53scope/全leaf増分0。親真正DONE・新Unit0or10・四100/native/CHR/正式451は未完。

|Test ID|対象・独立期待/実結果|証跡|
|---|---|---|
|PT-OPS-PG1983-PREPARE001|fresh fileEXCL/force/readback→正常runtime reload/正常closeを期待。実fileのみ完了、時刻range拒否→retain。oldsource16fd8→898347/143UNKNOWN/sourceQualifiedfalse、成功化0|pg1983-prepare-resume-v1.safe.json/logSHA1ae12f3f…/BUG1198|
|PT-OPS-PG1988-DIAG001|現在host332236/Java498727101FD/Ref4987584FD/DB498756・solegateをreadonly取得、actual0/oldprivatebefore-logだけ/reload予約0/外部start0|pg1988-fresh-resume-retained-diagnosis-v1/payload32b6c305…|
|PT-OPS-PG1989-PARTIAL001|rootdir元属性・子全identity/mtime非減少/target九属性・独立nativeargv全literalを確認。fileSHA78f1/root644/link1/644B/ino15250、currentdirinode5514、当byte・namespace保持、actual0|pg1989-fresh-resume-partial-time-diagnosis-v1/payloada80d371c…|
|PT-OPS-PG1991-PROOF001|全24表/32config/187signed/原本Backup/旧Root13failed10/canonical6phase/newFILE厳密meta・全101-4FD/二OFD/solepeerを独立二読、actual0/signal0|pg1991-fresh-runtime-partial-full-proof-v1/proof1dc3cb85…|
|PT-OPS-PG1993-GUARD001|実generated currentpid/ticks・子→親TERM一回/既知pipeのみ/正常gate返却・file/reload変異0、独立test1PASS/static0|pg1993_partial_runtime_pair_once_handoff_test.py|
|PT-OPS-PG1993-RECOVER001|同connectionfresh→Ref/Java各一回通常TERM/有限reap→全資源0/queued同gate正規継承、actual0/旧closeUNKNOWN保持|pg1993-partial-runtime-pair-once-handoff-v1/payload55546a2b…/freshproof1deb094d…|
|PT-OPS-PG1995-POST001|別全read-only scopeでpendingFILE/全meta・byte不変、cachednoresume/Success10、全旧原本24/32/187/26native/旧Unitinode保持・全kernel/actor/client/advisory/FLOCK0、actual0/source898347c0ce9c820f17df2ab17c433e54e1312478|pg1995-partial-runtime-recovery-full-post-v1/payloadc4c40107…、UTC00:33:46.360570→00:33:55.016189|
|PT-OPS-PG2001-EXISTING001..002|実new20source/static0、既FILE九属性/SHAの独立literal・write/chmod/unlink/utime禁止、残reloadだけ/旧sourcegolden不変更。独立2PASS|pg2001_existing_runtime_finish_test.py|
|PT-OPS-PG2003-ENTRY001|実namespace globals/oldprepare引数拒否・archive/root/producer/source/actionjoinの独立1PASS|pg2003_existing_runtime_finish_dispatch_test.py|
|PT-OPS-PG2006-ORACLE001|producer関数を呼ばず別literal/二configdelta・元beforephase/timewindow/同既runtime全属性・正常十Ref/全資源0を独立判定、1PASS|pg2006_existing_runtime_independent_post_test.py|

1995新全beforeSHA `b3bb209b57ca297b43d5b1fc78e191fcef2dbbf1c9e1645c445b212291a202fe`、native26/SHA `b9dce89b8ab71f077937a4eb2fd87141d5e7e3dcf300e3614080d42fd51a2683`。旧file唯一inode `28/15250`、全metadata `[28,15250,0,0,33188,1,644,1791850609774873609,1791850609774873609]`、SHA `78f1488383951e0fc2716bcf63ab41f75c64e975440e7f5e079fd6129f8612ec`。これを未知mtime許容/再作成で補完しない。

時刻調査：実dirctime/mtime1791850609774000000とfile1791850609774873609、保存before kernel timestamp1791850597287000000。旧精密mutation_beginは未保存でnull。host64/guest128/実writerguest64では「dirmtimeが精密begin以前」の再現0、一般tmpfs精度の仕様と断定しない。独立全predicateは同savedbeforeからのnamespace不在→EXCL→現在全meta/byteへ結合できるため、残完了では現在file全九属性を固定、旧耐久before～回収完了timestampの範囲を保持する。未保存値を推測・oracle変更で成功化せず、旧1983は失敗のまま。

次：新source固定→2002六ABI→2003新immutable stage/実producer→finish-runtime一回。旧1984/newFILEを書換えず、新SAVE2005へreload予約のみ耐久保存、一回通常reload timeout20、同owner/DB/M-A/十Ref/FILE全9field/正常close→2006別全post。終了/未知は未合格保全。Root外部startはまだ0、freshobserver/native保全・耐久一回startと真正終端/owned停止が後続必須。実command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes> python3 -B tools/quality/<tool>.py`、各manifestは日時/source/exit/payload・loghash、privateW/guestにrawを保全。秘密/session/cookie/token/DBdump Git格納0。管理工具変更でProduction fullMaven再発行0。
