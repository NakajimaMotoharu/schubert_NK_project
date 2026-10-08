# PG550 pre-SAVE固定Root-only回収

NK-OPS-001、RD OPS/BAK/MIG、UI251、SS343353/SSC221/QA047、BUG841/YKT610、PG549-C004補助。Design-only sourcec54c5a54d/PR57 normal merge→origin/main b609bbc2849924c7749616d6962e44a6dfb882e4公開確認、code/tool/evidence混入0。

|Test ID|対象・入力/操作|独立期待値・根拠|
|---|---|---|
|PT-OPS-PG550-H001|identity固定Root/null/型/UID/argv/ticks/親・余剰子、wrapper一回予約順/新run/hash|Root575778/ticks4093969/argvSHA4dfeee73…/sudo親575776・全UID0・全task子0だけ。literal independent fixture、unknown/foreign/不正型拒否、source文字列で単一pidfdTERM/先行durable予約/new-only・同helperpreflighthashを検査|
|PT-OPS-PG550-H002|preflight metadata十Ref/全原値二読/全7immutablepayload/old+unusedcandidate全187hash・各pin signature・SAVE不存在/全peer-advisory0/M-A FD-FLOCK|actual0/source9ddde… dirty explicit4helperSHA/3.787426831s/privateLogSHAee3f2ee5…、oldsourcea2/currentf699/native9/全24-462/元Backup/旧原本/未使用candidateBOMa224不変。Root-only前提をRef/DB取得済みpairへ拡張しない|
|PT-OPS-PG550-H003|source固定後same4helperでexecute一回、private before/予約→fixedRoot pidfdTERM143→原値二読/新Refbus正常/allowner-peer-advisoryFLOCK0|終了0は限定新回収のみ、旧verifyの143/closeUNKNOWN保持。whole原値厳密不変/namespace/start/reload/DBwrite0、before=after・completeprivate seal、旧wrapperverify再実行0。現在未実行|

Commands: `python3 -B tools/quality/vm/050_s1/pg550_presave_root_test.py`→`.../pg550_presave_root_native_v1.py preflight`成功済→source固定push→同`execute`一回。管理test/静的のみProductionPT/counter加点0、正式source8587/1964PT/53scope不変更。実時刻/環境・source/hash/exit/Rootproofをsanitizedmanifestへ保存、private DB/raw原本/permit/署名実体Git0。

H003実結果=source795f5ade045c551a9eb3ca0b8c4cb73eddeb273d/2026-10-08T03:03:04.553605～03:03:09.861610Z/actual0/5.308008917s、四helperはpreflight同byte。Root before=after fd96ee8dfb31b31bc9c457712ea257cd354382e4623cf17b5373daba71f97432/22,177,069B、completebf1efcd0…/203B、oldRoot消失・新metadata十Ref/bus正常・全旧peer/advisory/FLOCK0/全元原値不変二読。oldverify remote143保存後sourceHEAD差をhostassert1で拒否、normalcloseUNKNOWN不変更。sanitizedmanifest=evidence/provisional/PG550-presave-root-execute-v1/manifest.json、raw Git0。

次はPG549別v4 tools/source/run、M-A/RODB/十Ref→候補hostreadonly固定→typedBOM→全newscope正常verify→別fresh completed code-only公開。v2後続手compile/v3は不合格保全（annotationCP/try閉鎖、外部依存版置換BUG842）・VM未使用。新v4は正規annotationCP・警告0compile/管理6+3+CLI9・external-version独立1test/Pyflakes0。旧UNKNOWNの成功化/未実行合格0。
