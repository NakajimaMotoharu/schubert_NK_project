# P01501 通常session codec 29件・fatal独立vector仕様

Program NK-WEB-001、WBS-P015-01、SS312/314/331/352、QA049、BUG2704/2705・YKT2359/2374。元WEB001..004、009..023とTOKV206、PT-OPS-CAUSE3404-003・SESSION-GRAPH328001..003は001正本の既期待値を保持する。全fixtureはID4/JSON7/Payload9/graph1+3の既存24件と新5件、全6classの29件。Fixture3全body1,075行/Graph88行を公開sourceで確認、元DB/Spring/actualWebStartup fixture抽出なし。

|Test ID|class.method|独立期待値|
|---|---|---|
|WEB-SESSION-FATAL001|SessionPayloadFatalContractTest.fatal001ProviderCauseKeepsExactFatalAndWipesNonce|public合成ProviderException.cause内Errorを同一objectで伝播、nonce12byte全0|
|WEB-SESSION-FATAL002|fatal002SuppressedSqlNextReachesSameFatalWithoutChangingGraph|provider.suppressed→SQL.next→cause Errorを同一identity、元全edge不変/nonce消去|
|WEB-SESSION-FATAL003|fatal003NonfatalCyclesReturnOnlyFixedCatalogAndWipeNonce|非fatal cause/suppressed cycle有限、固定CRYPTO_UNAVAILABLE文字列/無cause無suppressed/nonce消去|
|WEB-SESSION-FATAL004|fatal004DirectErrorIsNotNormalizedAndCleanupStillRuns|直接Error同一identity、finallynonce消去|
|WEB-SESSION-FATAL005|fatal005FatalOperationStillAllowsIdempotentClose|fatal伝播後のclose/repeatedclose完了、closed codecはIllegalStateException、nonce消去|

期待Errorはfixtureが直接保持するobject、通常error文字列・byte0・独立JSON/AAD/JCE goldenは固定値/独立DataOutputStream/JCEで算出しproductionでexpectedを生成しない。public zero32byte vectorと公開nonce/UUIDだけをJUnit process内で使用、配備key/session/raw/private物を読まない。Provider削除は既WEB022の当JUnit JVM内SunJCEだけ・finally原位置へ復帰、host設定/OS/権限/VM変更なし。製品filesystem/network/DB/JMS0、tool own tmp/source/class/XMLのみ書込。null/欠落/空/未知型/UTF8/length/version/key/close/100並行nonce/monitor isolation/close競合は元wholeTestを保持。

BUG2705の三Test四poolは元全assertion逆変換一致のままfinally shutdownNow/await10秒、Future20秒保持。codec closeはworker停止確認後、releaseLatchを停止前へ置く。不明owner/期限切れを成功へ変換しない。新Testは5秒SEPARATE_THREAD上限、独自provider登録やprivate snapshot構築なし。

Main fa9b9fa8（CODEC2+Repo.hashの既fatal口四接続）、新Test pinは実行時記録。PG27390はactual4/Repo/Springを含まない正常15source/16classだけを変更なしroot Maven compiler（release25/ErrorProne2.50/NullAway0.14.1/JSpecify/lintWerror）で新規compile。既currentProto176を同byteへ結合し全192物理classを保持、rootmodule全buildとしない。新Test6 javac/PMD/CS/configuredGJF、Main2 fresh PMD＋全15SB0、13不変sourceのstyle/hashのみ再利用。Gson2.14/annotation2.48/JSpecify1.0.1/Proto同hashをcompile/aux/runtimeへ固定。raw31の個別適用性はPG27398へ記録、抑制/ルール変更0。

費用.25/.75/1.5pp cap2、原見積り不変更。PG27394は新5だけを元de781相当のnormal実classへ実行する故障再現。期待失敗3が成立しても製品PASSでなく元失敗として保存、旧成功確認の再演なし。PG27400は固定Test sourceの変更後全29を一回、PG27402は独立source/CRC/init/単exec・元OS終了/XML/全@Test/FESaborted0/四counterを検証。全192依存missと自然branch0は保持、必要target100のみ実測成立後記載する。新5のunique定義とred/fixedの延べ実行を区別する。

実行: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1617_session_fatal_original_red_control.py <Test source>`、次に`1615_session29_qualifier.py run <同Test source>`。PG27394の製品終了1を判定工具0と混同しない。元Bugs/fatal41site・Repo.hash・実DB/Spring/認証/CHR/native/451の終了依存は未受入、正式1964PT/53scope・元190新0・工数null維持。IT/ST合格を宣言しない。
