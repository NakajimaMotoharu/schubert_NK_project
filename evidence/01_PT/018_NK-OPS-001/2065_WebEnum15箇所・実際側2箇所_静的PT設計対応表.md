# Web enum 15箇所・実際側2箇所 静的PT設計対応表

## 1. 保存点・範囲・判定単位

2026-10-26、追加群G03_WEB_ENUM_STATIC_DESIGN_REVIEW_CAPACITY_20261026_V1、event2393開始、見積0.25/1/3pp・cap10。PMO17:50指令と477先頭の継続方針による公開既存資料だけの静的文書レビュー。元群2391 G03_WEB_ENUM_LITERAL15_V1の2/5/10pp・cap10・元費用は変更しない。

HEAD20bc2ac8d5c11bcb66ec8f2b5283e6f58c4a0bc7（origin一致）、source b8234ad5a1403e944acaf8e13f1e5f07a22309bd、Main21d不変。src差分0、当八sourceは変更していない。停止turn01a1749c-3fa6-7533-9699-c06be3c2447aはPMO報告のモデル混雑で、安全拒否/利用枠停止とは区別する。同じ失敗の再送、model/thinking変更、別agent/chat/経路は使わない。

参照2064 SHA d490f07a32adc8694fe2da1c94c28c451e310cf6a6025010aa0b448f909a208e、PG10426 manifest SHA ab39ebd9575eb734385f08f94bb67724252da20c7ba8f59e59910c333d8ca57b。当表のR01～R15/A01～A02はレビュー行IDで、新Test ID/製品試験件数ではない。source単位のowner/costは10420 registryのcanonical値、変更担当はG03.01と区別する。

## 2. 正本・独立期待の固定根拠

18:01頃fetch後のorigin/main=8b91944df5820535e23ba2469740f1c0aa94c447。次の正本は作業treeとorigin/mainのbyte一致を読取確認した。上位資料/期待値をコード都合で変更していない。

|正本|SHA-256|当表への要求|
|---|---|---|
|UI224 質問・通知画面設計|f4e20115d1438064729150d6a717bdb71a477351efa718e4f6c22b52d36aa4c5|SCR020/021のstate/type/削除/表示、質問・回答表示|
|UI226 認証・認可・session|30e0470c98990546f4d02f8e2c72088eb4779950ac56ac3354b0b3e1e0502d40|USER/ADMIN、保存/失効/認可境界|
|UI236 管理・質問・通知電文|0468f20da240ed61e056084f80e88f3b3f5d60b3afb70f23710a8320c5c653c9|NTS/NTDのRECEIVED/PROCESSING/COMPLETED/ERROR/CANCELLED、QSS/QSDのANSWERED/UNANSWERED/ERROR、固定byte位置|
|SS313 画面template/controller/form|76946dc55f4e2a4bda6dd40610ce5d993d0b2b727b3cbeffd80afa930a5af67b|閉view投影/明示controller・HTTP/DOM/認可との分離|
|SS314 認証/session/CSRF|ab7a1907d0861ca1b6d4181d674f98a73c13f8a4b897b86f655b5a30ce202a7b|§3/3.1/7.2.6、内部authorityはROLE_USER/ROLE_ADMINの一個、wire/DB roleはUSER/ADMIN、未知/credential/detail/不一致拒否|

独立期待（将来是正の根拠であり今回実装していない）：

- AnswerStateの入力enum identityから固定ANSWERED/UNANSWERED/ERRORを選ぶ。表示labelは既063 PT-QRY-HTTP006/008/011の回答済み/未回答/エラーの固定表を保持し、Production state.wireValue/label methodからexpectedを生成しない。
- NotificationStateも五つの固定wire文字列をTest側で選ぶ。既061のlabel表（受付中/処理中/処理完了/エラー/取消済み）は変更しない。UI224で全状態のlabel全文が逐語指定されているとは追加認定せず、既PT固定期待の根拠を保つ。
- authorityはTest principalのUSER/ADMINという入力identityからROLE_USER/ROLE_ADMINを明示する。Production encoder、権限設定、実認証又はアクセス経路は変更しない。実際値側のwireValueを検査する独立literal assertion二件は不変更。

