# WebBrokerContexts 全契約・静的レビュー仕様

Program NK-MSG-002、費用主担当 WBS-P005-02。開始 PGPT-20261008-4144、見積 .5/2/5pp、cap6。対象は current4217 の WebBrokerContexts 全209行と既存関連5 Test source。これは未実行のPT設計レビューであり、PT PASS・coverage・実資源所有・PT実行免除を認定しない。元の実行証拠と費用は保持する。

正本は origin/main の UI231/SS321/SS343/SS354、特に SSC311/314/315/316/330/334。入力の予想値はその明示契約と既存Testの独立literalから取り、Production methodでexpectedを生成しない。

| Review ID | 対象method・独立期待 | 既存Testで照合する範囲 |
|---|---|---|
| WBRO001 | create/createRetainingUnknown: credentials非null、supplierとlock/方針を取得前に準備、取得後は同一factoryをfinal二fieldへ格納 | CredentialTest、FactoryOwnershipTest |
| WBRO002 | newFactory: exact tcp://127.0.0.1、port1..65535、先頭0/localhost/query/0/65536拒否、connector connect timeout3000 | endpointAndProviderSettingsMatchIndependentSs321Literals |
| WBRO003 | configureOwned: acquire/policy非nullを取得前に確認、取得一回、未取得/nullを推定closeしない | mqfact311001、hold316008 |
| WBRO004 | 設定順と値: callTimeout2000、failureCheck10000、TTL30000、initial3、reconnect-1、retry1000、multiplier2、maxRetry30000、window1048576、durable=true、preAck=false、topology=false | mqfact311001/002 の独立12 literal |
| WBRO005 | 12 setterのどこで失敗しても取得済みfactoryへ一度close、設定後続を行わない | mqfact311002 の12×4表。今回実行しない |
| WBRO006 | close成功なら設定primaryを同一保持、cleanupの別Throwableをsuppressed、same-objectはself-suppressionしない | mqfact311003 の4×4＋same-object |
| WBRO007 | cleanup Error対非Error primaryだけcleanupを優先し元primaryをsuppressed。primary Errorなら元primaryを維持 | mqfact311003、SS321SSC311 |
| WBRO008 | suppression無効primaryではattachment不能でもfatal graphを見落とさず、分類はclose後 | fact334008、WebStartupException.attachSecondary の読取のみ |
| WBRO009 | 三/四引数注入入口はcallerが完成まで保護する借用入口。Production createは取得済みfactoryを注入入口へ渡さない | Main private ctorとSS343の順序。注入testを実Production所有の証明へ転用しない |
| WBRO010 | contexts/openはstopping後にpassword supplier/接続先を呼ばない | everyContextHasFixedWebRoleAndModeAndErasesBorrowedCopy、fact334007 |
| WBRO011 | 各openで独立copy、role nk_web、SESSION_TRANSACTED=0、providerへ3引数だけ。copy長1..65536 | everyContext...、nullAndProviderFaults...、fact334006 |
| WBRO012 | copy取得成功後の正常/null/長さ不正/provider Runtime/Error全経路でcopyをzero-fill。supplierが返す前に失敗した未借用copyはsupplier責任 | fact334006 とnull/provider表。JMS String/SDK内部copy消去は主張しない |
| WBRO013 | password/provider例外のcause/suppressed/JMS-linked/SQL-nextにfatalがあれば固定例外へ隠さず伝播。identity seenでcycle有限 | fact334006/007、WebStartupException.preserveFatalの静的読取のみ |
| WBRO014 | live closeは要求時stopping=true。失敗はclosed=falseを保持し、open拒否、未確認ownerだけ明示close再試行。成功後closed=trueで以後no-op | closeIsIdempotent...、fact334007。設定失敗の「一度close」と区別 |
| WBRO015 | retainUnknown=trueではprovider設定cleanup/live close失敗を保持policyへ渡す。nonreturn時は外側解放/正常return/自動再試行を認めない | hold316009/Driverの期待OUTER_RELEASED非到達。子job/保持実行はHOLD |
| WBRO016 | private final ReentrantLockをopen/close双方で取得しfinally解除。状態検査→copy→provider→消去を同lock内に置く | Main読取による直列化確認のみ。既5Testに明示並行競合の独立実測は確認できず未証明 |
| WBRO017 | 識別用toStringは固定REDACTED、通常公開例外は固定文、password/provider診断をログへ出さない | Main全体と既4Test/graphの固定message/null cause/suppressed0期待 |
| WBRO018 | 資格範囲を分離: real credential/readiness/embedded broker/native保持・四held例外の初期化を今回実行しない。既存Testの別名/抜粋/新fixtureで再演しない | CredentialTest2件、RetentionTest2件、BrokerGraph3件を含む全14methodは未実行の設計参照 |

一次点検は取得順・データ寿命から上表を読む。反証点検は状態 OPEN→STOPPING→CLOSED、例外primary/secondary順位、copy借用前後の三軸から逆に読む。元PTの成功歴を現在の依存全体へ移植しない。

許可された自動確認は公開Main/Test/設計/既normal20990・六静的20992のhash対応のみ。新しいcompiler/静的engine/Unit/JMS/HTTP/DB/native/VMの起動は不要。binderもProduct import/初期化・fixture呼出し・設定/権限操作を行わない。coverageは未測定null、新Test/newMethod/newSource/newLeaf0。
