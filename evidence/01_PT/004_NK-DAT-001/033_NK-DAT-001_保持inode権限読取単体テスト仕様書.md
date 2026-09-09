# NK-DAT-001 保持inode権限読取単体テスト仕様書

InodeSecurityCalls/LinuxInodeSecurityのcreate/accessAcl/readOnlyFilesystem/effectiveUid。RD DAT-009/OPS-009/FIL-006、UI212/241/251、SS311/343 §6.3、QA-046/SSC-049、PG-D-133。Storage低位SPIであり、業務policy/key読取りは含まない。

| Test ID | Method・入力/操作 | 独立期待値/fixture |
|---|---|---|
| PT-DB-INBOX-121 | actualAclAndUid: public temporary fileへsetfacl、保持handleで読取 | Linux UAPI手組み44byteと一致、ACLなし空、UIDは実file owner数値と比較 |
| PT-DB-INBOX-122 | filesystemFlagsAndFailures: 実local mount・注入flags/return | 実FileStore readonlyと比較、flags0/1/other/混在のliteral結果、非zero失敗 |
| PT-DB-INBOX-123 | aclReturnAndErrnoBoundaries: public call portでresult/errno/bytes | 1/max成功、0/超過/負・ERANGE/EIO/EACCES等拒否、61/95だけ非取得空 |
| PT-DB-INBOX-124 | canonicalCapabilityAndBounds: 任意/相対/別pid/非canonicalFD/範囲/null | JNI呼出前固定拒否、正当FDと上限1/65536のみ到達 |
| PT-DB-INBOX-125 | platformAndSymbolAdmission: OS/arch/lookup/null/欠落symbol | Linux/glibcの許可ABI・3symbolのみbind、他は固定失敗 |
| PT-DB-INBOX-126 | heldInodeSurvivesReplacement: public fileのrename・別ACL file置換 | callbackは旧inodeのACLを読む、path再openは新inode、close後同path不可 |
| PT-DB-INBOX-127 | concurrentReadsStayIndependent: 100calls・各scope arena | 各ACL/UID/readonlyが不変、全future回収 |
| PT-DB-INBOX-128 | interfacesAndRedaction: null call port/unsigned EUID/real不在FD/エラー | fixed cause-free failure、path/errno非保存、UID unsigned境界は正確 |

setfacl2.3.2は既存導入済、fixtureはTempDirの公開byteのみ。No real credentials/daemon/DB。Java25・Ubuntu26.04.1 x86_64、通常Maven root clean verify、全4種coverage100%/静的解析0を要求。対象source/branch/日時/command/exit/8actual・scope hashは034で確定する。AArch64の実動作・systemd配布・file reader/parent/IT/STは未実施と区別する。
