# Music曲一覧 HTML資源 単体仕様

NK-WEB-002/WBS-P016-13、SCR013/FUN007/UI223235/SS313・352/PG-D365、PT-MUSIC-DOM001..008。980/event4013原1/3/6pp cap8。MainD8のmusic-list.htmlとlayout断片のactual normalJAR/extracted/repo byteを結合する。既MusicHierarchyTemplateTestはcategory/section、ContentDetailControllerTestの実MVC/wire fixtureは実行しない。新試験は独立map+actualtemplateの表示枝とnegative入力だけを対象とし、既成功確認再演ではない。

1. MDOM001: 通常二曲、順序/title/path/controls/preload/media/downloadの明示DOM値。
2. MDOM002: 通常/ペアそれぞれ空、0曲、player/placeholder無し。
3. MDOM003: ペア両側/mainのみ/instrumentalのみ/両側欠落の四表示入力、独立固定audio/placeholder数・順序。両側欠落は不正上流mapの防御的表示確認であり、正常なProduction viewmodelと認定しない。
4. MDOM004: title/pathの<script>/属性境界/Unicode escape、HTML要素化無し。
5. MDOM005: page title/category/topbar/固定nav、USER/ADMINの表示値、category href保全。
6. MDOM006: byteSize 0/1048576/1572864 → 0.0/1.0/1.5 MB（独立1024²算出）、locale Japan。
7. MDOM007: inactive collectionをnullにした二mapの条件式短絡、active側以外を読まない。これも上流invariantの合格ではない。
8. MDOM008: 2worker8render、各10秒join、別title/map/output非混在。

期待値は上記literal/明示map、Production viewmodel/formatterから生成しない。8method/18派生DOMをnew-only保存する。locale/HTML頭をJsoupで解析し、synthetic CSRF hidden値は保存前redact。実cookie/token/key/DB/Root/VM/native/HTTP/audio取得/Browser操作なし。SpringTemplateEngine/WebContext/MockServletのみ、ApplicationContext/Production Java classpath初期化なし。全branchはHTML条件の列挙でありJava四counterは対象無しnull、100%を捏造しない。runtime MVC/認可/API/Range/CHR/451/個別leaf受入は未完。

input005 qualifier/config006、prepare20468/static20470→Git固定→PG20474一度だけrun/post。input/hash/resource/JAR/選択TestID/XML/環境/exitをmanifestへ保存し、結果131へ結合。依存JARは元004 exacthash再利用、新tool導入無し。失敗した場合は合格に足さず、実装済み仕様違反は修正前915/916へ起票する。
