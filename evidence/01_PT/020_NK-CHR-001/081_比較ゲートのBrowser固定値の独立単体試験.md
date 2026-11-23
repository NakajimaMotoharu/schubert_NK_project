# 比較ゲートのブラウザー固定値

NK-CHR-001、WBS-P020-01.03/2、UI264、SS355 §6／§11・12、TST-004、BUG-3730／YKT-2927。対象は `GateContractValidator.validateDefinitions` のブラウザー条件。

PT-CHR-DEF-019では許可済み公開定義6点を試験のメモリに読み、正本に固定された Playwright 1.55.0、Chromium 1187、ja-JP、Asia/Tokyo、desktop 1366×768、mobile 390×844、device scale 1を独立根拠とする。定義を同じ誤値に置換した比較で、文字四項目は各診断、両側での欠落も各診断、数値四条件は四診断。変更していない公開定義は診断0。過去の片側型違い、数値overflow、null、並行と合成全体も同候補で再確認した。

初回は1件が9独立assertionで失敗。修正後は定義21・数値3・合成全体6の計30件が成功。JDK25.0.4、JUnit1.13.4、JaCoCo 0.8.15、各実終了0。Checkstyleは確認済み二ファイルで0。新規固有IDは工具一件。固定した製品Core `98a8f53578cab17d9b67b1a16218179d39d4bc8f` の製品Java、承認済み画面・定義・Current原本は同一。

当変更3メソッドの生指標は行34・メソッド3・分岐24にすべて到達。全工具クラスでは行10・メソッド2・分岐66が未到達。実ブラウザー、実Current/NK、製品PT、全451、正式受入は別。 [元失敗](evidence/PG43726-pinned-browser-before/manifest.json) [再試験](evidence/PG43726-current-pinned-browser-definition/manifest.json)
