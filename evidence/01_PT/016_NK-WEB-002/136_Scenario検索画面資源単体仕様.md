# Scenario検索画面資源 限定単体仕様

Program NK-WEB-002 / SearchTemplateResourcePortTest、WBS-P016-03。関連RD FUN-003、UI222/223 SCR003・234、SS313/323。Production検索ViewModelは既whole証拠があるため再演せず、search.html/layout.html/pagination.htmlの現資源だけを検証する。既ScenarioSearchTemplateTestは実MVC/session/DB依存を含むため呼び出さず分割もしない。これは新しい独立fixtureの通常PTであり、HOLD対象の代替実行ではない。

前提: normal PG20586（製品資源70fb、Main D8全Java byte一致）の実webJAR・抽出資源・repoが一致、外部通信無し、OS Linux/JDK25.0.4。Thymeleaf/JsoupとServlet mockのみ。Main Java、鍵、実token、認証、CSRF生成・照合、DB/VM/Root/native/CHR/JSを起動しない。固定_csrf代替値は保存前にredactし、全DOM不在をpost確認する。入力は独立map、expectedは承認文言/経路/100件算術の固定literal、production methodでexpectedを作らない。

| Test ID | method | 入力・操作/独立期待値 | 派生DOM |
|---|---|---|---:|
|PT-SEARCH-DOM001|unsearchedPageRetainsSixGetControlsWithoutInventedResults|results Optional.empty、空6条件/候補順NUKITASHI2→1・乙→甲。GET /search、検索title、USER、未検索count/result/nav無し、script参照のみ|1|
|PT-SEARCH-DOM002|successfulEmptyPageShowsZeroCountAndNoPagination|total0/page1/rows空。0 results、該当無し、player/nav無し|1|
|PT-SEARCH-DOM003|bothPaginationCopiesRespectSingleFirstMiddleAndLastBoundaries|total/page=(1,1),(201,1),(201,2),(201,3)。範囲1-1/1,1-100/201,101-200/201,201-201/201、上下同値、前後リンクa/span・page±1固定|4|
|PT-SEARCH-DOM004|allKnownAndUnknownEnumFiltersRedisplayWithExplicitSelection|entry空/dialogue/narration/未知、voice空/with/without/未知、選択各1。ADMIN表示、入力本文/章、未知値HTML escape・選択保持|4|
|PT-SEARCH-DOM005|rowMetadataAndAudioPresenceDoNotCreateEmptyPlayers|chapter/speaker/audio有と空/無。表示順、script/line、scenariohref、player controls/preload none・DL経路、空player無し|2|
|PT-SEARCH-DOM006|errorsInputAndMultilineBodyEscapeWithoutExecutableMarkup|固定script風文字/newline/&をinput/body/errorに設定、DOM text完全一致、error表示、inline executable要素無し、固定戻り先|1|
|PT-SEARCH-DOM007|fullHundredRowPageKeepsEveryStoredPositionAndBoundaryBody|100rows、先頭first/末尾last/中間row-n。全100位置・count100・単page前後無し|1|
|PT-SEARCH-DOM008|ownedConcurrentRenderersNeverShareFiltersOrRows|自己所有2worker/8map、10秒join、各input/body一致、終了TWR。共有render状態の混線無し|8|

全8method/22派生DOM。Optional欠落・空collection・未知値・空文字・0/1/100/201件・page端・並行を上記に含む。Java null契約/全MVC/入力validation自体/実HTTP/順序SQLは別programの責務、ここで合格にしない。HTMLにJava四counterは存在せずnull、除外で100%へ補完しない。全HTML分岐に対して上表のtrue/false入力を明記し、全工程coverage100とは区別する。

実行command: `env PYTHONPATH=tools/quality python3 -B evidence/01_PT/016_NK-WEB-002/input/019_search_resource_qualifier.py prepare|static|run <frozenHEAD>|post <sameHEAD>`。prepare/staticは固定済み入力、実Product Unitは新規一回だけ。XML全method名・F/E/S/aborted0・22DOM・source/resource/dependency/normalJAR/inputHash・実終了codeをstrictpostで結合する。原prepare説明の複製残留BUG2345/YKT2090は原20604を保持し当工具metadataだけ是正、旧成功PT流用0。結果137/公開PG20620 manifestへ終了時記載。全451/正式認定1964-53/QA055/工数null保持。
