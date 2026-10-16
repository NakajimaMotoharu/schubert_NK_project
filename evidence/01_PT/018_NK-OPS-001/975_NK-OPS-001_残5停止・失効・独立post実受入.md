# NK-OPS-001 残5停止・失効・独立postの限定実受入

2026-10-16、source7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e/PG3976/BOM0a409301/boot79a。QA047、SS343/353 SSC287～289、BUG1338～1343/YKT1104～1109。451やRoot元30分/既Unit期限は不変更。

| Test ID | 操作・独立oracle | 実結果 |
|---|---|---|
| PT-SSC289-METADATA-TERM | fresh全5FD/権限/単task/世代二読、新十Ref＋host排他、固定791348のpidfd通常TERM一回/15秒・30秒内PID消失 | 成功、旧UNKNOWN closeはfalse、Root/sudo/host/VM signal0 |
| PT-SSC288-INSPECT-ACTUAL | 既4182 partial6ae32eabの別fresh M/A/RODB/本人TCP/十Ref、全189/24/原値/32宣言 | 10:42:46Z actual0、新scope正常返却、停止0 |
| PT-SSC288-FIVE-STOPS | 同partial6ae32eab、旧Caddy18項目/INV/旧PID-kernel空を観測のみ、Web/API/Expiry/Artemis/Cleanupの各一回予約/通常stop/真正terminal/全kernel・普通pool消失 | 10:44:56Z actual0、必要5stop/Caddy再stop0、全6terminal data成立。元Root143・旧4152 actual255は失敗のまま |
| PT-SSC288-REVOKE | SS089 ASCII/LF/key順cutoff_utc固定vector、state INVALID/digest -だけの差 | typed canonical revoke成功、全33起動entry保持、intent不存在で不要生成・削除0 |
| PT-SSC288-INDEPENDENT-POST | 別post c2acd4d2、新M/A/RODB/十Ref、全24・原本Backup/keys/native/全189/全32/全Unit世代、全DBpeer/advisory/flock/kernel0、新scope正常 | 10:45:27Z actual0、before/after SHA両方e77657150336362b6010058384db9d8a71be650b99c9b7c688c67b1cc862746c。旧50native＋同INV普通terminal二fileだけ、CRC/session資格は後続 |
| PT-SSC289-OUTER-CLOSE | 全子真正0後、外側十Ref正常Unref/host同inode gate自然返却・元host/SSH終端 | 元exec85274 actual0、driver545bb84f、新十Ref正常。旧工具のclose正常化なし |

実行operator d024419c6/branchdev-foundation、commandは`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg4200_metadata_continuation.py recover`。同sourceの前提73＋新3工具76/静的0は974参照、Production PT追加0。Java/class4112/既partial/postはbyte再利用・再compile/再stage0。公開PG4206に元結果・manifest/hash/environmentを保存し、raw入力/DB/FD/journal/nativeはguest/PG379私有に保全する。

本受入は限定回収・全新scope/別postの範囲だけ。BUG1332 Root timeout原因・元親正常DONE、新通常経路/新source資格、native CRC/session/coverage、F03/CHR/451/trace/正式全体/QA051finalは未完。正式1964PT/53scope・旧個別17/190履歴・工数nullを更新しない。
