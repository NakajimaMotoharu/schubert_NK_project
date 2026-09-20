# Music分類・区分HTTP単体テスト仕様書

NK-WEB-002/SCR011/012、MusicController.categories/sections/exchange/actor、MusicMvcConfiguration、FUN007/AUT/TST、UI221～223/232/235/264、SS311～314/323/352、PG-D-211。仕様先行・未実装/未実行。MusicControllerTestの以下12methodへ対応。

| Test ID | method | 目的・入力・操作 | 独立期待値 |
|---|---|---|---|
| PT-SCR-072 | music072SuccessAndWire | USER/ADMIN、0000/0200、MCT/MCS | GET2path、256/320byte要求、閉page・件数・順序 |
| PT-SCR-073 | music073ErrorMapping | 9error code×2path | 400/401/403/404/409/429/409/503/503、modelなし |
| PT-SCR-074 | music074SessionInvalid | 0102×2path、隔離DB/session | redirect Login・session削除・cookie失効・後続処理なし |
| PT-SCR-075 | music075MalformedAndTransport | 不正header/応答相関/transport | 503、modelなし、pending/buffer解放 |
| PT-SCR-076 | music076ResponseBinding | 重複category/section、dot等の不正リンク | 503、閉model作成範囲だけcatch |
| PT-SCR-077 | music077NullAndUnknown | null/foreign actor、未知model/HTTP/Error | null契約/未知例外同一性を保持 |
| PT-SCR-078 | music078MvcRoutesAndInput | GET/HEAD/POST/未知path、category64byte/NFC/control/space/不正Unicode | 正規化後MCS、invalid400送信なし、POST405/未知404 |
| PT-SCR-079 | music079RealHttpSecurity | 実Tomcat、未認証/両role/HEAD/0102 | Login redirect、no-store/nosniff/CSP、Logout CSRF、HEAD本文0 |
| PT-SCR-080 | music080EscapingAndIsolation | HTML文字・日本語category/section | th:textと固定percent URL、wire/contextなし |
| PT-SCR-081 | music081EmptyAndMaximum | MCT0/20、MCS0/100 | root空200・空category404、上限順/件数 |
| PT-SCR-082 | music082ConcurrentRequests | 64要求/8worker、actor別context | request-local identity、重複相関0、pending0 |
| PT-SCR-083 | music083CompatibilityTrace | 公開合成2画面/2route | title/card/nav順・件数・独立公開trace |

Fixtureは隔離PostgreSQL、JMS reply doubleとUI232/235手書きbyte、実Thymeleaf/MockMvc/loopback Tomcat。Production encoderや同一表示factoryでexpectedを生成しない。正常/境界/異常/null/例外/並行、send-onceとno-MQ invalidを確認。categoryはNFC/strict UTF8・64byte・CR/LF/TAB/NUL・末尾ASCII spaceをwire共通規則で検査し、trimしない。Currentの区分0件404を維持する。

Java25/Maven3.9.12、selected12PT＋Musicwire/model/template回帰後clean verify。line/method/class/branch100%、NullAway/Spotless/SpotBugs未解決0、failed/flaky/skipped/not-runは不合格。018実行結果とmanifestへ日時/環境/対象commit/command/exit/coverage/BUG/SSC/path/hashを保存。track/pair・stream/実broker/本番bootstrap/logging/実NKgate・PGPT/IT/STは未完了。
