# Animation合成テンプレートの例外型

NK-WEB-002、WBS-F03/2-2-b、SCR008/009、UI222/223/235、SS313/354、PT-SCR-046〜053。合成のメニュー、一覧、親子、25組／50本、0件、MB丸め、DOM/CSS、64並行の期待値は011仕様とPG14812の元XMLを用いる。待機、実行失敗、期限、合成結果のIOExceptionを宣言する。Spring Viewの汎用例外契約と既存期待値は変更しない。

PG42790-v2で上位包括型1件を確認し、BUG-3618を先に登録。PG42792（2026-11-23 JST、dev-foundation、対象コミット114537e5eb）はJDK25の隔離javac、3静的工具、選択JUnit一回で8件成功、失敗・エラー・skip 0。共通31とAnimation4の製品物理が既存のPG41502／PG41520と一致し、実行前後の4資源も一致。修正を逆変換して試験原文が完全一致した。SpotBugs rawは2→1、残るIM_BAD_CHECK_FOR_ODDは試験の非負固定域i=0..49内で影響なし。Checkstyle 0、PMD raw 5（有限スレッド4・finallyで終了確認するExecutor 1）。元XML、具体コマンド、開始終端値とハッシュは [PG42792 manifest](evidence/PG42792-animation-template-current-v1/manifest.json)。BUG-3618とYKT-2846の対象二fixtureを完了。Coverageの新規測定なし。実HTTP・六製品451・正式受入の条件は維持。
