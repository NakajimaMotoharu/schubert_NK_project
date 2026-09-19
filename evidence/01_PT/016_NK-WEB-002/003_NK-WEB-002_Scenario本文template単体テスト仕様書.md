# Scenario本文template単体テスト仕様書

NK-WEB-002/SCR007、scenario.html、schubert.cssのScenario規則、WebMvcConfiguration view allowlist。FUN004/PER002～004/TST001～005/AUT001～003、UI222/223§4.2/234、SS313§6～10/333、PG196。入力は検証済ScenarioDetailViewModel。detail controller/実MQ/file reader/本番bootstrapの完成ではない。

| Test ID | method | 入力/操作/fixture | 独立期待 |
|---|---|---|---|
| PT-SCR-017 | detail017HeaderAndCommonLayout | 両game/USER・ADMIN、実template render | title/h1/subtitle、メニュー・一覧・検索・通知、username/role、POST Logout＋hidden CSRF、UTF-8 |
| PT-SCR-018 | detail018PreviousNext | 前後有無4組、正規数値ID | 上下2navの同じ前/次label・URL、欠落は前: なし/次: なしで非link |
| PT-SCR-019 | detail019EntriesAndVoices | 3entry/0・1・2audio、非連続ID | article順/entry anchor、line/speaker有無、dialogue/narration、本文1回・全audio controls/preload none・DL URL |
| PT-SCR-020 | detail020EmptyScenario | inline0entry | Currentどおり空本文領域、article/audio/追加空文言なし、前後nav保持 |
| PT-SCR-021 | detail021HtmlAndUrlSafety | title/本文/speaker/path/usernameにHTML文字 | th:text literal保持、script/inline event/style/data属性なし、context/descriptor非露出、全href/srcは固定same-origin |
| PT-SCR-022 | detail022MaximumRecordsAndVoices | file10000entry、同entry999audio | 全件保持、本文重複なし・最後まで順序保持、silent truncateなし |
| PT-SCR-023 | detail023CssAndViewBoundary | Current由来CSS規則、resolver登録/unknown | 全新宣言値・900px/target highlightを独立literal照合、scenario解決・unknown/redirect拒否 |
| PT-SCR-024 | detail024ConcurrentRendering | 64独立本文/actor/CSRFで共通resolver | 全DOM値一致・他request値の混入なし |

期待値はCurrent scenario.html/styles.cssとUIの明示literalから作成し、Production templateのparse結果をexpected生成へ使わない。共通UI以外の表示変更をしない。新CSSは全新規rule/declarationを照合し、templateのif/each/三項両側を空/単/複数/最大とrole・前後・speaker有無で実行する。Java4coverageを下げずNullAway/SpotBugs・既存階層16/Menu/Error回帰を行う。秘密値は合成fixtureだけ、raw CSRF/session/contextを保存しない。選択8PT成功・正式全回帰待ち、004/manifestへcommand/時刻/OS/JDK/対象commit/結果/coverage/関連BUG/hashを確定後記録する。
