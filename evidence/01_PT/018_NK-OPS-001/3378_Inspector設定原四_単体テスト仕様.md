# InspectorLaunchConfiguration原四 単体テスト仕様

PG17350/event3637/PG-D1085、source6b53・HEAD8ab1ec89aa7fdfb3d7456aeecc6652b31d48fbb2。事前低1/標準3/高6共有pp cap10、primaryF03・canonical owner維持。関連NK-DAT-001/DAT009/OPS009/FIL006/UI212241251/SS343§6.8/341/352・QA046/SSC049。Program InspectorLaunchConfiguration constructor/read/value/toString/Invalid、原whole InspectorLaunchConfigurationTest四つ。SettingsTest3は既現15458で成功済み再演0。

|Test ID|method|独立入力・期待値|
|---|---|---|
|PT-DB-INBOX-221|validConfiguration|固定literal五keyのsnapshot、UUID000...002a/Instant2026-09-17T00:00:00.123Z/絶対Path/URL/version二値、無関係値非保持、constructor/read null fail-fast|
|222|missingUnknownAndArguments|各必須欠落/null/空、未知/大小文字alias/nullkey/args一件拒否・固定例外/cause/suppressedなし|
|223|scalarBoundaries|4096/256/36/32/65536超過、NUL CR LF、root/URL/canonical UUID/Instant/µs、年1/9999端/4096pathをliteralでassert|
|224|versionAndSnapshotContracts|空要素/duplicate/非ASCII/17字拒否、1/16字許容・元Map clear後version不変/immutable|

PT_DEFAULT：原whole/Main全体、InspectorSettings/InspectionRun/InspectorDatabaseConnections.databaseName（Patternの静的parserだけ、constructor/open/DriverManager/TIEを呼ばない）を読了。全て公開文字列/Map/Set/Path値、実file/DB/credential/session/key/Root/VM/native操作なし。URL/credential directoryは文字列であり接続/読取りではない。Main全一Source outerとInvalid二Codeを分母へ残し、従来NoCodeと混同しない。

command: python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17350_inspector_config_four_pt.py
原whole不変fresh一JVM/一session、FESaborted0/XML/CRC/input/actualOSJDKを記録し、独立post全分母/四counter・literal期待値/negativeを確認する。期待値をProductionから生成しない。実startup/DB/全451/CHR受入は別未達。実行前結果/coverage未確定。GroupResolver8は実getent/child、OwnerFrame4はnative clockを含むためwholeHOLD、抽出/再試行0。
