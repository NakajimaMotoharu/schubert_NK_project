# G13.07・storage直接companion Test十九pathの所有対応仕様

2026-10-25 11:42 JST、G13_STORAGE_COMPANION19_OWNER_V1/WBS-G13.07、事前 .25/.5/1pp・cap1固定。fresh62/reset1793382075、元90捕捉下限87＋cap1＋保全2=90、正確累積/専有N/T/工数null。source64446不変更、原941/歴史943/旧260と費用・PTは保全する。

対象はstorage Testのうち、下記既製造classと同packageで直接対になる19pathのみ。既941の同Main owner/cost責任と、当Test本文の実class参照/独立期待値の責任を照合しexact候補を追加する。単に同package・名称が似るだけでは割当てない。残10storage pathはこの群で推測せず未登録のままとする。

P003-04：LinuxHostDirectoryCallsTest、ExistingFileAccessTest、LinuxDirectoryCallsTest、OwnedTransferDirectoryTest。
P003-05：StorageRootInspectionTest、StorageRootLayoutTest、LinuxInodeSecurityTest、StorageAttributeGuardTest。
P003-06：LinuxExecDescriptorsTest、LinuxFileLockTest、LinuxStartupAdmissionTest、LinuxProcessExecTest、LinuxSealedProofTest。
P003-07：ServiceCredentialIdTest、ServiceCredentialLocationTest、ServiceConfigFilesTest。
P003-08：LinuxMonotonicClockTest、ResourceScopeTest。
P018-03：LinuxFilesystemClassifierTest。

各Testはsrc/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/、Mainは同module main/java配下でTest suffixだけを除いたclass。元Main責任は485を正とし、不一致や当source hash不整合は成功にせず停止/保存する。実native/FD/file/credential/Root操作を含み得るTestであるため、**Test本文の静的読取だけ**を行い、class load/JUnit/native/VM実行は一切行わない。HOLDの解除、拒否対象を探る試行、未実行をPASS化する行為なし。

同source正常9246入力/current hash、literal19owner golden、旧260canonical保持/未知隣接/元論理優先/正しいcanonical shape→cost単一field拒否を独立metadata postで確認する。期待増分はsource path登録19だけ（1085→1104、main965不変、test120→139、未登録704→685）。全method/RD/UI/SS/TestID多対多trace・Program/451受入ではない。新製品PT/Main/coverage/正式/工数率増分0、資料1897・append-only開始/終了・456/460へ実測/未確認範囲を保存する。
