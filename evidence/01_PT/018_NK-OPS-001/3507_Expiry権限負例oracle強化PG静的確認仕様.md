# NK-OPS-001 PT-OPS-MQ-022 oracle強化（PG/静的仕様）

元048/SS321§10/12・UI251§8・SSC075076、BUG2242/YKT1988、644645を適用。既存十一操作（maintenance許可2/拒否4、Web拒否2、Ops許可3）と実Broker/roleを保持する。新しい動的fixture/launcher/PTを作成又は実行せず、PG是正・compile/静的確認/独立設計レビューに限定する。PT分類はHOLD_SCOPE_UNRESOLVED維持、PT実行免除の認定なし。

|観点|入力/状態と独立期待値|
|---|---|
|成功|管理応答がnonnull・operation result・status非null trueだけtrue。終了時cleanup成功も必要|
|真正管理拒否|status=falseかつ固定SDK AMQ229032のuser・VIEW/EDIT・mops.resource.operation全文一致だけfalse。userは所有ClientSessionと同じfixture生成userへ結合|
|送信拒否|request内ActiveMQSecurityExceptionでAMQ229032/user/SEND/activemq.management全文一致のみfalse。認証失敗・別code/role/address等は伝播|
|reply準備拒否|requestor constructor内のtyped security exceptionだけ対象。CREATE_NON_DURABLE_QUEUE/CREATE_ADDRESS、AMQ229032 address形又はAMQ229213 queue形を固定sourceから確認。全publicfixture user一致、temp reply名はactivemq.management.＋canonical UUID、queue/address同一。認証・CONSUME・別対象・malformed/nullは拒否成功にしない|
|無応答/失敗|null reply・欠落status・非operation result・未知管理errorは固定AssertionError。transport/未知Runtime/NPE/Error/無関係なsecurity failureをfalseへ変換しない|
|cleanup|ClientRequestor TWR closeはdenial catchの外。closeが失敗したらfalse/trueのreturnを抑止して伝播。owned clientはAuthenticatedSession TWRで閉じ、record diagnosticsはredacted固定文|
|所有/ログ|wrapperは既publicfixture usernameとClientSessionだけ、password非保持。raw error bodyを新AssertionErrorへ転記しない。元role追加・最終reply address残存0という後条件は不変更|

SDK2.56.0のManagementServiceImplは全Exceptionを失敗flag＋getMessage文字列にするため、flag falseだけではDENYにならない。SecurityStore/ActiveMQMessageBundleが明示した229032/229213とClientRequestorの作成順/targetを根拠にする。645に公式source URL/entry/hash/line範囲・実binaryのpublisher checksum一致を保存し、SDKの値判定を呼んでexpectedを生成しない。

通常PGのscopeはこの一Test source。884のGit管理公開Test Javaからheld二名をread/stat/hash前に除外しManagementHelper＋catchfalse/nullable successを調査、同形producer候補一件。alias/別client APIや全認可実装の包括監査ではない。全候補の修正/非該当根拠はSDK scanと3508結果へ残す。

実commandは固定JDK25・既normal14216のMain jars/Batch test classpathをcompile専用で使用、明示一source/-proc:none/-Xlint:all/-Werror。JDK tool/PMD/CheckstyleはSDK/broker/testclassを初期化しない。source/hash/時刻/真正exit/静的指摘/独立branchレビュー/原失敗・未実行PT・coverage nullは3508と公開manifestへ保存する。新PT/PASS/実測coverage/実RBAC/BUG最終閉鎖/個別WBS受入は加算0。実broker・same-source全451/traceと実postは将来の許可済み工程へ保持し、未実施をstatic成功で代用しない。
