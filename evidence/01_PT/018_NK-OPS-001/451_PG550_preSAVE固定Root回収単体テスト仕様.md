# PG550 pre-SAVE固定Root-only回収

NK-OPS-001、RD OPS/BAK/MIG、UI251、SS343353/SSC221/QA047、BUG841/YKT610、PG549-C004補助。Design-only sourcec54c5a54d/PR57 normal merge→origin/main b609bbc2849924c7749616d6962e44a6dfb882e4公開確認、code/tool/evidence混入0。

|Test ID|対象・入力/操作|独立期待値・根拠|
|---|---|---|
|PT-OPS-PG550-H001|identity固定Root/null/型/UID/argv/ticks/親・余剰子、wrapper一回予約順/新run/hash|Root575778/ticks4093969/argvSHA4dfeee73…/sudo親575776・全UID0・全task子0だけ。literal independent fixture、unknown/foreign/不正型拒否、source文字列で単一pidfdTERM/先行durable予約/new-only・同helperpreflighthashを検査|
|PT-OPS-PG550-H002|preflight metadata十Ref/全原値二読/全7immutablepayload/old+unusedcandidate全187hash・各pin signature・SAVE不存在/全peer-advisory0/M-A FD-FLOCK|actual0/source9ddde… dirty explicit4helperSHA/3.787426831s/privateLogSHAee3f2ee5…、oldsourcea2/currentf699/native9/全24-462/元Backup/旧原本/未使用candidateBOMa224不変。Root-only前提をRef/DB取得済みpairへ拡張しない|
|PT-OPS-PG550-H003|source固定後same4helperでexecute一回、private before/予約→fixedRoot pidfdTERM143→原値二読/新Refbus正常/allowner-peer-advisoryFLOCK0|終了0は限定新回収のみ、旧verifyの143/closeUNKNOWN保持。whole原値厳密不変/namespace/start/reload/DBwrite0、before=after・completeprivate seal、旧wrapperverify再実行0。現在未実行|

Commands: `python3 -B tools/quality/vm/050_s1/pg550_presave_root_test.py`→`.../pg550_presave_root_native_v1.py preflight`成功済→source固定push→同`execute`一回。管理test/静的のみProductionPT/counter加点0、正式source8587/1964PT/53scope不変更。実時刻/環境・source/hash/exit/Rootproofをsanitizedmanifestへ保存、private DB/raw原本/permit/署名実体Git0。

次はPG549別v2 tools/source/run、M-A/RODB/十Ref→候補hostreadonly固定→typedBOM→全newscope正常verify→別fresh completed code-only公開。旧UNKNOWNの成功化/未実行合格0。
