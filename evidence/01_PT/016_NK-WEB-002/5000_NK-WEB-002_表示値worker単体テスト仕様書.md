# NK-WEB-002 表示値worker 単体テスト仕様

FUN-003/004/006、UI223/234/235、SS313 §6.1、BUG-3848、YKT-2997、F03/2-2-b。ページ区間、階層、検索結果、Animation一覧の純粋な値の投影を対象にする。既入力・assertionの独立性、8 worker、元タスク数、各Futureと終了の10秒を維持する。二重失敗や割込みに対する試験専用補助の独立結果はPG45324。

| 対象 | Test ID・独立期待値 |
| --- | --- |
| PageViewModelTest | PT-WEB-174～181。明示した件数・区間・端・独立fixtureを再利用。179の100入力は別々に計算し、Futureは四fixtureの検証結果をそのまま伝える。 |
| ScenarioHierarchyViewModelTest | PT-WEB-182～193。固定のGame/Route/File表示と範囲、190の並行境界。 |
| ScenarioSearchResultsViewModelTest | PT-WEB-206～213。固定の結果行・音声表示・頁境界、213の並行境界。 |
| AnimationViewModelTest | PT-WEB-230～237。カテゴリ・行の固定表示、237の並行境界。 |

現正規Protocolのpublic artifactと、純値四群に必要な既Web物理の現source適用を照合し、Java 25/Jupiterで36件を明示実行する。候補の同一execで対象物理のcoverageを採り、未命令を保存する。現実のWeb起動、データ、API接続、正式全六製品は別途判定する。
