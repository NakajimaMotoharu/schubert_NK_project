# Maven依存のオフライン照合

WBS-P018-02/2、RD171 SCM-005、SS352 §13。対象は `tools/quality/verify_maven_advisories.py`。検証済みのMaven CycloneDX 1.6構成表一つ、Mavenリポジトリ、固定SHA-256のOSV ScannerとMavenコーパスを入力とする。構成表のJAR・依存グラフを先行照合し、空設定・一時領域で明示した構成表だけを検査する。

| Test ID | 合成入力と独立期待値 |
| --- | --- |
| PT-OPS-OSV-001 | 一座標・三byteの固定JAR、正規終了0、全座標報告。終了0相当で指摘0、offlineの固定引数を実証。 |
| PT-OPS-OSV-002 | 一座標・合成ID `OSV-TEST-0002`。報告は座標とID、詳細報告は出力しない。 |
| PT-OPS-OSV-003～004 | 実行ファイルの異なるSHA-256、コーパス欠落・SHA-256不一致。処理開始前拒否。 |
| PT-OPS-OSV-005 | 報告の座標欠落、重複、他ecosystem、異なるsource型。未成立。 |
| PT-OPS-OSV-006～007 | 元終了127/128、指摘有無と終了値の双方向不一致。未成立。 |
| PT-OPS-OSV-008～009 | 不正JSON、JAR不一致、空構成表。未成立。 |

PG42738は `f8e89da09ad62c9523dfcaf35d442e6060d7c36c`、dev-foundation。上記9件成功。OSV Scanner 2.7.1とPG42658で固定したMavenコーパスで、既Protocol構成表の1座標を本入口から実際に検査し終了0・指摘0。コーパス期待値を変えた際は終了2で、結果JSONの出力なし。製品JUnitの追加実行0、外部CI・実配布・QA-061のライセンス判定・全451は未実施。コマンド、時刻、終了値、固定入力と証跡hashはmanifestを参照。[PG42738](evidence/PG42738-p01802-offline-advisory-ci-v1/manifest.json)
