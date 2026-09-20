# Log画面template単体テスト仕様書

現在状態: 正式PT-WEB-20260920-27/source3b980d71で本仕様8件を合格認定。次番号の実行結果/manifest参照。以下の未実装/未実行は仕様先行時の履歴。Log HTTP/Browser入力検査/実NKgateは未完了。

NK-WEB-002/SCR014、logs.html・fragments/log-pagination.html・css/schubert.css、FUN008/AUT002/MON003/UI222/225/235/DIF008・010/SS313/352/SSC073/PG216。仕様先行、未実装/未実行。LogSearchTemplateTestの8method。

| Test ID | method | 入力・操作 | 独立期待値 |
|---|---|---|---|
| PT-SCR-084 | log084LayoutAndFilters | ADMIN/全条件で実resolver | Logs/title/h1、共通menu/logout、7label・値/placeholder、type7・level4option順、datetime-local/step0.001 |
| PT-SCR-085 | log085RowsAndOptional | 全15field/空optional/新着2row | Current label順＋承認ID、UTC時刻literal/Status/Elapsed、空省略、details閉じる |
| PT-SCR-086 | log086Pagination | 0/1/100/101/201/過大page | 上下同じ条件URI/表示範囲、片側disabled、0件label/リンクなし |
| PT-SCR-087 | log087Escaping | username/filter/message/details/invalid enumへHTML記号 | text/attribute literal一致、任意tagなし、URL二重encodeなし |
| PT-SCR-088 | log088InvalidDisplay | 全field error/invalid enum/date | 固定順alert/入力保持、結果・count・pageなし、HTTP400維持 |
| PT-SCR-089 | log089CsrfAndClosedSurface | 公開synthetic CSRF/ADMIN | POST Logoutだけtoken、GET検索tokenなし、role/credential/context非漏えい |
| PT-SCR-090 | log090StylesAndResources | CSS実配信とCurrent Log選択子 | media type/固定CSS規則/mobile適用・本番JS未導入を明示 |
| PT-SCR-091 | log091ConcurrentRendering | 64入力/8worker同resolver | username/条件/row/CSRF混同なし |

期待値はCurrent templateとUIの固定文字列/DOM属性・page独立算術・固定percent URIで作成する。production rendererをexpected生成へ使用しない。null/USER/データ不整合はPG212/215で拒否済み、ここは有効閉modelのHTML境界、再送は副作用なし表示で非該当。実Spring Thymeleaf resolver/MockHttpServletRequest/Jsoup、Java25/Maven3.9.12、selected後clean verify。Java既存4coverage100%維持、templateは上記全条件のDOM assertionで分岐を検証（Java coverageをtemplate coverageと偽らない）。

020結果/manifestへ日時/OS・tool・branch・commit/command・exit/input/expected/actual/coverage/BUG・SSC/path・hashを記録。failed/flaky/skipped/not-run非合格。Browser byte事前検証/Controller/実認証HTTP/実Browser視覚/NKgate/PGPT/IT/STは未完了。