## 3. 15対象・2対象外の対応

Source aliasは次節の完全hashへ結合。全行の動的状態は今回NOT_EXECUTED_HOLD/coverage未測定。既成功の再認定/他sourceへの転用なし。

|行|Source:line・class/method|既Test ID・source責任|要求/対応Main|期待・分岐/assertion・不足/残存証拠|
|---|---|---|---|---|
|R01|N:599 NotificationControllerTest#ntf007AllStatesTypesSummaryAndImmutableDisplay|PT-NTF-HTTP007、WBS-P016-21|UI224§4/UI236§8、NotificationListViewModel|5state×削除有無、3type caption/日時/summary/link/immutableを別assert。state期待だけが同Production encoderに依存。固定五wire文字列への分離と元byte/他assert保持が未実施。|
|R02|N:925 #detail002StateDatesDeletedAndEmptyAnswerProjection|PT-NTF-DETAIL002、WBS-P016-21|UI224§5/UI236§9、NotificationDetailViewModel|五stateのlabel/削除/空回答。COMPLETEDかつ非削除だけanswer/link、削除は本文非表示。label MapのkeyへSUT encoder使用。固定key分離・dynamic正負/全分岐/資源後条件は未証明。|
|R03|Q:510 QuestionControllerTest#qry006DetailWholeWireAndDisplay（fixture）|PT-QRY-HTTP006、WBS-P016-18|UI236§12/UI224、QuestionWireClient→QuestionController.detail|両role×0000/0200×3state×ID1/N12最大のfixture stateをSUT encoderで生成。Test固定三wire値で入力を作る修正が未実施。|
|R04|Q:527 #qry006DetailWholeWireAndDisplay（expected）|PT-QRY-HTTP006、WBS-P016-18|QuestionDetailViewModel.from/label|回答済み/未回答/エラー、回答可否/時刻、ID/受付ID/owner/body/immutableの既assertを保持する。label keyの共有encoder依存が未是正。R03と同じmethodだが別箇所でありPT二件にしない。|
|R05|Q:687 #qry008MvcEscapeRolesStatesAndMethods（fixture）|PT-QRY-HTTP008、WBS-P016-18|UI224/236、QuestionController/MVC templates|両role×3state、HTML特殊文字は既公開合成入力。fixture stateの独立literal化が未実施。MVC開始やHTML入力の動的再演は今回許可しない。|
|R06|Q:704 #qry008MvcEscapeRolesStatesAndMethods（一覧expected）|PT-QRY-HTTP008、WBS-P016-18|QuestionListViewModel→questions/list|一覧state label、escape、ADMIN限定条件を別assert。state label Map keyの依存が未是正。|
|R07|Q:723 #qry008MvcEscapeRolesStatesAndMethods（明細expected）|PT-QRY-HTTP008、WBS-P016-18|QuestionDetailViewModel→questions/detail|明細state label/本文escape・空回答等を別assert。R05/06と同一Test ID、source/hashを共有しても成功数は加算しない。|
|R08|Q:902 #qry011FactoryControllerNullAndIntegrity|PT-QRY-HTTP011、WBS-P016-18|QuestionDetailViewModel.from、controller/form境界|正常三stateのraw表示state期待をSUT encoderで生成。null/欠落/不整合/immutableは既仕様へ追跡、今回は実行せず、正常stateのsource修正も未実施。|
|R09|I:681 ApiSessionInvalidTest#setActor（fixture）|PT-WEB-159/160/164＋PT-USER-BIZ007、source owner WBS-P015-06|SS314§3/7.2.6、ApiSessionInvalidHandler/ClosedWebAuthentication|明示authority一個/credential null/閉principal。直接callはweb159/160/164、biz007。0102終端/監査/DB/Cookieとself-reset成功を混同しない。BIZ007の逐TestID主責/終了依存の横断joinは本表で未確定、当部分HOLD_SCOPE_UNRESOLVED（source ownerは既知・不変更）。|
|R10|E:919 ErrorMvcTest#set（fixture）|PT-WEB-149/156、WBS-P016-24|SS313/314、WebDisplayContext/ClosedWebAuthentication/error dispatch|匿名/認証済snapshotと偽dispatch拒否のTest入力authority。実設定・権限は変えない。unknown/foreign/credential/detail等は元期待、固定authority化と実HTTP/DB故障後条件は未証明。|
|R11|S:784 ScenarioControllerTest#setActor（fixture）|PT-SCR-005/014、WBS-P016-07|UI221～223/SS313314、ScenarioController/ApiSessionInvalidHandler|result分類/例外伝播用principalのauthority。通常UI/state/messaging/0102失効を新grantへ変えない。fixture encoderの分離/元assert保持が未実施。|
|R12|F:435 SessionAccessFailureTest#setPrincipal（fixture）|PT-WEB-127/130、WBS-P015-02|UI226/SS314、WebAccessFailureHandler|閉role拒否403/監査・100並行actor分離の入力authority。nullable/foreign/cause診断・ThreadLocal後条件は実行未確認。|
|R13|L:535 SessionLoginHandlerTest#auth（fixture）|PT-WEB-113/114/117/119、WBS-P007-06|UI226/SS314、MqLoginSuccessHandler|成功/不正identity/null・公開故障/並行の入力。authorityは固定ROLE_USER/ROLE_ADMIN、HTTP302/保存済GET/Cookie/監査/応答失敗の既期待は保持。provider/DB/fixation/handler成功は未認定。|
|R14|C:676 SessionSecurityContextTest#auth（fixture）|PT-WEB-068/069/070/071/072/073、WBS-P015-02|SS314§7.2.6、EncryptedSessionSecurityContextRepository/ClosedWebAuthentication|USER/ADMIN一authority、credential/detailなしの正常Test認証。foreign型/不正principal/余剰・null・別role authority等の負例は別literal。fixture依存除去・実PG/fixation/失効/並行後条件は未証明。|
|R15|C:715 #assertIdentity（expected）|PT-WEB-068/070/073/074/075、WBS-P015-02|SS314§7.2.6、ClosedWebAuthentication.authenticated/principal|authority listの期待を同encoderで生成し共通誤りを見逃し得る。expectedを固定文字列一個へ。principal/name/credential/detail等の他assertは保持。認証復元/現在有効性/DB保存をレビューで成功化しない。|
|A01|A:714 SessionFormLoginTest#web089ConcurrentLoginChainsKeepPrincipalsAndCookiesSeparate|PT-WEB-089、WBS-P015-02|UI226/SS314、provider/login後の閉principal|期待側はn偶奇のUSER/ADMIN literal、wireValueは実際側。独立assertionであり変更しない。PG10426の元hashを保持、元dynamic成功は今回未照合。|
|A02|B:335 WebSecurityChainTest#web136ConcurrentHttpChainsKeepSessionsAndAuditIsolated|PT-WEB-136、WBS-P015-02|UI226/SS314、単一chain/閉principal|A01と同じactual側のencoder検査。実Tomcat/PG/監査/全資源終端を含む元Testは未実行HOLD、assertionをexpected helperへ誤置換しない。|

