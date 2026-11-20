# NK-OPS-001 F02の直接archive依存境界

WBS-F02-a、SYS-005、SS311 §3／§5.2・SSC028、PG-D516、BUG-3472／YKT-2771。入力は手書きの架空型をコンパイルした6合成JAR。実ファイルopenとfixture型初期化は0。JDK25.0.4／ArchUnit1.4.2、Linux x86_64。実行はrepo直下で `python3 evidence/01_PT/018_NK-OPS-001/input/5626_f02_file_archive_dependency.py before` または `after`。独立確認は `python3 evidence/01_PT/018_NK-OPS-001/input/5627_f02_file_archive_dependency_independent.py`。

- PT-F02-ARCHIVE-001/002/006/007はController／ProtocolのZipFile／JarFile直接openを違反とする。
- PT-F02-ARCHIVE-008/009はProtocolのScanner(Path)／PrintWriter(String)直接openを違反とする。
- PT-F02-ARCHIVE-003～005、010～012は借用InputStream／Writerまたは明示file adapter。上記直接open規則の許可対照。
- 独立期待は固定SS311の責務とJDK25の公開constructor形に基づく。null、例外、スレッド、再送は検査入力となる依存の分類と別であり、fixtureの処理を実行しない。

PG41218は12条件、誤って見落とした6を保全。修正 `6cf10b2ce3ba3450386da69d60a55a84b4094ee2` のPG41220で新12条件と既影響23条件が期待どおり。検査器は意図した違反19を検出し終了1、反証の比較runnerは終了0。PG41222でJDK公開constructorと13 Controller／169 Protocol sourceにおける対象四型の字句参照0を独立に照合。領域全体、実六JAR、451、正式受入の更新なし。

- [修正前](evidence/PG41218-f02-archive-owner-baseline-v1/manifest.json) SHA-256 542fb9d21dfef60411486a09e49817d952c730250b77b6205eb4218eaf42728a
- [修正後](evidence/PG41220-f02-archive-owner-fixed-v1/manifest.json) SHA-256 f89f22f99f0b3dda0122f616d45d08739bd227f3c91a850d1f79a7ebffb6c9b8
- [独立確認](evidence/PG41222-f02-archive-owner-independent-v1/manifest.json) SHA-256 de1809ae72bd23503e206db5626078c5fb0c9cbadb043dd7629ac1cb67d1c8b9
