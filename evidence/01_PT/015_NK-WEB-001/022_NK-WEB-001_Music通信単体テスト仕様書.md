# Music一覧通信単体テスト仕様書

NK-WEB-001/NK-MED-001/SCR011～013、MusicWireClient constructor/exchange、FUN007/AUT/MQ/TST、UI232/235§7～9/264、SS311/312/321/322/323/352、PG-D-210。仕様先行、未実装・未実行。MusicWireClientTestの8methodへ一意対応。

| Test ID | method | 入力・観点 | 独立期待値 |
|---|---|---|---|
| PT-WEB-254 | web254Requests | MCT/MCS/MTR、日本語category/section | 256header＋0/64/192dataのUI byte literal、一度だけ送信 |
| PT-WEB-255 | web255SuccessProfiles | 0000/0200、MCT0/1/20、MCS0/1/100、MTR0/1/200 | 8/8/16data、72/136/1312record、count/名称/各track field |
| PT-WEB-256 | web256ErrorProfiles | 10 error code、非zero data破損 | errorはpayloadなし、破損はINVALID_RESPONSE |
| PT-WEB-257 | web257MalformedReplies | 相関/context/layout/長さ/reserved/UTF8/count/role/pair/順序 | malformed拒否、未知結果正常化なし |
| PT-WEB-258 | web258CapabilitiesAndNull | 他layout/descriptor/record混入、null/timeout | MCT/MCS/MTR以外送信なし、境界契約維持 |
| PT-WEB-259 | web259TransportFailures | JMS/timeout/clock/ID/未知Error | 既知UNAVAILABLE、未知同一Error、pending解放 |
| PT-WEB-260 | web260ConcurrentRequests | 8worker/64要求、最大pending12 | actor/context/相関/layout隔離、残pending0 |
| PT-WEB-261 | web261OwnershipAndDiagnostics | M/I/N pair、caller配列変更、不変list、診断 | record snapshot、元応答非変更、送信buffer消去、固定redact |

Header offsetはUI232、recordはUI235から直接組立て、production encoderでexpectedを作らない。MTR pairは表示推論せずwire fieldを検証する。category/section名は日本語literal、0/上限・異常byte・null/欠落/未知・並行を含める。retryはreadでも追加しない1exchange方針。protocolの全64layout PTと共通engine既存PTも正式回帰へ含む。

Java25/Maven3.9.12。selected新8PT＋Animation/Scenario/JMS回帰後clean verify、line/method/class/branch100%、NullAway/Spotless/SpotBugs未解決0、failed/flaky/skipped/not-run不合格。023結果とmanifestへ日時/環境/対象commit/command/exit/input/expected/actual/coverage/関連BUG/SSC/path/hashを保存する。HTTP/track投影/配信/実broker/実NKgate・PGPT/IT/ST未完了。