### Test IDの根拠

- N:016_NK-WEB-002/059のPT-NTF-HTTP007、061のPT-NTF-DETAIL002。
- Q:016_NK-WEB-002/063のPT-QRY-HTTP006/008/011。
- I/E/F/L/C/A/B:015_NK-WEB-001/001の各class#method対応表。Iの追加biz007は016_NK-WEB-002/081のPT-USER-BIZ007まで確認したが、逐TestIDの横断責任/受入依存は上記限定HOLD。
- S:016_NK-WEB-002/001のscreens005/014→PT-SCR-005/014。helperの直接call箇所から対象methodを限定し、各family全件を実行・影響確認済みとしない。

## 4. Source hash（base=`src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/`）

|alias/file|SHA-256|
|---|---|
|N NotificationControllerTest.java|d2c624c5e8a334cc645a485c8a29d81829e4f7fc3de171799e3041c0b53232a8|
|Q QuestionControllerTest.java|172ef36eeaa00bbdb67d47966ebef897177479c5382cd58d7c81c6032b181099|
|I ApiSessionInvalidTest.java|a49030f0a351f0d6d029d20c036af318a62f91de49b9be06b92f16257351e82e|
|E ErrorMvcTest.java|0362bdfe6994ceda94dca00568c9f2befb3dc315449cc335b99b850d39a1b83e|
|S ScenarioControllerTest.java|6a6364f62363d72da0de17a6a4a21909c39f99c289d49d7af5a167859fc83f02|
|F SessionAccessFailureTest.java|e5e760caf9d76562da194604ca5e32f806a494df40368699233780c0d0b1672b|
|L SessionLoginHandlerTest.java|0dc1ce9bd3f919c9539de576884c9b5c55df883981d8ad8bf72202b33b0ddfae|
|C SessionSecurityContextTest.java|eb63e3a93db5cb2bc1229fff6ac40521d774a43acdbcf4ba172df855bb384eeb|
|A SessionFormLoginTest.java（対象外）|6e3900960796e66935d265d28c2948d4a28d07ea962a4f6559ea0986c5c9b9d2|
|B WebSecurityChainTest.java（対象外）|a87bf173237a9d1b96ed0a8676c115d28c519f4d241e8dfb99f25d90e0e7234b|

