# QA055 固定locked画面 単体仕様

Program NK-WEB-002 / WBS-P016-01、RD FUN-001、UI222/226/264、SS313/314§5.2/355、QA055/UIC012/SSC338・BUG2340/YKT2085。回答「現行の固定文を維持する」、正本main42450b515/PR207。期待文はinput040の承認UI原文・hashから独立literalとして定義し、Production methodでexpectedを計算しない。現在login.htmlは変更不要、DIF/Current baseline不変更。

対象 LockedLoginDisplayResourcePortTestの新4method、元LoginDisplayResourcePortTest8件/PG20560やController元4件は参照のみ、確認目的で再実行しない。Thymeleaf/SpringMock/Jsoupの明示CPにProduct Java jar無し。現在通常20990からlogin.htmlだけを抽出しhash一致を確認。GET用public flagと固定非credential markerだけ、auth/filter/POST/実session/DB/JMS/Browser/server/Root/VM/held4操作はない。SDK既純粋template8の同版を参照し、新Unitの初期化を個別照合する。

| Test ID | method | 入力・事前条件・操作 | 独立期待値 |
|---|---|---|---|
|PT-LOCK-DOM001|approvedLockedMessageDependsOnFlagPresenceNotItsValues|locked空/false/複数値の3レンダリング|承認固定文一件、error一件、password空、action/login|
|PT-LOCK-DOM002|independentErrorLockedLogoutFlagsKeepCurrentOrderAndFixedText|lockedとerror/logout有無の全4組|既error→固定locked→既logoutの順、各独立条件、script/イベント無し|
|PT-LOCK-DOM003|allegedRemainingSecondsAndCredentialsNeverBecomeDynamicDisplay|残秒風0/1/899/900/99999/不明markupの6、username/password風public marker|固定文一件、動的残秒/hidden/JavaScript/img/credential反映0、入力空|
|PT-LOCK-DOM004|parallelLockedAndUnlockedRenderingsKeepTheirOwnFlags|二worker8固有GET表示、locked有無交互|各固有条件の固定文/empty、混線0|

全21 derived HTMLはCREATE_NEWで保存し、hidden CSRFは保存前redact、raw request/token/session/実credentialを証拠へ入れない。四件のF/E/S/flaky/not-run/abort0、XML method集合/21HTML/入力Git/SDK init/通常resource byte/source/真正exit/独立postを照合。HTMLにJava line/method/class/branch counterを創作しない（Production Java CP無し/除外設定無し、javaCoverage=null）。API Retry-Afterの全境界/実controller・Browser・実NK CHR-A01/全451/個別leaf正式受入は別終了依存。

Command: 016/input039 prepare → static → source固定 → run <same frozen source> → post <same source> →独立post。実日時/OS/JDK/tool/branch/source/command/終了code/Input/expected/actual/静的結果/BUG/hashはmanifest・152結果へ記録。null/欠落はlocked無条件表示を避ける対照、空/false/多値・異常入力・並行を確認。SQL/transaction/再送の動作試験は当template-only範囲に非該当、既header再送の合格に読み替えない。
