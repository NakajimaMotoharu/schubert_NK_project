# NK-OPS-001 保持inode環境file読取単体テスト仕様書

PG-D-152/SSC-049（先行58f7e8b7）。OPS-009、UI251、SS311/343 §6.9。InspectorEnvironmentReaderのconstructor/readStatic/readRun/read/metadata/attributeとNioIo。期待値はSS literal bytes・fixture自身のdev/ino/sizeとUnix metadata、独立resource countを用い、Production生成expected禁止。

| Test ID | method | 事前条件・fixture・入力/操作と独立期待値 |
|---|---|---|
| PT-OPS-EFILE-001 | staticReadAndBoundaries | 実隔離directory/inode/readonly channel、root/groupだけ合成。静的literal2行と65536byte version列を読み、独立byte一致、書換なし、借用root生存、新規返却配列 |
| PT-OPS-EFILE-002 | runReadAndBinding | runtime属性合成、UUID/時刻のliteral2行。同run成功/別run・±1μs・年境界・破損拒否、SQL/child起動なし |
| PT-OPS-EFILE-003 | permissionAndFilesystem | euid/UID/GID/type/mode/link/size/device/ACL、static許可local/RO・runtime tmpfs/RW、未知/不正組合せを独立表で拒否。type拒否後はnative追従照会/content openなし |
| PT-OPS-EFILE-004 | metadataAndNull | 各必須metadata欠落/異型/null、channel/FS/ACL欠落、constructor依存/null・GID上下限。全て明示非成功、値補完なし |
| PT-OPS-EFILE-005 | boundedReadsAndMutation | advertised sizeと実read差、短縮/伸長/EOF/0/count/position不正、開始終了size/mtime/ctime変化、max/max+1、read-only open flagsと上限+1buffer。無限read/巨大allocationなし |
| PT-OPS-EFILE-006 | inodeReplacementAndOwnership | read中に同名交換→保持元inodeを読んだ後に新inodeとの差を検出し失敗。symlink/hardlink/dir/不足、root identity変更。借用rootは閉じずowned channel/entryは全close |
| PT-OPS-EFILE-007 | ioFaultsAndRedaction | openEntry/attrs/ACL/FS/openChannel/size/read/channelClose/entryClose各出現位置とprimary+close複合故障。全取得資源close、raw path/value/cause/suppressedなし、例外を成功にしない |
| PT-OPS-EFILE-008 | concurrentAndConstructor | 64独立読取・異なるrun期待、入力/返却所有分離、有限wait。default Nio境界の実metadata/readとnonroot拒否、借用rootのclose後拒否 |

本機unprivilegedの実inode/FFM/IO上へroot:schubertまたはroot:root/tmpfsを合成する箇所を明示。実root/systemd配備を合格としない。directoryはread-only操作対象で作成/修復/削除せず、fixtureだけtestが管理する。失敗/skip/未実装は不合格。Java25/Maven固定・探索Batch+Storage verify→新正式run全reactor clean verify/NullAway/SpotBugs/4coverage100%→collector全scope/hashを014・manifestへ記録。BUG発見時は修正前起票する。
