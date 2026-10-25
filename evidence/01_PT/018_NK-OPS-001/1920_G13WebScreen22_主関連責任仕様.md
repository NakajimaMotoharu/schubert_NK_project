# G13.07・Web画面/form/view複合22 sourceの主関連責任

2026-10-25 15:07 JST、G13_WEB_SCREEN22_SOURCE_V1/source64446不変更、開始.5/2/6pp/cap10。fresh67残33/reset1793382075（06:07:03UTC）。現在窓残10以下/取得不能で保全、旧累計80/90停止なし。

sourceは`src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/`以下。原485の共有controller担当を維持し、menu/list/detailの複数画面を試験することを理由にMain担当を再配賦しない。AnimationControllerはP01610、MusicControllerはP01613、ScenarioController/ContentDetailControllerはP01607、NotificationControllerはP01621、MediaControllerはP00905。関連する各画面/DTO/security/transportの全既知担当は残す。複合view familyは明示したroot view modelをprimary候補とし、関連list/section/fileなどを消さない。

|source|primary/cost|実Main又はprimary view artifact根拠|
|---|---|---|
|form/TargetOperationFormTest.java|WBS-P015-07|共通TargetOperationInput、UI224/236/TARGET、detail P01621/23関連|
|form/UserMutationFormTest.java|WBS-P016-17|UserMutationInput、USER CHANGE、UI225/236|
|session/AnimationControllerTest.java|WBS-P016-10|実AnimationController、関連menu08/list09保持|
|session/ContentDetailControllerTest.java|WBS-P016-07|実ContentDetailController、関連animation10/music13保持|
|session/LogControllerTest.java|WBS-P016-14|LogController、SCR014/UI225|
|session/MediaControllerTest.java|WBS-P009-05|実MediaController、Range04/descriptor関連保持|
|session/MenuMvcTest.java|WBS-P016-02|MenuController、WEB142..147|
|session/MusicControllerTest.java|WBS-P016-13|実MusicController、関連category11/section12保持|
|session/NotificationControllerTest.java|WBS-P016-21|実NotificationController、関連list20保持|
|session/QuestionControllerTest.java|WBS-P016-18|QuestionController、関連accepted19/list22/detail23保持|
|session/ScenarioControllerTest.java|WBS-P016-07|実ScenarioController、関連game04/route05/file06保持|
|session/ScenarioSearchControllerTest.java|WBS-P016-07|同共有ScenarioController、検索03関連を保持|
|session/UserAdminControllerTest.java|WBS-P016-17|実UserAdminController、一覧15関連|
|session/UserBusinessControllerTest.java|WBS-P016-17|同共有UserAdminController、create16/業務P010関連保持|
|view/AnimationTemplateTest.java|WBS-P016-08|animation.html/menu root model、list09関連|
|view/AnimationViewModelTest.java|WBS-P016-08|AnimationMenuViewModel root、AnimationList09関連|
|view/LogSearchTemplateTest.java|WBS-P016-14|logs.html/LogSearchViewModel|
|view/MusicHierarchyTemplateTest.java|WBS-P016-11|music.html/category root、section12関連|
|view/MusicHierarchyViewModelTest.java|WBS-P016-11|MusicCategoryViewModel root、section12関連|
|view/ScenarioDetailTemplateTest.java|WBS-P016-07|scenario.html/ScenarioDetailViewModel|
|view/ScenarioHierarchyViewModelTest.java|WBS-P016-04|GameListViewModel root、route05/file06関連|
|view/ScenarioSearchTemplateTest.java|WBS-P016-03|search.html/ScenarioSearchViewModel|

元9386v3 graph/現9450 register、原941 Main/resource担当、原Program PT/SSをcurrent-normal snapshot/hash/JDK宣言/CPと静的照合し、上表を独立parseしたexpectedと確認する。複数関係を多数決/画面順で縮めず、明示primaryと関連/runtime不確定を分離。TestのHTTP/DOM expected自体をproduction renderer/codecで再生成せず、旧PT/oracle/Current baselineを変更しない。

実Browser/HTTP/Servlet/DB/broker/credential/native/child/Root/JUnit/target compile-loadの実行0、旧成功PTの確認再演0。5 fullpath選択vector、明示Web→APIの反例、cost一field/関連/不確定/owner/byte/source/status/欠落重複/近傍/旧logical優先を反証。旧785の全canonical/関連/runtime/artifact witnessを保持。見込1610→1632/1789/Test645→667/824・残179→157・限定785→807だが独立検証後だけ計上する。

file責任の補完を全method/要求/oracle/TestID/終了依存や実行PT/coverage/正式受入へ変換しない。元941943/481484/予算/受入意味・正式1964-53/17-190/工数null/QA051final/全actualHOLD/全current WBS scope guardHOLD維持、費用はG13.07一回のみ。設計書閲覧正本origin/mainはfresh fetchで8b91944dfを確認済み、設計/仕様変更0。その後も残157の独立PG/PTへ自走し、通常群/commit/報告/PMO待ちで停止しない。
