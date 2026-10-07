# PG501 cold所有準備・独立PT仕様（v1失敗・SSC207限定回収）

2026-10-08: v1は077/078部分成功、079 NEW_NAMESPACEでRO親契約拒否・SQL発行前、080正常未受入。BUG810/YKT579。SS207設計onlymain2937a7137/PR42。旧native-v1再発行禁止、143/closeUNKNOWNを保持。
PT-OPS-PG501-081..104: fixed pid/ticks/argv/Root/parent/childrenの独立24正常・欠落/null/foreign/型拒否fixture、signals0、Production PT0。
PT-OPS-PG501-105: 当bootのRoot1804/ticks162765と子1830/ticks162864、immutable class/Pythonの既実byte pin・全task子集合・M/A実FLOCK/inodeを前後照合。新Root私有予約、全10cold/full18/全24table442batch/永続102/namespace0・candidateRO・peer0を二読。child→parent pidfd TERM一回だけ、消失/全peer-advisory-lock0/全原値二読一致を期待する。旧DB idle期限は正常closeに算入しない。失敗前の原本と独立PG498afterをoracleとし、私有rawはGitへ出さない。
command: python3 -B tools/quality/vm/050_s1/pg501_cold_handoff_test.py; python3 -B tools/quality/vm/050_s1/pg501_cold_handoff_native_v1.py（immutable pin/同owner/新予約成立時一回）。実結果・hashは別manifestへ保存。

NK-OPS-001 / WBS-N11・N14/G13.07、RD SYS-011/OPS-009～017の担当参照。
UI211/212/243/251～253、SS343/353 SSC206（設計onlymain b8651513b/PR41）。
Production source a2/PG495、工具は別source、Coverage/Production PTへ加算0。

| Test ID | 対象・入力/操作 | 独立期待値・根拠 | 実行状況 |
|---|---|---|---|
| PT-OPS-PG501-001..076 | bounded/cold/epoch_valid、literal full18/ASCII epochとactive fixture、null/欠落/foreign/上限/旧boot/ISSUED | SS343 canonical fieldsから独立goldenを構成、encoderによるexpected生成0、76正常/拒否 | host76/compile-Xlintall-Werror0。Native未実行 |
| PT-OPS-PG501-077 | currentboot/Root同peer・M/A fd/flock/ticks、専用batch DB/advisory/他peer0、十Ref/manager/kernel二読 | PG500新bootcc9・PG498after hash固定、全10cold/profileと全24/442/永続102原値一致。旧PID/boot/raw namespace再利用0 | 未実行 |
| PT-OPS-PG501-078 | 同所有下にPG495だけfreezeCandidate→typedBOM/approval/source再認証 | BOMf699/187/SQL28/history29、approval固定rawと一致、readonly実判定。旧成功だけでsource確認としない | 未実行 |
| PT-OPS-PG501-079 | same activation保持・empty/new-only namespaceと所定coverage owner/mode・新INVALID | 全24/442・5永続rootの完全原値不変、startup epoch.current1件だけ、canonical ASCII独立fields、当boot/同run/cutoff/activation/permit=-、oldRuntimeRetired0 | 未実行 |
| PT-OPS-PG501-080 | DB rollback/close→十Ref逆順Unref/bus正常→A/M正常→complete記録 | peer/advisory0とholder/kernel/全原値、全新scope正常の現実証。UNKNOWN/部分終了を成功にしない | 未実行 |

工具初期goldenは合成run/activation/dateを使用しprivate rawをGitへ出さない。
実SQLはPG498afterの全24/442/全列を独立二読し、32MiB超/非0/変質は拒否。
host76はpure guardsのみで、所有・実操作・normal close/fault/競合の網羅を完了扱いしない。
現実故障/競合の残matrixはN16/G04に別管理し、同試験/共有費は重複加算しない。

command: python3 -B tools/quality/vm/050_s1/pg501_cold_test.py;
bash tools/quality/vm/050_s1/pg501_cold_compile_v1.sh;
python3 -B tools/quality/vm/050_s1/pg501_cold_native_v1.py（前提・current所有確認後一回）。
失敗時はphase/typeだけを非秘密記録しRoot同所有を隔離保持、再付着して認証する。
不明状態で同nativeを再発行/旧raw復元/業務start/新ISSUED/DB変更/force killしない。
