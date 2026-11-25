# NK-WEB-002 管理フォームworker 単体テスト仕様

対象は UserCreateTemplateResourcePortTest、UserDetailTemplateResourcePortTest と試験専用 ViewFixtureWorkers。RD FUN-009、UI225 §4–5、SS313、BUG-3846、YKT-2997、WBS-F03/2-2-bを参照する。製品の画面変換は承認済み合成入力を使用し、端末の実認証・JDBC・実HTTPは使用しない。

| Test ID | 操作と独立した期待値 |
| --- | --- |
| PT-UCREATE-DOM001～008 | 新規画面の既入力とDOMの既期待値を維持。並行8入力は個別username・Role・有効値と非表示項目をそれぞれ照合。 |
| PT-UDETAIL-DOM001～008 | 詳細画面の既入力とDOMの既期待値を維持。並行8入力は個別usernameと操作種別を照合。 |
| PT-WEB-VIEW-WORKER001 | 先行例外と終了未達を独立入力。先行は同一参照、終了未達のassertは抑制1件。submit、cancel、10秒終了確認の固定順。 |
| PT-WEB-VIEW-WORKER002 | 代理を正常終了と未終了に設定。固定タスクの結果17を確認後、cancelと10秒終了確認を各一回。未終了単独の場合は主assertとして通知。 |
| PT-WEB-VIEW-WORKER003 | 先行例外と終了割込みを別々に入力。両例外はそれぞれ同一参照。割込み状態を復元し、試験終了時に試験自身が消去。 |

現正規Maven処理済み資源とその親POMを照合し、Java 25、既定SDK、Jupiterで三fixtureを選択する。一次失敗保持の新三件は試験工具の品質確認として別に計上する。通常試験16件は失敗、エラー、スキップがすべて0の場合だけ局所成功。四指標は試験補助クラスの単一execで確認し、製品Javaや画面のcoverageには加算しない。実行argv、環境、対象commit、原XMLと終了、SHA-256、静的検査はPG45324へ記録する。
