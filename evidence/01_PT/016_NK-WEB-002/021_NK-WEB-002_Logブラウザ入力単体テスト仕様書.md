# Logブラウザ入力単体テスト仕様書

Program NK-WEB-002 / SCR-014。対象 `static/js/log-search-validation.js`、`logs.html`、`LogSearchScriptTest` / Node DOM fixture。関連RD FUN-008/AUT-002/TST-001、UI222/225/235、SS313/352、SSC-073、PG-D-217。2026-09-23仕様先行。初回結果は022、従来の正式証跡は本Programの`evidence/manifest.json`。現行のNode A～Hは下表どおり。親JUnitの識別子はPT-SCR-092、TAPに載る各subcaseはPT-SCR092-A～H。

| Test ID | 入力・操作 / fixture | 独立期待値と根拠 |
|---|---|---|
| PT-SCR092-A | Log form不存在 | 例外・登録・送信なし。DOM不存在の閉境界 |
| PT-SCR092-B | q/action/pathの一つが欠落 | 固定構造異常として例外。SS313の3文字列field |
| PT-SCR092-C | ASCII各上限±1 | q/path256、action64 byte。UI225の数値から独立計数 |
| PT-SCR092-D | 孤立surrogate・CR/LF/TAB/NUL | 禁止文字の固定エラーを返して原入力を保持する |
| PT-SCR092-E | NFC結合文字・前後ASCII space・NBSP・先頭U+FEFF | NFC・ASCII trim後のUTF-8境界を独立計数し、画面の原入力を保持する。U+FEFFは3 byteの入力値 |
| PT-SCR092-F | 不正q/action/pathを同時submit | field別customValidity、submit抑止・reportValidity1、送信回数0 |
| PT-SCR092-G | 補助文字・日本語のUTF-8上限と超過 | 3 byte／4 byteで独立計数し、超過時は固定長エラー |
| PT-SCR092-H | 修正後input→submit | errorを解除し、DOM fixtureの送信回数1、原入力を保持する |

PT-SCR-092でNodeの構文検査と実scriptのline/function/branch 100%を確認する。八subcaseのfailed、skipped、todoをそれぞれ0とし、coverageの対象ファイルは一つ。 [現候補の実行証跡](../018_NK-OPS-001/evidence/PG43616-scr014-leading-bom-literal-contract/manifest.json)

`LogSearchScriptTest#log092BrowserInputScript`の1 JUnit内にNode subcaseを内包し、JUnit件数へ二重加算しない。JavaScriptなしでも`LogSearchForm`がserver-side validationを実行する。SQL/JMS/sessionの再送は副作用なし入力補助へ非該当。null DOM/欠落/空/未知・Unicode・境界/例外を上表で確認する。Node scriptのexpectedはProduction JSを呼び出して生成しない。実行commandはNode `--check`＋`--test --experimental-test-coverage`（実script限定・3指標100%）をJUnitから実行し、正式認定時は451のroot `clean verify`。branch/commit、OS/JDK/Node、終了code、input/expected/actual、coverage、関連BUG/SSC、証跡path/hashは結果とmanifestへ記載する。未実行・失敗・flaky・skipは合格に算入しない。実Browser/実NK CHRは別判定。
