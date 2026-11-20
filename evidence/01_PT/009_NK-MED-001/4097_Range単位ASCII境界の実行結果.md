# NK-MED-001 Range単位ASCII境界の実行結果

2026-11-21 JST。PG41202は旧Main `559f5b5945e82374e0843dcfae11a8d07faef1ea`。PT-MED-RANGE-UNIT-001の失敗1、対照の成功1、エラー・skip・未実行各0、終了1。原因をBUG-3470へ修正前登録した。

修正commit `300f0a09705c755778c4a6c5f003a0aaabc5e4f9`。PG41204は試験source `6c2e8b027818c8dac0ed0f895edb85658e9c4ff1` で、同修正Mainを使用。新規2と修正対象の既存6の計8成功、失敗・エラー・skip・未実行各0、終了0。JUnit起動前の初回準備でMain出力の列挙にTestが混じり停止した。出力先を分離した後のJUnit起動は一回。旧成功をcoverageへ合算していない。

PG41206は元の単一execとMainの物理5classをCRCとSHA-256で再照合。生カウンタはline 44/44、method 21/21、class 4/4、branch 32/32、instruction 273/273。Selection interfaceはbytecodeに実行命令を持たない。手動除外0。SpotBugs 4.10.4は対象Main 5物理と新Test 1物理について指摘・欠落・処理エラー各0。全6製品・実配信・451の判定は未実施。

- [修正前manifest](../018_NK-OPS-001/evidence/PG41202-range-unit-ascii-baseline-v1/manifest.json) SHA-256 f3fa8f0f99235a847e4143813925626c7b4da5cf37654fac2a17fb46511b24ed
- [修正後manifest](../018_NK-OPS-001/evidence/PG41204-range-unit-ascii-affected-v1/manifest.json) SHA-256 c879718e0132f37d326ac917d29378479347d11bc58ba49b9050a28c703f3d10
- [独立検証manifest](../018_NK-OPS-001/evidence/PG41206-range-unit-ascii-independent-v1/manifest.json) SHA-256 28cffcf61b6a98dfbf31a6fb09cd5c50adaf13374d61ffbf534cafa88479e04d
