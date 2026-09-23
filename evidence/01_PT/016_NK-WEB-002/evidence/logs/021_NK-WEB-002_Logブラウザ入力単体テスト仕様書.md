# Logブラウザ入力単体テスト仕様書

Program NK-WEB-002 / SCR-014。対象 `static/js/log-search-validation.js`、`logs.html`、`LogSearchScriptTest` / Node DOM fixture。関連RD FUN-008/AUT-002/TST-001、UI222/225/235、SS313/352、SSC-073、PG-D-217。2026-09-23仕様先行。結果・coverage・commitは未実行につき未認定。対応結果は022、正式証跡は本Programの`evidence/manifest.json`。

| Test ID | 入力・操作 / fixture | 独立期待値と根拠 |
|---|---|---|
| PT-SCR-092-A | Log form不存在 | 例外・登録・送信なし。DOM不存在の閉境界 |
| PT-SCR-092-B | q/action/pathの一つが欠落 | 固定構造異常として例外。SS313の3文字列field |
| PT-SCR-092-C | ASCII各上限±1 | q/path256、action64 byte。UI225の数値から独立計数 |
| PT-SCR-092-D | NFC結合文字・補助文字・孤立surrogate・CR/LF/TAB/NUL | Java bindと同順のNFC/ASCII trim後byte。危険文字をtrimで消さず拒否。UTF-8固定幅vector |
| PT-SCR-092-E | 不正q/action/pathを同時submit | field別customValidity、submit抑止・reportValidity1、HTTP未送信 |
| PT-SCR-092-F | 修正後input→submit | errorを消し、native GET送信1。入力値を書き換えない |
| PT-SCR-092-G | 文字列がちょうど上限、日本語境界 | 3byte/4byte独立計数。切捨てなし |
| PT-SCR-092-H | Node24.19.0実script構文・coverage | 実source inventory1/1、line/function/branch100%、failed/skipped/todo0。fixtureは独立したDOM event double |

`LogSearchScriptTest#log092BrowserInputScript`の1 JUnit内にNode subcaseを内包し、JUnit件数へ二重加算しない。JavaScriptなしでも`LogSearchForm`がserver-side validationを実行する。SQL/JMS/sessionの再送は副作用なし入力補助へ非該当。null DOM/欠落/空/未知・Unicode・境界/例外を上表で確認する。Node scriptのexpectedはProduction JSを呼び出して生成しない。実行commandはNode `--check`＋`--test --experimental-test-coverage`（実script限定・3指標100%）をJUnitから実行し、正式認定時は451のroot `clean verify`。branch/commit、OS/JDK/Node、終了code、input/expected/actual、coverage、関連BUG/SSC、証跡path/hashは結果とmanifestへ記載する。未実行・失敗・flaky・skipは合格に算入しない。実Browser/実NK CHRは別判定。
