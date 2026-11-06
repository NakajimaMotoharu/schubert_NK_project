# User追加画面資源 限定単体仕様

NK-WEB-002/SCR016/WBS-P016-16。関連RD FUN-008/AUT・UI225§4/236・SS313/314/SSC177。Test class UserCreateTemplateResourcePortTest、input021/022。UserCreateViewModelの既whole測定を再演せず、normal PG20586（資源70fb、Main D8と全Java byte一致）のactual admin/user-new.html/layout.htmlをrepo/抽出と照合する。独立固定map、固定文字と組合せtableをoracleとし、production methodでexpectedを作らない。

既UserAdminControllerTestの実fixtureを起動/分割しない。Thymeleaf/Jsoup/Servlet mockだけ、ローカル単体・外部通信無し、Main Java初期化無し。固定UUID形のhidden値は**表示用の非権限fixture**で発行/検証/消費をせず、_csrfとともにDOM保存前にredact、全21ファイルの原値不在をstrictpostする。実credential/Passwordは入力しない。未定義fieldの非機密markerは一切redisplayされないことを検証する。

| Test ID | method | 独立期待値・観点 | 派生DOM |
|---|---|---|---:|
|PT-UCREATE-DOM001|initialFormHasApprovedEmptyValuesAndDefaults|User追加title/admin上部表示、username空、Role USER/有効true、summary/alert無し、Password二欄value無し|1|
|PT-UCREATE-DOM002|everyRoleAndEnabledCombinationRetainsExactlyOneSelection|USER/ADMIN×true/falseの四組、各selected一つ、option順固定|4|
|PT-UCREATE-DOM003|emptyUsernameAndOtherIssuesHaveIndependentSummaryAndFieldScope|issues空/username/roleの3map、summaryの固定期待配列、username専用errorは該当時だけ|3|
|PT-UCREATE-DOM004|alertFieldAndUsernameEscapeLiteralMarkupWithoutNodes|script風文字/&/quoteをusername/alert/summaryへ設定、DOM text/value完全一致・実行要素生成無し|1|
|PT-UCREATE-DOM005|usernameDisplayKeepsExactByteBoundaryWithoutClaimingValidation|ASCII64/65文字を表示時にtruncateしない、maxlength64/required属性保持。サーバvalidation合格を意味しない|2|
|PT-UCREATE-DOM006|unmappedPasswordPropertiesAreNeverRedisplayed|未定義password系fieldの非機密markerを無視、Password二欄value属性無し/空/required/autocomplete new-password|1|
|PT-UCREATE-DOM007|displayOnlyHiddenFieldPostActionAndStaticNavigationMatchContract|一つのPOST /admin/users/new、表示hidden一つ、作成button・一覧戻り先・operation JS静的参照|1|
|PT-UCREATE-DOM008|ownedConcurrentFormsDoNotShareUsernamesOrSelections|2worker/8個別map、10秒join/TWR、username/selection/Password空の混線無し|8|

合計8method/21派生DOM。空/未定義/境界/異常文字/並行は上表で、null自体のcontractは既ViewModel/form責務の別証拠と分離。Java四counterはHTMLに存在しないためnull、100%へ補完しない。ローカル値表示の成功をUSER/ADMIN認可、token/HMAC/CSRF、Password policy、作成/重複防止、実HTTP/MVC/Browser/JS/DB、native/CHR/451/正式工程完了としない。

実行: `env PYTHONPATH=tools/quality python3 -B evidence/01_PT/016_NK-WEB-002/input/021_user_create_resource_qualifier.py prepare|static|run <frozenHEAD>|post <sameHEAD>`。環境Linux/Java25.0.4/Thymeleaf依存hashはmanifest。compile/staticが実行可能なTestだけを準備、RootFailed二/held四動的対象無し。BUG2347/YKT2092の原static4保持、適用2是正/再発防止PMD、最終8method/21DOM/XML/hash/終了code/全TestID guard。ad hoc生成scriptのjson import漏れでconfig未作成の開始失敗が一度あり、job/compile/Product起動前にconfigを作成、Product再演ではない。結果139/PG20642公開manifestへ対象commit/command/時刻/OS/tool/expected/actual/exit/source/input/hash/不具合を結合する。
