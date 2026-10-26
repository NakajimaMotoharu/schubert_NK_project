# API request四Test・同値fixtureと私有名のPG/PT仕様

群API_REQUEST_FIXTURE_BATCH_PGPT_V1/event2504、WBS-F03、開始1/3/7pp cap10、共有使用24/残76/reset1793599188。基点source9c37bc73a20bab2028413db2c08f6bbdf28c76a6/Main21d、BUG1889-90/YKT1640-41/PG-D691。原program単体仕様・Test IDを保持する追加品質仕様であり新Program/外部仕様の作成ではない。

|Program/PT格納先|class・既Test ID|独立oracle/実操作|
|---|---|---|
|NK-SCN-001/008_NK-SCN-001|ScenarioRequestTest（三method、PT-SCN-009-Q01..Q03）|UI234手書き672byte等、明示field列/SS324 LP、JCE HMAC固定key11。queryは全callがAssertionErrorの未使用JDBC proxyとnull guardのみ|
|NK-MED-001/009_NK-MED-001|MediaRequestTest（三method、PT-MED033..035）|UI235手書き8layout・CanonicalField long/文字/close値、独立LP/JCE key11。実file/SQL無し|
|NK-QRY-001・NTF-001/014・013|QuestionQueryRequestTest（二method、PT-QRY009..010/NTF009）|UI236手書き384/64/ID12byte・nullと空区別、独立LP/JCE key0。all-null query guardと応答page metadataのみ|
|NK-QST-001/011_NK-QST-001|QuestionSubmitRequestTest（八method、PT-QST-SUB001..008）|UI236手書き4144byte・質問UTF8上限4096/UUID36、独立LP/JCE key0・owner/body binding、buffer terminal/race、固定redacted trace一|

関連RD FUN003..007/QST001..010/NTF001..012/MQ006..010/UI234235236241/SS323§9.1,9.2,9.6・324/332/SSC025029070157。Main対象ScenarioRequest/MediaRequest/QuestionQueryRequest/QuestionSubmitRequestは全文read、Canonical/Protocolは既固定sourceのmemory処理、repositoryはconstructorに外部初期化なし・queryのObjects.requireNonNullより先へ進めない。認証/Inbox/実authority/現DB・鍵・原本・VM・Root・service操作を含めない。

## 品質是正・独立期待

原10690当四31rawのうちString duplicate12（5/3/2/2）を同じliteralのprivate定数へ。Submitのprivate MESSAGEをMESSAGE_IDへidentifierだけ変更し、data helperのif4096一だけMAXIMUM_QUESTION_UTF8_BYTES=4096へ。全元assertion/fixture/expectedは独立逆展開後の全token一致で保持する。Main/oracle計算法/各golden offset・length・JCE LPを変更しない。共有QRY.MESSAGEはDB系二Testからstatic importされるため局所rename対象外で、元警告一を未分類保持する。

UserMutationRequestTestはBeforeAll new ApiLogDatabaseFixture/実transactionがあり全class除外、そこからmethodやfixtureを抜出し実行しない。旧Web query form三はPG5980/1250の四100と現全byte同一を確認した選定訂正だけで、旧921の再演・現sourceへの全体資格移植0。

## PT_DEFAULT・固定副作用

既四Test/二wire helper・MainをreadしてDB/network/VM/Rootなしを確認。HMACの公開合成key（new byte[32]又は11埋め）は実鍵ではなく、生成結果を送信・配備・権限付与しない。Scenario/Media helperのUUID.randomUUIDはheader metadataだけで期待fingerprintに不使用、header identity比較は同wire objectであり乱数値に合否依存しない。Submit8worker64task・CountDownLatch/Future5/10s/TWR、memory atomic-close二admissible outcomeと終端拒否を検証、外側専用JVM240s。

唯一のfile書込は既PT-QST-SUB008固定redacted text、fresh owned CWDのtarget/question-submit-traces/PT-QST-SUB008.txtに限定。事前不存在/非symlink・内容/hash/余分な書込無しを後で確認。実raw body/key/context/tokenを出力しない。全16method/4suiteのclosed catalogのみ、extension自動検出/parallel/package discovery無効。実backend/Test DB/原cohort・保留二工具/Graph9動的/元deferred controllerを選択しない。

## Test ID・実行・終了条件

PT-REQ-FIX001：12 literal/1 private rename/1数値定数を逆展開し全元token復元、誤値/欠落/annotation/rename/境界値改変拒否、全Main/他input不変。PT-REQ-FIX002：当source原16TestのF/E/S/aborted0だけ成功、golden/JCE/Null/Unicode/数値境界/未知/close/並行の元期待不変。PT-REQ-FIX003：原static31から当14消滅を実XMLで確認、残raw17は適用性未分類を保持し抑制0/CS・processing0。PT-REQ-FIX004：単一exec/CRC・全API artifactの全class/line-method-class-branch実測、未到達は未到達としquery/descriptor等未実行を除外して100にしない。

pyflakes→11034同値plan/11036独立source→commit固定→11038六正常compile/PT0→11042原16PT→11040当四static→11044独立元XML/exec/全Main・他Test/完全APIcounter→最終trace/2142結果。command/実時刻/OS/JDK/tool/version/branch/source/hash・BUGをmanifestへ保存し各caseと一意対応。旧成功/execの確認再演や合算0、正式1964-53/17-190/工数null/QA051final/全F03・451未受入を維持。通常小群・commit・PMO返答待ち停止0。
