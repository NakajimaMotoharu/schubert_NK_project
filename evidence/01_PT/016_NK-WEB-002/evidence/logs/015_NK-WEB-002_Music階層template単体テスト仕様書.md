# Music category・section template単体テスト仕様書

NK-WEB-002/SCR011/012、music.html/music-sections.html/WebMvcConfiguration、FUN007/AUT/TST、UI222/223/235/264、SS313/352、PG209。仕様先行・未実装/未実行。MusicHierarchyTemplateTestの6methodを対応付ける。

| Test ID | method | fixture/操作 | 独立期待値 |
|---|---|---|---|
| PT-SCR-066 | music066CategoryMenu | USER/ADMIN、曲29/BGM99/その他1 | title/h1 Music、129曲、3card順・分類を選択する・固定URL、共通/業務nav |
| PT-SCR-067 | music067SectionMenu | category曲、3section10/15/4 | title/h1曲、29曲、ゲーム/アニメ/キャラクターソング・個別件数、固定URL |
| PT-SCR-068 | music068EmptyAndMaximum | category0/20、section0/100 | 空gridに追加文言なし、上限card/件数/先頭末尾URL一致 |
| PT-SCR-069 | music069EscapingAndCsrf | actor/category/sectionのHTML/特殊文字、公開合成CSRF | text逃避、strict URL非二重encode、POST Logout hidden1、secret/contextなし |
| PT-SCR-070 | music070CssAndViewBoundary | 実resolver2view/未知・traversal、共有CSS | 正規2viewのみ、Current由来menu4規則＋900px1列、script/inlineなし |
| PT-SCR-071 | music071ConcurrentRendering | 8worker/64identity・request-local context | actor/count/link/CSRF独立、公開trace、actualNkGate=false |

PG208の合成modelをfixtureとして使うが期待値はCurrent文言・URLliteral・UI235上限から独立に明示する。実Spring/Thymeleaf resolverを使用し、実Browser画像の合格とはしない。null/不変性はWEB246～253、HTTP/404/認証は後続controller試験、再送は副作用なし描画で非該当。共有CSSは既存ruleを照合し仕様を変更しない。

Java25/Maven3.9.12、selected新6＋PG2088・既存共通画面、その後clean verify。line/method/class/branch100%、NullAway/Spotless/SpotBugs、全template条件/反復を確認。failed/flaky/skipped/not-runは不合格。command/環境/commit/日時/exit/coverage/BUG/SSC/証跡path/hashは016とmanifestへ。raw HTML/context/session/CSRFはGitへ保存しない。HTTP/track/pair/player/実NKgate・PGPT/IT/STは未完了。
