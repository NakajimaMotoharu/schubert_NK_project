# NK-WEB-002 SCR-001 Login画面単体テスト仕様書

PG219、QA-045/UIC-005/SSC-074、RD FUN-001/SYS-001/AUT-001/TST-001～005、UI222/226/264、SS313/314/355、CHR-A01。対象は`LoginController.login`、`login.html`、`WebMvcConfiguration`の閉view登録。POST `/login`の認証処理は既存filterと後続実NK結線の別対象であり、画面GETだけでLogin機能完了とはしない。

| Test ID | 目的・事前条件/fixture・操作 | Productionから独立した期待値 |
|---|---|---|
| PT-SCR-105 | Spring MVCと実resolverで匿名GET `/login`。CSRF属性あり、DB/MQ接続なし | HTTP200、view `login`、`lang=ja`、title `schubert NK - ログイン`、可視h1 `schubert NK`。Current baseline `schubert - ログイン`との差だけDIF-001/CHR-A01。form method POST/action `/login`、hidden `_csrf`が1件で入力fixture値と一致 |
| PT-SCR-106 | 同じ実templateの入力DOMを検査 | Username `autocomplete=username`/autofocus/required、Password `autocomplete=current-password`/required/値空、label対応、button `ログイン`。password/context/cookieをHTMLへ埋め込まない |
| PT-SCR-107 | `?error`、`?locked`、`?logout`、通常/未知queryを個別描画 | Current Loginの3文言だけを各条件で表示し、条件外のmessageは0。Passwordはすべて空。lock待機15分。未知queryは認証成功や任意HTML注入へ変換しない |
| PT-SCR-108 | 閉resolverとGET controllerを検査 | `login`のみview解決、未知view・fragment・任意redirect/forwardは引き続き拒否。POSTはControllerで扱わず既存security chainが所有 |

JaCoCoの新Production classを含むJava line/method/class/branch各100%、NullAway/SpotBugs/format0、全関連Web/PTの失敗・skip0。試験実行command、OS/JDK/branch/source、終了code、独立DOM期待値、coverage、関連BUG/SSC、evidence path/hashは正式runの同一source manifestへ記録する。実Browser HTTPS・Production起動・実NK CHR-A01/L01とCurrent差分比較は別未完了条件。Current baselineは書き換えない。
