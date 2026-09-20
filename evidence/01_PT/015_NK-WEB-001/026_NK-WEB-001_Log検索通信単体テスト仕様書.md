# Log検索通信単体テスト仕様書

NK-WEB-001/NK-ADM-001/SCR014、LogSearchWireClient constructor/exchange、FUN008/AUT002/MON/MQ/TST、UI232/234§2/235§11/264、SS311/312/321/323/352、PG-D-213。仕様先行・未実装/未実行。LogSearchWireClientTestの8methodを対応付ける。管理Log APIは431の既存NK-ADM-001に属し、新Programを増設しない。

| Test ID | method | 観点・入力 | 独立期待値 |
|---|---|---|---|
| PT-WEB-270 | web270Requests | 空/全filter、全6type×3level、31日境界 | 256＋656byte、各UI235 offset/space/数値/JST literal |
| PT-WEB-271 | web271SuccessProfiles | 0000/0200、0/1/100 records、optional有無 | PAGED48算術、2088byte各fieldの閉typed値 |
| PT-WEB-272 | web272ErrorProfiles | 全10errorとerror data破損 | payloadなし、破損拒否、0103を成功へ変換しない |
| PT-WEB-273 | web273MalformedReplies | 相関/context/layout/length/reserved/UTF8/enum/page破損 | INVALID_RESPONSE、pending0/buffer消去 |
| PT-WEB-274 | web274CapabilitiesAndNull | ANM/MCT/WLGEVT混入、null、0/過長wait、page/date不正 | LGSのみ送信、null契約、invalid noMQ |
| PT-WEB-275 | web275TransportFailures | JMS/timeout/clock/ID/未知Error | 既知UNAVAILABLE、未知同一性、再送なし |
| PT-WEB-276 | web276ConcurrentRequests | 8worker/64要求、actor別context | 相関64一意・context/response独立、pending0 |
| PT-WEB-277 | web277OwnershipAndDiagnostics | caller応答配列/不変record/全diagnostic | copy所有、caller非変更、固定redact、suppressed禁止 |

HeaderはUI232、data/recordはUI234/235から手書きvector、production encoderでexpectedを作らない。0/1/100の正常・境界、全error/壊れた入力・null・並行・timeoutを確認。Role認可はcontroller/security chain/APIの責務であり、このfacadeの存在をADMIN検証完了としない。HTTP query/log値を保存しない。

Java25/Maven3.9.12、selected8PT＋既存read facade/JMS回帰→clean verify、4coverage100%、NullAway/Spotless/SpotBugs未解決0、failed/flaky/skipped/not-run除外。027結果とmanifestへ日時/環境/対象commit/command/exit/input/期待/実際/coverage/関連BUG/SSC/path/hashを保存。HTTP/form/template/実broker/実NKgate・PGPT/IT/ST未完了。
