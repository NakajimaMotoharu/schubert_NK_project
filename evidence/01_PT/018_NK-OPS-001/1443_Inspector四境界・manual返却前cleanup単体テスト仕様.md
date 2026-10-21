# Inspector四境界・返却前manual cleanup PT仕様（実装前）

同群ORDINARY_JDBC_MAPPER329/event1625、開始.5/1.5/4pp不変、追加発見BUG1595/YKT1348を区別する。主P004-04、共通P018-05の再製造費重複0、実配賦/N/T null。関連SS312/314/324/332/3436.6/354、QA046/SSC329330、BUG1592/YKT1345。実Main/Testは先行256原qualificationが終わるまで変更しない。

## 着手前判定

PT_DEFAULT。自己所有Java interface proxy、固定独立wire/JCE fixtureのみ、Connector injectionでDriverManagerを呼ばない。URLはpublicな不使用localhost/1の形式入力、公開canary bufferは接続・認証に使わずclose時erase。鍵・原本・DB・VM・サービス・failed cohort・intent/permit・外部接続なし。既instanceを使う試験ではborrowed connectionのcommit/rollback/close0、factory失敗では取得済connection close1、handoff成功ではprovider close0/caller close1が独立oracle。

## 予定Test IDと独立期待値

PT-DB-INSPECTOR-GRAPH329001: connectorのSQL次graphに同一fatal、返却0/未取得close0/設定Properties erase。非fatalcycleは固定08001/catalog原因・suppressedなし。

002: admit(getAutoCommit)のSQL/cause-next fatal＋cleanup SQL/Runtime、同一fatalを保持、close1/後続SQL prepare0/commit/rollback0。

003: 直接primary Error＋各cleanup SQL/Runtime/Errorはprimary identityを保持、nonfatal primary＋cleanup Errorはcleanup fatalを伝播、全close1。primaryとsecondary同一objectでもself-suppressionを発明しない。

004: 非fatalSQL/Runtime循環と同一SQL secondaryは有限帰還、SQL固定08001、未知Runtimeは元identity、close1/Properties erase。Productionの同methodでexpectedを生成しない。

005: 手書きadmission role/database/recovery一行の正常proxyはConnectionを同一objectで返し、返却までprovider close0、caller close1、Properties erase。getAutoCommit/readOnly/ResultSet/Statement呼出順・closeを独立counterで検証する。

006: null返却/通常SQL・不正admissionは従来固定失敗、未取得close0/取得後close1、closed providerはconnector0を維持。

007～009: Authentication/NonAuthentication/QuestionMutation各isConsistentの構造有効な手書きsnapshotを用い、getAutoCommitにSQL next/cause/suppressedのfatalを注入して同一Errorを期待、非fatalcycleは既false、call到達1/borrowed commit/rollback/close0。return falseを無条件fatalへ変更しない。snapshot fixtureは入力組立のみ、expectedは固定identity/false/counter、暗号秘密・wire原本を証跡へ出さない。

## 検証・未実行

原Mainで目的赤を真正XMLから確認→当4 Mainの必要PG→同Testbytes/既Inspector domainsでgreen→当source原Jar/XML/counter/static→全113適用性/同型manual Web/必要まとめ全体。有限profileと所定の全六baselineを維持する。counter/coverage100・全体/正式/nativeは未測定・未受入、拒否PT代替0/全HOLD/QA051final不変。具体run/count/hashは実Test宣言確定後、開始前にdriverへ固定して追記する。