Main読取結合：NotificationListViewModel 0d9826eecee7a3e0e63e779dac32949bced1748bff8d927b58e10c23160b5ed7、NotificationDetailViewModel 4221d0482e8b5f84224a2ec7d91cba648046d5e23bcef3112c5bf6f48353a7cd、QuestionListViewModel eef4e7d0a88a56f5209e5ece2ceec9cb5abd57dc292cd8b380816419b583f497、QuestionDetailViewModel 6a10ebbadbc52df317de2fec18b68aab3275d832b5f73e0c4edfe24935b1903c、ClosedWebAuthentication ad4406d529ecd8fcbca8c523d74bb6d8f6602632ef7cdd768f589bf52ce58214、EncryptedSessionSecurityContextRepository d6ff8eec25554583f88ad34f79ced1bf34aec6303b286ceb65b6ddae15835da2。

## 5. 動的依存・未証明・終了判定

八Test class全てにWebLogDatabaseFixtureを開始する@BeforeAllがある。N/Qの対象methodがtyped projectionだけに見えても、元classのmethod選択実行で実PG fixtureが自動開始する。単なるpure-method判定で通常PTへ進めず、新fixture/ハーネスによる別経路実行もしない。authority側はsession/暗号/DB/HTTP/認証/失効等も元依存であり、当表では読取対応に限る。

今回の結果はSTATIC_PT_DESIGN_REVIEW_COMPLETE_WITH_EXPLICIT_HOLD。全15箇所＋対象外2assertionを対応付け、R09/BIZ007の逐TestID責任/終了依存はHOLD_SCOPE_UNRESOLVEDとして残す。BUG1829/1830と元2391の実装は未着手/未完、未実施PTはNOT_EXECUTED_HOLD、coverage未測定。今回のcompile/JUnit/製品/helper実行/動的load/DB/鍵/実認証/設定・権限・アクセス経路/Root/VM/native/Graph9操作は全0。PG10426の元実行を再演していない。未知の外部job/所有はUNOBSERVED_HOLDで、停止・正常終了と推定しない。

PT_EXECUTION_EXEMPT、ACCEPTED_WITH_USER_APPROVED_PT_ALTERNATIVE、製品PASS、native、正式品質、工数率へ変換しない。正式1964PT/53scope・個別17/190・工数null・QA051 final・451/全安全HOLDは不変更。原本DB/Backup/鍵/stash七/Scenario3/Current baseline/native/旧失敗/held witness二fileは保全。

次は本表と元2391を保存し、当八source/原jobへ再送せず、別の独立許可済み工程の具体的着手条件を調べる。候補は当八sourceと重ならない既存pure view-model TestのF03残指摘（既PMD10394参照）。新群を開始前見積/cap10・source/副作用/依存の確認で分離し、適用性未分類を0へ変えない。限定レビュー/commit/PMO返信待ちだけでPGPT全体を停止しない。
