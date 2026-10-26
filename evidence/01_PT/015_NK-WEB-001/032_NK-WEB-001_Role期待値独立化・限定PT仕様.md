# NK-WEB-001 Role期待値独立化・限定PT仕様

BUG1825/YKT1576、G03.01、source b98ab2b8a2e8868f07471a95530d1005b6121b10。元source3d9fからTest13source/18期待式だけを、UI226/236のUSER/ADMINを明示したexhaustive switchへ変更。Production role encoderを期待値生成に呼ばない。RD FUN-002/004/006/007・AUT-001～004、UI223/226/234～236、SS313/323、元006/016/020を継承する。

## 着手前判定：通常PTを許可する最小4method

|Test ID|Class/method|fixture/入力|独立期待値|
|---|---|---|---|
|PT-WEB-182|ScenarioHierarchyViewModelTest#web182GameDisplay|USER/ADMINの合成SessionPrincipal、固定GameRecord二件|roleはUSER/ADMIN、reader、code NUKITASHI1/NUKITASHI2、名称NUKITASHI/NUKITASHI2、href /scenarios/NUKITASHI1と2、順序固定|
|PT-WEB230|AnimationViewModelTest#web230AnimationMenuCounts|両role×五固定count vector、および不整合三入力|literal role/reader、MAIN・OVA・opening・合計の各Test値、固定redacted文字列。不整合三件はIllegalArgumentException|
|PT-WEB246|MusicHierarchyViewModelTest#web246CategorySnapshot|両role、曲29/BGM99/その他1、totalCount3|literal role/reader、曲/BGM/その他順、29/99/1、合計129、明示UTF-8 percent-encoded href三件|
|PT-WEB247|MusicHierarchyViewModelTest#web247SectionSnapshot|両role、親曲、ゲーム10/アニメ15/キャラクターソング4、totalCount3|literal role、親曲、順序/10-15-4、合計29、明示親/ゲームpercent-encoded href|

上表以外のTest methodを発見・実行しない。catalogは四つのclass#methodの完全一致、suite三。新Test IDなし、既成功の確認だけの再演でなく、期待式を変更した当sourceに対する限定再試験である。全classのnull/境界/例外/並行を今回網羅したとはしない。

Test三classのheader/field/selected methodとactor・固定record helper、ProductionのGameList/AnimationMenu/MusicCategory/MusicSection/TopBar/SessionPrincipal、Protocolの関連record/enum/AuthenticationContext及びrequireUnsignedRangeを読取確認。選択methodはin-memoryの文字列/collection/数値/URL変換だけ。両role/上限countをTestで明示し、認証contextは公開合成値のformat確認のみで暗号/key処理なし。Test lifecycle annotation/static初期化blockなし、Spring/Thymeleaf/HTTP server/実DB・file・native/Rootを開始しない。Test内の他methodやimportsを全実行許可としない。

元API UserCommand、controller/template、その他未確認TestはNOT_EXECUTED_HOLD又は未選択のまま。新fixture/拒否対象の別経路は作らず、既独立な通常画面部品の元methodを明示選択する。Graph9/Root11/実VM等全HOLDは不変更。

## source/static/compileと証跡

PG10392 plan af9752f79f1a4af7be0264e301841f31dc1be0f3976115198ec6a112f8ab147c、所定static PG10394 raw250/CS0/processing0/exit1（0b1be65fb8da3963f2565090880365c7091fecc39578ccc17b13dbbc25299f38）を未分類・未受入として保持。正常compile PG10396 actual0/六jar/PT0（42e446d87c251b819592758cbadeee1d5ba4e785d91269edfb6ac873f71b8b5c）。staticを製品PASSへ変換しない。

PG10398はsource/normal class/helper/catalogを束縛する着手前manifest、PG10400は四methodのJUnit/XML/exec/真正終了、後続postは同source/coverage/全Main不変・選択外Test byte等を確認する。coverageは測定値をそのまま記録し100%未達を補完・旧exec合成しない。manifest/hash/command/環境/actual結果は033へ、初回開始記録だけで成功にしない。正式1964PT/53scope、個別17/190、工数null、QA051 finalを維持する。
