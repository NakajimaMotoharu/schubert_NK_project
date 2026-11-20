# Webログcodec 鍵構築所有の実行結果

対象source `5c879b5b77b9feedf6c39f93c813519dc151ead5`。WBS-P018-10.03、PT-WEB-WEBLOG-OWN002、BUG-3483、YKT-2779。

PG41348は旧classのconstructorで最初の鍵cloneが全設定検証より早く、保護範囲がないと確認した。変更後は入力を全て検証してからcopyする。二つめの取得がErrorで終わった場合のbytecodeには先に取得したcopyの消去と同一Errorの伝播がある。借用入力は書き換えない。

PG41350は既10件と新しい構築境界試験1件の全11件を同一sourceで実行し、失敗・エラー・skip・未実行0。PG41352は元exec一つをCRCで照合。対象constructorは分岐14/14、Error処理3行は未到達。対象クラスは分岐52/52、行140/143、命令570/583。CheckstyleとSpotBugsは指摘0。PMDの汎用Error捕捉1件は判定を保留し、抑制設定は追加していない。構造上の確認と動的未到達を区別し、451は未成立とする。

[元構造](evidence/PG41348-p01810-web-log-constructor-ownership-v1/manifest.json) · [通常11件](evidence/PG41350-p01810-web-log-constructor-qualified-v1/manifest.json) · [独立結果](evidence/PG41352-p01810-web-log-constructor-independent-v1/manifest.json)
