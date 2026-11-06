# Scenario本文画面資源 限定単体仕様

NK-WEB-002/SCR007、ScenarioDetailTemplateResourcePortTest、WBS-P016-07。RD FUN-004、UI221/222/223/234、SS313/333。actual scenario.html/layout.htmlをnormal20586/資源70fbのwebJAR・repo・抽出で同byte照合する。Main Java不変更。既ViewModel等のwhole測定、JMS/QA054既済証拠は再演せず、PG20670に候補除外の根拠を保持する。

入力は独立map/順序固定list、期待はUIの明示literal/ID/リスト位置で定義しProduction methodで生成しない。権限を持つsessionやAPI、実scenario/media/原本fileを取得しない。Thymeleaf/Jsoup/Servlet mockと自己所有2workerだけ、Product Java初期化0。表示用_csrfは保存前redactし全23DOM不在をpost。本文/script風文字は非機密fixtureで実行せず、リンク/player属性の表示確認のみ。

| Test ID | method | 入力・独立期待値/観点 | DOM数 |
|---|---|---|---:|
|PT-SCENE-DOM001|metadataAndNavigationUseExplicitApprovedDisplayValues|title/brand/game/path/USER/固定nav、entry-9/line9/speakerを明示。正本SCR007 routeは /scenarios/{id}|1|
|PT-SCENE-DOM002|emptyEntryCollectionHasNoInventedBodyOrAudio|entries空、body section有・article/audio/DL無し、上下nav二つ|1|
|PT-SCENE-DOM003|everyPreviousNextCombinationMatchesBothNavigationCopies|previous/next Optional有無の四組、上下同値、a/span・前/次なし・正本plural経路16/18|4|
|PT-SCENE-DOM004|dialogueAndSpeakerFlagsRemainIndependentInAllFourCases|dialogue/narration×speaker空/有四組、classとmeta span1/2、行番号保持|4|
|PT-SCENE-DOM005|zeroOneAndTwoAudioLinksKeepStoredPlayerAndDownloadOrder|音声0/1/2、controls/preload none・/audio/71,72・DLと表示pathをlist固定順で照合|3|
|PT-SCENE-DOM006|titlesSpeakerAndMultilineBodyEscapeMarkupWithoutTextLoss|script風文字/&/改行/日本語/éをtitle/speaker/bodyへ。DOM wholeText完全一致・script要素無し|1|
|PT-SCENE-DOM007|hundredEntriesKeepEveryAnchorPositionAndLongFirstBody|100article、全anchor entry-1..100、先頭4096byte本文非切捨て、末尾line-100、player無し|1|
|PT-SCENE-DOM008|ownedConcurrentPagesKeepTheirBodiesAndTitlesIsolated|2worker/8独立map、10秒join/TWR、各title/bodyが混線しない|8|

合計8method/23DOM。Optional欠落/空/境界0-1-2音声・100行・4096本文・不正表示文字/並行は上記。view nullやfile/descriptorの業務invariantは別責務、ここで保証しない。Java四counterはHTML資源に無くnull、coverage100%を補完しない。HTTP/MVC/実Browser/Range/認可/token/HMAC/CSRF/実file/large-result reader/DB/Root/VM/native/JS/CHR/451は未受入。

command: `env PYTHONPATH=tools/quality python3 -B evidence/01_PT/016_NK-WEB-002/input/025_scenario_detail_resource_qualifier.py prepare|static|run <frozenHEAD>|post <sameHEAD>`、input026に依存hash、Linux/Java25.0.4。source固定後Unit新規一回、XML全8method/FESaborted0/23DOM・input-resource-normalJAR/tool/command/time/hashをstrictpost結合する。結果143/PG20678公開manifestへ記録。

同じScenario遷移経路の必要内部依存としてBUG2349/YKT2094の旧検索fixture二literalを正本pluralに是正し、input027/PG20684の必要8/22DOM回帰を併行準備する。新Scene8と再試験Search8を別run/source証拠で記録、旧Search8と再試験8は同TestIDなので一度だけ数える。原PG20620・元group4028/29・原1/3/6cap8を保持し、追加発見/手戻り見積0.25/0.75/2ppを別記、追加予算や正式完成率へ転用しない。
