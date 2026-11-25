# NK-WEB-002 検索・Scenario・Animation worker 単体結果

対象 `2710773181cd387f9bacf74275e9d0bfc84b53e5`、製品Core `cf08e414be9f877b851a387704350d5e7c980209`。AnimationBrowse 8、Search 9、ScenarioDetail 8の全25件が一実行で成功。失敗、エラー、スキップ各0。検索のcontext付きmedia fixtureはPT-WEB-FRAG-003として保持。既fixtureの入力・期待・10秒条件は正確に保持した。

処理済み正規Maven Web資源34と現入力が一致。Spotless3、Checkstyle、SpotBugsは指摘0。PMDは三fixtureで原15から生3へ減少し、残りは有限合成workerの箇所。生結果と正式品質の適用判断を区別する。補助の三件と補助クラスはPG45324の同一byte証拠を用いた。

BUG-3847は該当3画面で再試験完了。YKT-2997残7。実Browser、実サービス、正式F03と六製品451は未受入。 [PG45326](evidence/PG45326-current-content-dom-worker-fixtures/manifest.json)
