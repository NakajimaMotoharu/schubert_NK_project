# Menu固定catalog・内部model projection三Source 独立単体テスト仕様

群18110/3719・HEAD87c10fde3440437524a9871976cde4d7d60b5670/dev-foundation、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備。開始固定1/3/6pp cap10、開始前fresh83→直後84/rem16/reset1793774153の境目は共有区間で当群専有費不明。主F03/元ownerP01602参照費0。

正本UI221～223/226・SS313§4/6.2/7・314、NK-WEB001/FUN002/AUT001～003/SYS006/PG-D115・新PG-D1120。Current original template /home/mini/codex/project1/schubert_project/program/app/src/main/resources/templates/menu.html SHA9b45b5b83c14e945c6dd446889b020749bfdb87dd1f5f83d093a30d9bb074cd1を独立legacy oracleに読取のみ使用（コピー・baseline変更0）。元Current四title/説明/順・Log title/説明/path、追加cardのtitle/path/USER7ADMIN9はUI223/SS313を正とする。追加四説明の全文literalは上位に指定がないため、一行/空でない/質問・通知・回答・ユーザーという目的語だけを検証し、Production文字列からexpectedを生成しない。将来の実DOM/CHRの全文比較を今回の未測定から成功化しない。

MenuCard39行/MenuViewModel52/MenuController26、TopBar39/SessionPrincipal42・SSEconstructor・ProtocolContext/UserRoleの実calleeを確認（wcで照合し実行前draftの行数を訂正）。Controllerの直接methodは自己ExtendedModelMapへpageだけを設定し、Servlet/HTTP/security chain/server/DBを起動しない。SSEは固定ctorだけでgraph0。後続2070/2067は旧sourceの他view三TestでMenuの当source資格でない。元MenuMvcTest wholeはBeforeAll実DBのままHOLD・method/fixture抽出・改作0。

|Test ID suffix|入力/操作|独立期待値|
|---|---|---|
|MENU-PROJECTION001|全九catalog enum|getTitle/getHrefはUI固定九配列、legacy五説明はCurrent template literal、追加四説明は明示目的/単一行/非空|
|002|公開合成USER principal|UI first7順/閉list mutation拒否・brand schubert NK/PUBLIC_DISPLAY/USER・固定redaction|
|003|公開合成ADMIN principal|UI九順・末尾Log/User管理だけ追加・閉list/PUBLIC_DISPLAY/ADMIN|
|004|null principal/model、purefactory null|NPE invariant拒否・未設定model不変、NPE catch正常化0|
|005|GET annotation metadata/直接show・自己model既存marker/両role|mapping /、return menu、keyはretained/pageだけ・既marker同identity/表示値だけ・合成context非露出|
|006|foreign Principal|固定SSE/session storage is unavailable・cause null/suppressed0・model未設定|

plain SessionPrincipalはPUBLIC_DISPLAY/UserRole/固定Instant/公開合成a64だけ、SecurityContextへ設置/実session発行/認証grant無し。NFC/UTF8検査はhelper ctorで呼ぶ、crypto/UUID生成/clock read/IO/DB/JMS/HTTP/VM/Root/native/worker0、JDK/Spring内部初期化効果null。Modelは当Testのmapだけで外部caller資源解放なし。再送/並行の実HTTP隔離は元whole別HOLD、不変viewのlist非変更だけをこのunitで確認する。

六件/一suite/新一execで全三Source/三Code、全closure/normalJar/snapshot/現在source/CRC/単一session/XML/FESと全counterを測定。既TopBar自然B0資格は保持して新execへunion/置換0。分岐があるModel/Controllerは全条件、catalog自然0branchはN/A。手動除外/公式filter変更0、未測定・未達は未達のまま。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg18110_menu_projection_six_pt.py。normal14216/Spot14224を同Mainで再用、Java25.0.4/元command環境時刻branchHEAD・input/helper/Main/Test/class/exec/XML hash/exit/coverage/独立oracle/BUGを3461/manifestへ保存。新quality六は普通5786へ混同0・新製造0、正式1964/53/歴史17/190・新WBS受入0/工数null/QA051final/451/全HOLD維持、実画面HTTP/Browser/CHR成功0。
