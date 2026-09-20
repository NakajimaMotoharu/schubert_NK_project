# Log検索入力単体テスト仕様書

現在状態: 正式PT-WEB-20260920-26/source7df9eb2eで本仕様8件を合格認定、対応する次番号の実行結果/manifest参照。以下の「未実装/未実行」は仕様先行時の履歴。Log全画面/HTTP/NKgateの完了ではない。

NK-WEB-001/SCR014、LogSearchForm.bind/toRequest/invalidCharacters/date/optional、FUN008/AUT/MON/TST、UI222/225/235/DIF010、SS313/352/SSC073、PG-D-214。仕様先行・未実装/未実行。LogSearchFormTestの8methodへ対応。

| Test ID | method | 入力・操作 | 独立期待値 |
|---|---|---|---|
| PT-WEB-278 | web278DefaultsAndFilters | missing/空・全field・全enum | 空Optional/page1/size100、NFC/ASCII trim、固定wire値 |
| PT-WEB-279 | web279TextAndBinding | q256/action64/path256、Unicode境界、未知/重複/空List | 超過拒否、切捨てなし、固定BINDING/LENGTH |
| PT-WEB-280 | web280Characters | CR/LF/TAB/NUL/孤立surrogate/正しいpair | trimでcontrolを消さず拒否、valid supplementary受理 |
| PT-WEB-281 | web281PageAndEnums | 負int/0/1/999999/overflow/plus/小数/未知enum | UI222補正、その他VALUE、invalid toRequest拒否 |
| PT-WEB-282 | web282Dates | yyyy-MM-ddTHH:mm[:ss[.S..SSS]]/年・閏日・JST変換 | 独立UTC Instant、0000/無効日・24時・offset・4桁小数拒否 |
| PT-WEB-283 | web283DateRange | 片側/同時刻/31日/31日+1ms/逆転 | 両側有効時だけRANGE、境界含む・丸めなし |
| PT-WEB-284 | web284NullOwnershipAndRedaction | null map/key/list/要素、元map/list変更、返却map | null契約、不変snapshot/診断固定、raw入力非反射 |
| PT-WEB-285 | web285ConcurrentBinding | 64入力/8worker、共有元fixture | 検索/日時/page独立、元入力不変 |

日付期待は固定UTC literal、byte境界はASCII/日本語/補助文字の既知幅、page補正はCurrent Math.maxの仕様から独立算術。production toRequestでexpectedを作らない。正常/境界/異常/例外/null/並行を実行し、再送は副作用なし入力投影で非該当。NPE catch正常化なし、NullAwayとconstructor invariantも確認。

Java25/Maven3.9.12、selected新8＋既存Scenario入力8後clean verify、line/method/class/branch100%、静的解析未解決0、failed/flaky/skipped/not-run非合格。029結果/manifestへ日時/環境/対象commit/command/exit/coverage/BUG/SSC/path/hashを保存。Controller/実template/HTTP/実NKgate・PGPT/IT/ST未完了。
