# TopBar診断・null補完と同source15class閉鎖PT仕様

BUG1832/YKT1583、群2404（開始1/3/7pp、cap10）。source73c18457afce837ecfc3687fc7aae84c04cca2c1。前source65のPG10454で唯一残ったTopBar.toString一method/一lineと、直接null契約を既純粋ScenarioHierarchyViewModelTestへ補完する。PG10459 plan-v2の二追加assert以外は元全token/期待/旧assertionを保持、Main変更0・新fixture0。PT-WEB-185へTopBar.from(null)のNullPointerException、PT-WEB-193へ固定literal TopBarViewModel[REDACTED]を追加し、原006仕様へ同時反映した。既Game actor/表示入力だけを使用し、認証・権限・アクセス経路や実DB fixtureを変更しない。

元MenuMvcTestの@BeforeAll等はそのまま実DB依存であり未実行/HOLDを維持する。当純粋部品の診断/値契約を通常単体試験するもので、PT142/143・Menu/HTTP/loggingを実行したことにしない。元八enum群/拒否不明対象の別経路・再演ではない。新slot/sessionは今回source/runのみ、旧成功を流用しない。

対象28methodと独立入力/期待/全境界/null/例外/並行・合成DOM・非該当再送は2069と原006/016/020の表を継承。新Test ID0。既28catalog/launcherを完全一致で再利用するが、変更後の新sourceに対し、一つの必要runで全15完全Main countersを測定する。旧65のexecとの合成/算術28+28加算0。役割や画面HTTP・exit依存を未照合のままWBS受入へ変換しない。

PG10458原工具の未使用import二/親pyflakes失敗guard不足はBUG1833/YKT1584へ是正前登録し、原工具と結果を保持。PG10459 V2は二unusedを除き、親がpyflakes終了0確認後に実行。同一plan e81eca37500886bd576802186dd95bf6126d53c6b600d485a11fc46f733a2a3e、五metadata反例（誤診断/二検査欠落/誤例外/旧assertion削除）を拒否。反例は製品PT件数へ加算しない。原10458二指摘は歴史として未抑制保持し、他旧工具unused三の未解決履歴も書換しない。

PG10460静的raw六/CS0/処理0/終了1（fe30b85e0e7c678bf7b7352c830bcf31218bf1506ccc9a0a53c5c10eaa2a72ec）。六は既三Test standalone executor/submitの文脈、抑制0。PG10462は新source六module正常compile/PT0、10464は原仕様・source/static/二追加assert・元14定数/全token/28case/15class・正確な依存を固定。10466を新sessionで一回実行し、10468が元XML/真正終端/session/CRC/15完全Main/全Main1843/選択外Test/禁止probe・classload0を独立照合する。

各manifestにtool/command/OS/JDK/時刻/source/dependency/input/actual/exit、公開XML/counter/path/hashを記録し、2072へ結果集約する。F/E/S/flaky/aborted/not-runを成功へ加えない。counter未達・branch非適用をそのまま記録し、coverage除外0/旧exec合成0。全451・F03・正式1964/53・個別17/190・工数null・QA051 final・安全HOLDは維持する。
