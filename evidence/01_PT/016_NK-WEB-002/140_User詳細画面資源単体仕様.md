# User詳細画面資源 限定単体仕様

Program NK-WEB-002/SCR017、UserDetailTemplateResourcePortTest、WBS-P016-17。関連RD FUN-008/AUT、UI225§5/236、SS313/314/SSC177。資源admin/user-detail.html/layout.html、normal PG20586/資源70fbのwebJARとrepo/抽出一致が前提。UserDetailViewModelは既FOUR100なので再演しない。既UserAdminControllerTestの実MVC/session/DB等を起動/分割しない、新たな独立mapによる表示資源だけの通常PTである。

固定12項目/日時/actorと操作formを**表示入力として**供給する。認可判定やSTATUS/ROLE/PASSWORD/UNLOCKの実行は無い。id17/version3/UUID形の非権限表示fixtureだけ、発行/検証/消費/HMAC/認証/実Passwordは無い。_csrf/operation hiddenはDOM保存前redact、全22ファイル原値・未定義field非機密marker不在をstrictpostする。Thymeleaf/Jsoup/Servlet mockのみ、Product Java初期化・通信・DB/VM/Root/鍵・JS無し。期待値はUI225の明示literal/table、独立mapの固定値でありProduction methodで作らない。

| Test ID | class method | 入力・独立期待値 | DOM数 |
|---|---|---|---:|
|PT-UDETAIL-DOM001|missingFormsAndMessageKeepDisplayMetadataWithoutInventedOperations|forms/message欠落（式のnull枝）、固定12表示項目/日時/active2/actor完全一致、操作section/alert無し|1|
|PT-UDETAIL-DOM002|emptyFormsCreateNoMutationControlsAndRetainStaticNavigation|forms空collection/message空、sectionのみ・操作field無し、一覧戻り先/JS静的参照|1|
|PT-UDETAIL-DOM003|absentEmptyAndMarkupMessagesHaveExplicitNullAndEscapeBranches|message null/空/markup三種、alertの固定期待配列、実行要素生成無し|3|
|PT-UDETAIL-DOM004|allOperationKindsAndRoleEnabledVariantsKeepSeparateControlShapes|有効true/false×Role USER/ADMIN、4formの順と固有field・有効化/無効化・選択一つ・Password二欄・Lock解除、別operation用control混入無し|4|
|PT-UDETAIL-DOM005|validationAndHiddenIdentityStayScopedToEachSuppliedForm|issues空/confirm有、summary固定、POST /admin/users/17、hidden operation/id/version/表示fixtureの保持、confirm必須、実行button|2|
|PT-UDETAIL-DOM006|metadataEscapesMarkupAndEmptyDateValuesRemainEmpty|username markup escape、5日時全空を明示5elementで確認、文字列の切捨て・代替捏造無し|2|
|PT-UDETAIL-DOM007|passwordControlsNeverRetainUnmappedFieldValues|未定義password field markerは出力されず、二欄value属性無し/空/required/new-password|1|
|PT-UDETAIL-DOM008|ownedConcurrentDetailPagesKeepTargetNamesAndFormsIsolated|2worker/8map/10秒join/TWR、各targetusername/UNLOCK表示が混線しない|8|

全8method/22派生DOM。null/欠落/空/4状態/例外的文字/境界active2/並行を表で扱う。実際の自己無効化禁止・ADMIN0人化禁止・owner・version conflict・Password policy・session revoke・token消費はこの表示試験では検証しない。全HTTP/MVC/Browser/JS/DB/native/CHR/451は未受入。HTMLにJava counterは無いのでnull、coverage100を補完しない。

実行: `env PYTHONPATH=tools/quality python3 -B evidence/01_PT/016_NK-WEB-002/input/023_user_detail_resource_qualifier.py prepare|static|run <frozenHEAD>|post <sameHEAD>`。input024に依存hash、Linux/JDK25.0.4。compile/static/source固定後に新Unit一回。全8method/FESaborted0/22DOM/input-resource-normalJAR-XML-hash/実終了をstrictpostする。BUG2348/YKT2093は初期Optional import不足、原PG20652 compile1と元source/producerを保持。staticはguardで未起動、合格にしない。修正後新compile/static/Unit/postで是正を照合する。結果141/PG20662 manifestへ対象commit/実行時刻/環境/command/expected/actual/exit/BUG/証跡hashを記録。正式1964PT-53scope/新leaf0/工数null/QA055lockHOLD保持。
