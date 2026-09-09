# NK-DAT-001 検査AESfile読取単体テスト仕様書

InspectorCredentialLoader/load、AesCredentialFile、InspectorCredentialException。API .file、RD DAT-009/OPS-009/FIL-006、UI212/241/251、SS311/343 §6.4、QA-046/SSC-049、PG-D-134。

FixtureはTempDirの実FileChannel/保持inodeと実行時CSPRNG32byteから独立構築するASCII/Base64 envelope。key値・file内容は保存証跡/Gitへ入れない。正常経路のroot UID/許可mode/readonlyは明示したpackage-local OS metadata portから合成し、独立検証済み031/033のpolicy/native読取へ追跡する。ProductionデフォルトIOの実不正root拒否も確認する。親systemd root-managerの実配布試験の代替とはしない。

| Test ID | Method・事前条件/入力/操作 | 独立期待値 |
|---|---|---|
| PT-DB-INBOX-129 | validAllIds: 4固定名と実file、version1/16長、54/69byte | 元keyとcopy一致、current/previous区別、明示filenameだけ使用 |
| PT-DB-INBOX-130 | optionalMissingOnlyBeforeOpen: current/previousの欠落とIO途中missing | previous entry open前だけempty、currentと途中missingは固定失敗 |
| PT-DB-INBOX-131 | rootAdmissionBeforeRead: root不正owner/mode/link/ACL/RO、実default IO | file openより先に拒否、補正・書込みなし |
| PT-DB-INBOX-132 | inodeTypeBeforeNativeOrContent: symlink/FIFO/device/socket/directory | type拒否、対象へのACL/内容openは0回 |
| PT-DB-INBOX-133 | fileAttributesAndNulls: 各属性の欠落/null/型違い、size/link/permission | 固定失敗、IO先行なし、NPE正常catchなし |
| PT-DB-INBOX-134 | boundedReadsAndEof: partial/EOF/short/long/0進捗/size不一致 | 全長一致だけ成功、70byte超readせず停止、無限retryなし |
| PT-DB-INBOX-135 | postReadChangesReject: dev/ino/uid/gid/mode/link/size/mtime/ctime/ACL/ROの前後変更 | channel/entry/rootの差異で失敗、material返却なし |
| PT-DB-INBOX-136 | ioAndCloseFailures: attrs/ACL/RO/open/read/size/channel close/entry close/root再検証 | 全て固定原因非保持失敗、後始末とbuffer全0 |
| PT-DB-INBOX-137 | heldEntryAndRootReplacement: 読取中path rename/差替え | 保持inodeからだけ読む、rootの変更検出は拒否、外部targetへ逸脱しない |
| PT-DB-INBOX-138 | constructorAndEnumContracts: null/不正EUID/4 enum/valueOf | 境界拒否・nonsecret固定名、root所有はcallerで維持 |
| PT-DB-INBOX-139 | ownedBuffersAreCleared: parser成功/不正/IO例外でchannel借用bufferを観測 | load終了時全buffer0、独立returned copyのみ残りcaller消去 |
| PT-DB-INBOX-140 | concurrentReadsAndRedaction: 100load/異なる4key/原因sentinel | 全future/キー対応確認、例外/表示へ値・原因を出さない |

通常Java25 Maven root clean verify、failed/flaky/skipped/not-runを合格に算入しない。4種coverage100%/静的解析、source/branch/日時/OS/tool/command/exit/Test ID actual/BUG・SSC/manifest hashは036へ記録する。前後metadata・retained inode・key内容期待値はproduction helperから生成しない。実credential配布/codec4鍵接続/main/parent/実NK CHR/IT/STは別残件。
