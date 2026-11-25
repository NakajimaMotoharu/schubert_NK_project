# NK-WEB-002 MockServlet画面worker 単体テスト仕様

FUN-004/006、UI223/235、SS313、BUG-3849、YKT-2997、WBS-F03/2-2-b。三つの既fixtureを現正規Maven資源と現候補の局所Web型で実行する。MockServlet内の合成入力、表示用固定値だけを用いる。元のFutureおよび終了確認10秒、context所有者の終了順、タスク数、既assertionを保持する。二重失敗、単独timeout、割込みは現と同じ補助のPG45324独立結果を参照する。

| 対象 | Test IDと独立期待値 |
| --- | --- |
| AnimationTemplateTest | 既PT-SCR-046～053。053は合成64入力を別々に描画し、menu件数・一覧行・画面文字列を文言まで照合。 |
| ScenarioDetailTemplateTest | 既PT-SCR-017～024。024は合成64入力で個別タイトル・本文・表示用値を正確に照合。 |
| AnimationWatchTemplateResourcePortTest | PT-WATCH-DOM001～004。003は8入力でタイトルと合成mediaのhrefを独立確認。 |

Java 25/Jupiterで20件を選択する。失敗・エラー・スキップは0。traceとHTML出力は当run専用領域。現実のWeb起動、DB、実メディア、実Browser、CHR、全六製品451への加算は別。
