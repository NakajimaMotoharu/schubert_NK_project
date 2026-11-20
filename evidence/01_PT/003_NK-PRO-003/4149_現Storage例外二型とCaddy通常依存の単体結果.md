# 現Storage例外二型の単体試験

NK-PRO-003、FIL-001〜009、UI237、SS333／342、SSC461。WBS-P018-07/2／F03/2-2。PG40612でCaddy旧runが持つStorageIoExceptionとReasonの物理差を確認した。元Caddy20件／Service12件はそれぞれのrunで保持する。

| Test ID | 入力・期待値 |
|---|---|
| PT-SCN-008-F01〜F02、BUG-2718 | 固定Reason、未知／null、普通causeとsuppressed、SQL nextと有限cycle、同一Error、元オブジェクト不変。旧fixtureのliteralとidentity比較。 |
| PT-OPS-SSC461-STORAGE-NULL-001 | nullの追加edgeは固定診断のNPE。nullのfailureはedge未呼出しでNPE。普通例外のcauseとsuppressedもそのまま。 |
| StorageReasonValueContractTest#reason001ClosedCatalogFactoryAndRedactedFailureKeepTheirIndependentLiteralContract | 固定3名・順序・factory・配列のコピー、未知値とredactionを独立literalで照合。 |

現Maven Storage JARの2型だけで、既5件＋新1件を単一execで実行した。6成功、失敗・エラー・skip・未実行0。生line 27／method 10／class 2／branch 12／instruction 143の未到達0。片方の分岐分母0は実コードの条件がないため。対象Test 2ファイルのCheckstyle／formatter各0。PG40614の実行とPG40616の独立証跡を保存した。SHA-256 `9a338a4a854e82b12029677962c16d1702169c5994af42de0d3c43ac097392d3`。

本物Caddy、TLS、manager、同親budget、実FD/native、全Storageおよび全451は別の証拠が必要。
