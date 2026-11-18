# BUG-3264 API五Recorderの生coverage結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `4d74ed903f987f2e5d61372c14f9b7b91a5d2880`。PG39274はRecorder元40＋GENMET元8で全48初回成功、失敗・エラー・skip・未実行0。Poolの不正modeに同hash異値二件を追加し固定CONFIG_INVALID・監視登録0を確認した。既存の他試験本文とMainは同じ。PMD生33は元26とPoolの有限worker及び参照同一性7を個別確認し、関連静的適用0。

PG39278独立は物理14・正CRC13。標準四counter全到達。PG39282は同じexecの生205L／85M／13C／136B／1335I全到達。前回未到達だったenumのvalueOf 3、Counts recordのequals／hashCode／toString 3は今回すべて到達し、五constructorの生Bは各14/14。package-infoは実行Code無しとして物理に含めた。元32回は同一execの必要再資格、今回固有追加16件、試験定義追加0。F03の全体品質・451／YKT2691の他対象は継続。

Linux amd64、JDK25.0.4／Maven3.9.12／JaCoCo0.8.15、dev-foundation。[独立証跡](evidence/PG39282-f03-api-recorder-unfiltered-with-generated-v1/manifest.json) SHA-256 `3b2596b9909f05d7357ea311f192df4a5fbc5428740d716ef83a113e58562d33`。command・終端・XML・CRC・静的・生coverage・圧縮stream元hashを参照できる。
