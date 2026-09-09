# NK-DAT-001 検査credential権限単体テスト仕様書

InspectorCredentialAccess constructor/requireDirectory/requireAesFile。RD DAT-009/OPS-009、UI212/241/251、SS343 §6.2、QA-046/UIC-006/SSC-049、PG-D-132。設定metadataだけを扱い、credential値・file内容を使わない。期待ACLはLinux UAPIから独立に手組みし、production methodからexpectedを作らない。

| Test ID | Method・fixture/input/操作 | 独立期待値 |
|---|---|---|
| PT-DB-INBOX-113 | rootAclFileAndDirectory: UID1/1000/4294967294、file0440/dir0550、44byte固定vector | root+専用UID ACLだけ成功、size54/69、dir nlink1/2 |
| PT-DB-INBOX-114 | ownedReadonlyFallback: 同UID、file0400/dir0500、空ACL、RO true/false | ROだけ成功、root/他owner/ACLありは拒否 |
| PT-DB-INBOX-115 | inodeTypeAndMode: symlink/FIFO/socket/device/dir/file不一致、permission全bit変異 | exact type+mode以外拒否、setuid/gid/sticky等を含む |
| PT-DB-INBOX-116 | linkSizeAndUidBounds: file nlink0/2/負、dir0/負、size53/70/負/MAX、UID0/負/4294967295 | 固定不正例外、許可境界は成功 |
| PT-DB-INBOX-117 | everyAclBitAndShape: 独立44byteの全352bit反転、version/endian/不足/追加、USER/GROUP/MASK/OTHER差分 | 全拒否、他userや権限0追加も拒否 |
| PT-DB-INBOX-118 | nullAndInputOwnership: null/空/未知ACL、検査後のinput変化、再呼出 | null契約拒否、不正拒否、input非変更・非保持 |
| PT-DB-INBOX-119 | concurrentPoliciesDoNotCross: 100呼出、異なるUID/形式の独立検証 | 各期待許可/拒否を全future回収、共有mutable状態なし |
| PT-DB-INBOX-120 | errorsAreFixedAndNonMutating: 各失敗のmessage/cause/suppressed、所有権変更なし | 固定値のみ、input不変、IOなし |

実行は通常のJava25 Maven clean verify、Ubuntu26.04.1/toolchain421。対象commit/branch/日時/command/exit、8件actualと全4種coverage、BUG/SSC、sanitized証跡/hashは032で確定する。探索成功だけでは完了にしない。native属性取得、inode保持/IO/close、実systemd/main/親backup gateは別途未完了。IT/ST・実NK CHR合格へ算入しない。
