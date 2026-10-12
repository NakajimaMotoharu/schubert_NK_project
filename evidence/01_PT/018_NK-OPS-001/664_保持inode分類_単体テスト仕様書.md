# NK-OPS-001 保持inode分類単体テスト仕様書

Program LinuxFilesystemClassifier（storage）/InspectorEnvironmentReader.NioIo/EnvironmentInodePolicy（batch）。RD OPS009/FIL006/SYS004、UI251、SS343/353 SSC269、WBS-P018-03.01/.02、共通利用caller費用重複0。設計だけmain1c5083fa0/PR111、実装・影響PT・native/正式は未受入。

PT-OPS-FSTYPE-001（fst001）: 独立手書magic0xEF53→ext2/ext3/ext4 family、0x58465342→xfs、0x9123683E→btrfs、0x01021994→tmpfs。glibc LP64 statfs sizeof120/alignment8/f_type offset0、bsize/spareに別値を置き誤offsetを検出。同じinstanceで値変更→unknown0拒否→tmpfs復帰、fresh syscall6回を検証。Productionからexpectedを算出しない。

PT-OPS-FSTYPE-002（fst002）: syscall -1/1/int境界は有効magicを書いても拒否。null、欠落/空/異prefix/相対/非canonical fd/負/MAX超え/過長/子path拒否。失敗やnullを正常へ変換せず、readonly classifierが所有/ACL/readonly能力を代替しない。

PT-OPS-FSTYPE-003（fst003）: 非Linux/非LP64指定/gnu欠落/statfs欠落はfail closed、暗黙fallback0。PT-OPS-FSTYPE-004（fst004）: 当実retained FDのfresh分類と独立JDK FileStore type→手書family対応、FD返却後拒否。実secret/bodyを読まない。

影響PT: InspectorEnvironmentReaderTestの旧LOCAL全6＋family、StartupPermitFilesTestの実capability（単なるpathを認可にしない）・独立FileStore oracle、同delegate利用Publisher/Files/DurableRecordFiles/MaintenanceRunFiles/Backup等の既独立tamper/null/ACL/readonly/例外suite。元scan/全boundary/1800秒budget/Root/epoch検査不変更。固定glibc bits/statfs.h・Linux magic.h実版/hash、source/command/終了code/XML/四counter/静的結果は次結果へ保存、未実行をPASSにしない。既Main769成功全6は新sourceへ流用禁止。
