# Scenario検索画面状態単体テスト仕様書

2026-09-20正式17で8PT認定済。実行結果015/manifestを参照。以下の未実装表記は仕様先行履歴、現在は015の正式認定を正とする。

NK-WEB-001/ScenarioSearchViewModel.success/invalid/Filters/FieldError、FUN003/AUT/TST、UI222/223/234、SS313/323、PG200。未実装・未実行、正式認定へ未加算。

| Test ID | method | fixture・操作 | 独立期待 |
|---|---|---|---|
| PT-WEB-222 | web222SuccessfulSnapshot | 両role/game、speaker API順、6条件、literal結果 | closed scalar/候補順/結果順/TopBar一致 |
| PT-WEB-223 | web223PaginationUrls | 0件/1page/先頭/中間/最後/超過補正 | 固定/search、全6条件固定順、前後有無、literalpage一致 |
| PT-WEB-224 | web224QueryEncoding | 空/空白/+/&/=/quote/#/%/日本語/emoji | 手書きpercent encoded vector、query injectionなし |
| PT-WEB-225 | web225ResponseBindingAndBounds | 要求pageとeffective不一致、GAM10/11、SPK500/501 | 不一致/超過拒否、上限受入・並替えなし |
| PT-WEB-226 | web226InvalidFieldDisplay | 全8field/error4種、invalid factory/valid誤用 | 固定name/message、入力再表示、結果/URLなし、raw未知名非表示 |
| PT-WEB-227 | web227NullAndOwnership | factory全null/要素null/入力変更/返却変更 | null契約拒否、deep display snapshot不変 |
| PT-WEB-228 | web228ClosedBeansAndRedaction | bean一覧/field型/診断/合成HTML | context/DTO/formなし、固定REDACTED、HTML文字escape |
| PT-WEB-229 | web229ConcurrentSnapshots | 64別actor/filter/結果、8worker | cross-request混入なし、独立literal一致 |

期待値はCurrent search.htmlのquery名/順/表示値とUI/SS固定値を手書きし、Production URL/mapperで生成しない。正常・境界・異常・例外・null・並行を確認、再送/DB/JMSはこの不変投影の責務外で既存client/API PTに残す。新class/method/line/branch100%、NullAway/static・既存回帰成功後に015/manifestへcommand/commit/時刻/OS/JDK/tools/exit/input/expected/actual/coverage/関連BUG・SSC/hashを固定する。
