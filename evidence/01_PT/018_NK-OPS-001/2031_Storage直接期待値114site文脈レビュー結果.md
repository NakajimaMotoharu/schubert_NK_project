# Storage直接期待値114site・文脈レビュー結果

2026-10-26、仕様2029/G03_PROTOCOL_STORAGE_EXPECTED_CONTEXT_V1・開始.5/2/6 cap10。Protocol95は2030/10146（manifest SHA739f22ba2d61ab18b668870d4dcacba8b4d349e1a967c0693377886265f41c36）へ保存。Storage114は以下のsource文脈を静的読取で点検した。新製品実行/fixture操作/外部接続0。既索引ddのlineを使い、UID以外sourceは当d17と同byte、UID七siteは075/10136の旧token保持証拠により原lineと現在hashを区別する。

|source|site数|独立根拠・限界|
|---|---:|---|
|ChildDirectoryPublicationTest|3|Test-local固定open/publish/sync/close順、失敗点literalによるclose数、fixture所有rootFdのSet。実操作は今回未実行。|
|ExistingFileAccessTest|1|固定rwx------のJDK Posix権限集合、拒否後非改変。|
|FactoryResourceScopeTest|7|Test-local固定イベント順/空、hardcoded suppressed行列0000/0111/0111からcharAtで期待数。製品のsuppression生成をexpectedに再利用しない。全例外・競合の動的再検証はしない。|
|LinuxDirectoryCallsTest|1|固定rwxr-x---のJDK Posix集合、製品modeから生成しない。|
|LinuxExecDescriptorsTest|6|固定fd/flag syscallイベント五site、残一はJDK自己child.pidと固定INHERITED文字列の相関property。製品生成PIDを期待とせず、実child起動も今回なし。|
|LinuxFileLockTest|19|12件OptionalのTest callback固定返値/empty、七件固定open/flock/body/close順。返値保持と所有/後始末のpropertyでありnative kernel排他の実証へ換算しない。|
|LinuxFilesystemClassifierTest|1|Test-local UAPI magic→name四literal Map、製品分類表をexpectedに使わない。|
|LinuxHostDirectoryCallsTest|4|Test-local固定uid/open/close/path/flagイベント。fixture引数を実host観測と混同しない。|
|LinuxInodeSecurityTest|7|一UIDはJDK unix:uid/unsigned、六ACL期待はTest helperの固定Linux UAPI hexと指定uidのlittle-endian独立展開。goldenが製品getxattrを呼ばない。原index line/旧hashと当075のhash/token対応を分離。新当native試験の実行なし。|
|LinuxProcessExecTest|7|六固定argv/env List及びTest-local ThreadLocal入力。残一はJDK自己child.pidと固定出力の相関で、製品PID生成でexpectedを作らない。実execは今回なし。|
|LinuxSealedProofTest|4|Test-local固定create/mode/write/fcntl/read/close順及びfixture reserved fd。実sealed proof資格を静的検査で認定しない。|
|LinuxStartupAdmissionTest|18|17固定P=129/A=128のclose順/flagイベント、残一は固定PUBLIC ASCII byte。root metadata/実boot/permitの動的受入には転用しない。|
|LinuxStartupFileLockTest|10|四Optional固定callback返値/empty、六固定open/dup/flock/closeの独立順。実OFD/維持/競合は未実行。|
|OwnedTransferDirectoryTest|1|固定rw-r-----のJDK Posix集合、実inode/公開操作は未実行。|
|PrivateChildDirectoryTest|9|六Test-localイベント/List/Set、失敗点literal。二件JDK別pathのunix:inoによる保持/競合結果相関、一件固定失敗点とexists後条件。JDK観測を製品getterと同一視しない。元shared二siteは10122へ別保存済み。|
|ResourceScopeTest|2|固定body/inner-close/outer-close順のTest-local List。|
|ServiceConfigFilesTest|1|Testが書く固定a×16384文字をそのまま独立expected、製品YAML出力から作らない。実file読取/作成は今回なし。|
|ServiceCredentialIdTest|4|固定filename五件/role別kind五件、宣言したenum memberは識別identityでwire生成getterではない。実鍵アクセスなし。|
|ServiceCredentialLocationTest|2|001は固定ROOTのJDK Path期待。005は同Production先行getter期待のためBUG1798/YKT1549を先行起票し是正必要。現状を独立oracle合格としない。|
|StorageAttributeGuardTest|1|固定rw-r--r--のJDK Posix集合、拒否後非改変。|
|EnumValueCatalogCompatibilityTest|6|Test-local固定十identifier/filename/role/kindと二roleの固定enum identity集合、実credential内容を使わない。|

114中113はこの直接expected-call文脈において同Production出力を期待へ戻す欠陥を見いださず、独立値と補助propertyを区別した。残一はBUG1798。これは113試験PASSではない。Protocol95と合わせ209siteの文脈点検、先行七を含め直接216の索引候補を点検したが、identifier202/constructor等の間接依存・全forward/reverse TestID/要求/branch/実行証跡joinは未完。補助propertyの当source runtimeも今回未実行。

10148は原site集合/当hash/UID例外bindingと本review hashを結合するmetadata工具だけで、Main/Test実行や新期待値算出はしない。BUG1798は次群で既PT-OPS-CREDLOC-005のexpectedをJDK固定Pathへ是正し、同sourceの通常五PT/全class counter/静的/全Main不変を検証する。既HOLD/正式1964-53/17-190/工数null/QA051finalを維持し、実native/鍵/Root等へ動的展開しない。
