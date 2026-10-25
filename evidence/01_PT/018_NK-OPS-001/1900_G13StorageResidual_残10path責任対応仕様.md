# G13.07・storage残十pathの複合試験/helper責任対応

着手前監査補足：BUG1746/YKT1497、元485/486 whole-file参照不整合を修正前起票。一次binding是正後も正規全WBS監査は旧e7資格候補と新64446の実scope差でHOLD、全監査を合格にしない。初期traceは最終品質受入と分離可能という477に従い当source path候補補完を継続する。後で当485更新の486 hash再同期と元semantic不変検査を行うが、古い全体資格/coverageを新sourceへ転用しない。

2026-10-25 12:12 JST、G13_STORAGE_RESIDUAL10_OWNER_V1/WBS-G13.07。開始見積 low.5/base2/high4週次共有pp、一群cap10pp。1899のfresh現在窓残10%以下/取得不能を停止基準とし、旧累計90/80・下限/buffer・累計由来小capは使わない。source64446不変更、既登録279/全Java1104と元941/歴史943・元費用/原runを保持する。

対象はstorage未登録残10pathだけ：LinuxStartupFileLockTest、PrivateDirectoryEntryTest、ChildDirectoryPublicationTest、LinuxProcessExecChild、OwnedDirectoryFactoryTest、PrivateChildDirectoryTest、EnumValueCatalogCompatibilityTest、FactoryResourceScopeTest、ExceptionValueContractTest、LinuxExecDescriptorsChild。実ソース/fixture/Main参照・既Program責任・既TestID/要求/設計を静的に対応し、根拠を確定できたものだけexact所有候補に加える。複合試験の共通費primaryを一つとし、参照先複数を別owner分として重複計上しない。確定不能ならUNKNOWNと理由/必要資料を残す。

静的調査で確定した責任oracle（mapper実装前）。全pathはstorage同packageで、下記Mainは485元論理ownerを保持する。helper二つは親Testに参照される実行fixtureであり独立@Test件数ではない。

|source class|主対象Main|主担当/費用owner|種別|
|---|---|---|---|
|LinuxStartupFileLockTest|LinuxFileLock|WBS-P003-06|TEST|
|PrivateDirectoryEntryTest|OwnedTransferDirectory|WBS-P003-04|TEST|
|ChildDirectoryPublicationTest|OwnedTransferDirectory|WBS-P003-04|TEST|
|LinuxProcessExecChild|LinuxProcessExec|WBS-P003-06|TEST_HELPER|
|OwnedDirectoryFactoryTest|OwnedTransferDirectory|WBS-P003-04|TEST|
|PrivateChildDirectoryTest|OwnedTransferDirectory|WBS-P003-04|TEST|
|EnumValueCatalogCompatibilityTest|ServiceCredentialId|WBS-P003-07|TEST|
|FactoryResourceScopeTest|ResourceScope|WBS-P003-08|TEST|
|ExceptionValueContractTest|StorageIoException|WBS-P003-04|TEST|
|LinuxExecDescriptorsChild|LinuxExecDescriptors|WBS-P003-06|TEST_HELPER|

参照補足：Enum catalogのServiceConfigFilesも同P003-07、FactoryResourceScopeはResourceScope.acquireの失敗・所有表/SS333 SSC308、例外値はStorageIoException固定reason/SS333・PT-F03-EXC005。二helperは各LinuxProcessExecTest/ LinuxExecDescriptorsTestの明示class参照を静的に確認し、構成に使うdirectory等の共通費を別計上しない。private directory三Test/OwnedDirectoryFactoryはOwnedTransferDirectoryの生成/公開/親子の保持で同P003-04、実native成功はこの表で認定しない。

実file/native/exec/credential/Root/VM等の副作用を含む可能性があるため、当群は通常PTの再実行ではなくsource path trace補完のみ。class load/JUnit/Java/native/DB/VM/Root/実ファイルfixture操作なし。ソース本文の読取と公開WBS/Test仕様・台帳の参照、自己所有のPython metadata検査だけ。既成功試験・原4222/normal/static/archは再演しない。metadata結果をPT PASS/coverage/正式受入へ加算しない。

開始前既後続索引/元source・WBS監査→十pathの責任根拠記録→exact resolver/原join→固定責任表から作る独立golden/未知隣接/原owner優先/正しいcanonical shapeでcost一field拒否→現在source・旧279不変・登録増分/残数の独立確認→1901結果/append-only計測・456/460/公開delta/保存。元見積と群費は補完成果/追加発見/手戻り/tool費を分け、不明N/T・専有費・工数はnull。成果が閉じても正規停止条件まで次の独立PG/PTへ継続する。
