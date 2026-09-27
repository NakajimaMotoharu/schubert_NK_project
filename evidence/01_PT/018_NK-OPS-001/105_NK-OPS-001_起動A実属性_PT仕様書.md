# 起動A実属性PT仕様書（PG294・未認定）

Program NK-OPS-001 / StartupAdmissionFile.create/tryExclusive/withView/verify/identity/ViewOwner.close。
RD SYS-002/004・OPS-009、UI212/251、SS341～343、SSC086/087、BUG265/YKT199、471 D04/05。

| Test ID（PT-OPS-ADMISSIONLOCK） | 独立期待値・fixture/操作 |
|---|---|
| 001 | NOFOLLOW実inode、合成root/tmpfs属性。callback時観測所有FD0、reserved A128以上、外部flock20→終了後0 |
| 002 | host/private物理A違いはdevinoまたは独立OFD競合検査で拒否、callback0 |
| 003 | 7属性の欠落/型/null、dir/file mode・link・size・UID/GID、ACL/tmpfs/hostRO境界をliteralで拒否 |
| 004 | symlink/hardlink/nonregular、callback後inode交換も成功にしない |
| 005 | 各open/negativeFD/close故障。callback前故障0回、normal callback後再検査故障は1回だが非成功。所有close各1 |
| 006 | 通常/未知bodyとclose組合せ。未知identity優先、全取得済みcapability消費、秘密診断なし |
| 007 | 同一Aで8thread、保持中winner1、終了後取得可 |
| 008 | 全null、不正path、nativefactory通常UID拒否、NIOtyped属性 |
| PT-OPS-NATIVE-013 | 隔離VM root/ProtectSystem=strict/NoNewPrivileges/ProtectHome/PrivateTmp、actual host/private identity・tmpfs・crossflock、callback時root観測FD0 |

正常/境界/異常/例外/null/並行を上記で検査。業務再送は本adapter対象外。期待値はSSのliteral属性、独立kernel/flock/FD一覧でありproduction出力から生成しない。native013は隔離工具でPID1/Unit由来・現在permit・全root/schema/Ops・実NKを証明しない。
command/環境/commit/hash/coverageは106とprovisional/PG294 manifest。BUG265 REDは旧adapterのcallback時残FDを独立再現、初期TDD失敗は合格へ算入しない。

