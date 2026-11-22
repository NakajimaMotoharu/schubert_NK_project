# Current組立・対応表と保持COPYの八製品型検査

NK-MIG-001、WBS-F03/2-2-b・P019-03、SS343、SSC408～416、451。CurrentMigrationAssembler、MappingManifest、MappingVerifier、Projection、MigrationMasterCopyDataset、CopyFingerprint、CopyManifest、CopyVerifierが対象。元独立期待はPG42830（Current投影12）、PG42832（組立24）、PG42856（保持COPY照合20）、および対応表と写しの各仕様を参照。外部原本やJDBC driverを使うコードは解析入力から切り離した。

PG42882、2026-11-23 JST、Java Core e8368d22c4。Maven offline、JDK25、root POMと同じNullAway 0.14.1／Error Prone 2.50.0。現JARの11物理全てが再compileのbyteと一致。補助41物理も既許可の固定hashから選んだ。NullAway、SpotBugs、Checkstyleはいずれも0。PMD生1は固定のDigestSink受渡しで、メッセージダイジェストと件数だけ保持し、親OutputStreamのcloseが無操作であるため適用外。生報告は保存した。[PG42882 manifest](evidence/PG42882-migration-copy-eight-main-typed-v1/manifest.json)

新しい通常PTの起動なし。先行証拠のscopeを現型付き証拠と結合し、全製品451、業務DB／COPY、実環境、正式受入は別に検証する。
