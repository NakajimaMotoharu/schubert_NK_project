# PG515 実ISSUEDから正規失効・単一API退役

Program NK-OPS-001 / WBS-N10 / SS343・353 SSC209/210、QA047、BUG817～819/YKT586～588。Production a2e98ce9e96c42425921e3686e8ae7a94bff9e6c / PG495 / schema028。運用工具だけの試験をProduction PT・WBS ACCEPTED・正式認定へ加算しない。

## 独立仕様と事前条件

- PT-OPS-PG515-001: Boot cc9、署名187/current PG495、元親bbb6dc/PID5872/ticks380665のtimeout143、元4startup ISSUEDを全値認証する。readIssued→data-only ownerは期限切れparentsGuard、存在しないAPI launch/Pair/publicationを生成しない。permit/owner/markerの原値はPG505全rawを独立に再読する。
- PT-OPS-PG515-002: 新M→A→専用RWbatch/readCommitted/ACfalse/advisory→十Ref、独立RO全24table/452batch/全原本102/config/nativeを保持し、Expiry→Cleanup→Artemisを所有停止する。依存停止済みBrokerへ再stopせず、同INV/vendor全journal/PID1 stop done/kernel全消失を確認する。
- PT-OPS-PG515-003: 全10kernel終端後だけ、認証したactual permitを用いて既canonical revokeを一回発行する。同boot/epoch/run/cutoff/activationのINVALID、permit_sha256=-をSS343の独立literal vectorで期待する。currentのinode/size/mtime/ctimeとstartup directoryの必要metadata以外は不変、外部仕様/DB更新/startは0。
- PT-OPS-PG515-004: INVALID readRevoked→元data-only owner→Root空同API markerを限定退役しdirsync。mutation中の3/4集合以外を拒否し、終了は元permit/owner/currentだけの3file。独立期待値をProduction serializerで生成しない。
- PT-OPS-PG515-005: 認証302位置・遷移1699位置のone-shot故障を実FD/syntheticRoot/tmpfsへ注入。currentは故障位置に応じ元ISSUED又は正規INVALID以外を許さず、permit/ownerと同API markerを維持する。未知closeを正常化せず、実M/A確認とusable held rootだけで隔離を試みる。root/A/M消費後は未保持権限による修復0。
- PT-OPS-PG515-006: DB rollback/close→十Ref逆順Unref/bus close→root→A→Mが正常帰還した新scopeだけ受入する。元親143/旧PG513工具143/closeUNKNOWNを変更しない。再実行・stage・start・migration二重発行0。

## 工具・host結果

`bash tools/quality/vm/050_s1/pg515_issued_api_compile_v3.sh` actual0、Werror0。Java issued35102assert/302read-fault/1699transition-fault、既single-api20907assert/1304fault、Python212assert/vendor-PID148assert。数はassertでありProduction PT数ではない。初回compile-v1は試験fixture overrideのIOException宣言不整合で拒否、失敗source/class/logを保持。v2限定正常後、実TOOLS固定v3を別compileし全当試験を完走。null/空/未知enum/壊れたcurrent/foreign namespace/nonempty marker/所有PID・LOCK・同世代・dependent stop拒否を含む。

## 実行・未受入

実command `python3 -B tools/quality/vm/050_s1/pg515_issued_api_native_v1.py`。new-only TOOLS pg515-issued-api-tools-v3 / SAVE pg515-issued-api-recovery-v1。guest同boot現在値再認証、旧Ref309634/Java309605消失・peer/advisory0・ISSUED raw SHA87a7556e…・旧cohort不変は実readonly確認済み。nativeは未実行のまま着手し、actual終了・Root全原値・safe hash manifestを後記する。全親DONE/native100/CHR/正式・PGPT全完了は未達。
