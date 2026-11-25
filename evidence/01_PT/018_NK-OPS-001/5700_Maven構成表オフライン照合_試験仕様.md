# Maven構成表オフライン照合の試験仕様

NK-OPS-001、WBS-P018-02/2、RD171 SCM-005、SS352 §13。対象は `tools/quality/verify_maven_sbom.py`。

実行例は `python3 -B tools/quality/verify_maven_sbom.py <software-bom.json> <verified-maven-repository>`。入力は指定した構成表と選定済みローカルMaven cache。SHA-256は参照されたJARをバイト列として読み出す。対象に合わせて生成したCycloneDX 1.6のMaven構成表を使う。依存JARのコードは実行しない。

| Test ID | 操作 | 独立した期待 |
|---|---|---|
| PT-OPS-SBOM-014 | 3-byte `abc`、固定SHA-256、rootと依存1件を入力 | hash照合1、依存行2、欠落宣言0 |
| PT-OPS-SBOM-015 | 標準JARとclassifier付きJARに異なる3-byte fixtureを用意 | 固定SHA-256と一致するclassifier付きだけを照合 |
| PT-OPS-SBOM-016 | 宣言欠落、空・不正な宣言、固定名・式を渡す | 欠落を座標で明示、不正を拒否、固定名・式は宣言あり |
| PT-OPS-SBOM-017 | ファイルを`def`に変更、SHA-256を重複 | 不一致と曖昧な宣言を個別に拒否 |
| PT-OPS-SBOM-018 | 重複行、未知行・辺、辺重複、行欠落、孤立点 | それぞれを拒否 |
| PT-OPS-SBOM-019 | 不正座標・PURL・外部symlink | 経路・参照契約違反として拒否 |
| PT-OPS-SBOM-020 | CLIで固定正例と重複キーのJSONを照合 | 正例は0、重複は1、失敗時に成功JSONなし |
| PT-OPS-SBOM-021 | 採取済み六製品の構成表を読み、各固定GAVのcacheを照合 | PG42606/08/10/12と一致する各モジュールのJAR件数、宣言欠落 |

Unitは `PYTHONPATH=tools/quality python3 -B -m unittest discover -s tools/quality/tests -p test_verify_maven_sbom.py -v`。実行結果のsource、exit、manifestはPG42630の証跡を参照。ライセンスの充足、配布クラスパス、CI稼働、製品通常PTと451は別工程の証拠。

## PG43048 root座標と参照の一致

PT-OPS-SBOM-025は3-byteの既依存と到達可能なグラフを保持したまま、rootのgroup、artifact、version、PURL、添付type又は重複qualifierを個別に不正化して照合する。期待は6形すべて拒否。PT-OPS-OSV-010はroot不一致時に外部scannerを発行しないことを合成呼出で確認する。

2026-11-23 JST、dev-foundation、工具source `eab10e0c3e`。修正前6形すべて拒否漏れ、修正後18工具試験成功。保存済みCycloneDX六件のroot座標は現六POMの明示・継承座標と一致した。実JAR・配布・advisoryの再検証には含めない。QA-061の配布条件と担当は未決。[PG43048 manifest](evidence/PG43048-sbom-root-gav-equivalence-v1/manifest.json)

PT-OPS-OSV-014（BUG-3897、YKT-3018）は正規pathを一度だけ決定し、そのpathから得たSHAと返却結果の結合を検証する。代理が指定する3-byteの別ファイルは、SHA不一致なら拒否し、abc一致だけ同pathを返す。真のscanner、cache、配布操作は起動しない。元正常・欠落・異SHAは同じ通常fixtureを参照する。
