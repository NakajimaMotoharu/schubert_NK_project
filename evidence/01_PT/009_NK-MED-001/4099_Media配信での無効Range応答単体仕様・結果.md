# NK-MED-001 無効Rangeの配信応答

WBS-P009-04/2、FUN-005～007、UI223/237、SS333 §10.1・§10.2／SSC-476、PT-MED-PORT011。対象は `MediaRangeService.deliver` から `HttpByteRangeParser.parseFirst` と応答への接続。

長さ2,097,155の自己所有メモリchannelと記録用Responseを使う。ASCII外の単位名と符号付きlong上限を超える終点の2入力をそれぞれ渡す。いずれも416、Content-Rangeは当固定長を含む `bytes */2097155`、Content-Lengthは0。レスポンス本文の取得とchannelの読み出しは各0。長さ確認用channelを各1回開いて各1回閉じる。最初の失敗後に同じ1枠を使用できることも、同serviceへの第2入力で確認する。

JDK25.0.4、JUnit1.13.4、JaCoCo0.8.15、Linux x86_64。実行は入力5639、独立検証は入力5640。PG41250は現Main `6c2e8b027818c8dac0ed0f895edb85658e9c4ff1`、新1＋変更影響の旧10＋fixture反証1が計12成功。失敗／エラー／skip／未実行各0。対象のSpotBugs指摘・欠落・処理は各0。HTTP接続・原本ファイルへの操作は0。

PG41252は13物理のrawを検査。line 131/139、method 26/39、class 9/9、branch 58/74、instruction 635/736。生PMDは旧と現の各9。プログラム全体の実行・coverage100%、正式品質、実配信、CHRは未受入。

- [動的PG41250](../018_NK-OPS-001/evidence/PG41250-media-current-range-response-port-v1/manifest.json) SHA-256 4157fa87b942a680279fb1195873ebe34f7353a80c92cf53a6a880c13927f6d7
- [独立PG41252](../018_NK-OPS-001/evidence/PG41252-media-current-range-independent-v1/manifest.json) SHA-256 d96aa29fef40d137f2421e10b7ea9a6eeee17c0bbc5ad362e078c970e1e66cbd
