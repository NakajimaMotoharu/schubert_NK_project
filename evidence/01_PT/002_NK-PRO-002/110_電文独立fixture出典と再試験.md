# 固定長電文の独立fixture出典・再試験

UI233～236、SS322 §13、SS323、SS354、QA-054／UIC-011／SSC-336、BUG-3716／YKT-2916。WBS-G03.01の局所実績。

- PT-PRO-002-P07～P09、PT-CODEC-AUTHERR-001～003、LayoutFieldCatalogTest 3件とPayloadTypeCatalogTest 6件。承認版から独立抽出した64 layout・389 field・287 digestを照合。WLGEVT01では従来REQUESTを固定入力として互換を照合し、ACTION/MENU_VIEWEDの組合せは別のWebLogActionContractTestの現13件で確認済み。
- PT-OPS-ORIGIN-PRO001～004。UI234～236とfield TSVのSHA-256をGit固定版から計算し、正規の4リンクは一致。独立の交換入力で、UI235旧ハッシュ、旧fieldを指すgolden、欠落、重複、意図しない参照をそれぞれ検出。修正前実資料のCLI結果は終了1・不一致2件、修正後は終了0。
- 変更はfixture二つの出典コメント。全行の意味・期待ハッシュ287・製品JARは同一。選択した既存15件は新fixtureで全成功。旧全171件の原証拠は保持し、今回の実行と別記録とする。JaCoCoの原execを保存し、四カウンタ集計・正式451の判定には使用していない。
- 実行はJDK25.0.4／JUnit 1.13.4／JaCoCo 0.8.15。対象commit・command・入力ハッシュ・原XML・結果は [PG43596試験manifest](../018_NK-OPS-001/evidence/PG43596-protocol-fixture-provenance-guard/manifest.json)、出典再計算は [PG43594照合結果](../018_NK-OPS-001/evidence/PG43594-canonical-protocol-golden-provenance/manifest.json)。
