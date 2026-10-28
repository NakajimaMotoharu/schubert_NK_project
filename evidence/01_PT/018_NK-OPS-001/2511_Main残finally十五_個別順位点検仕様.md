# 2511 Main残finally十五 個別順位点検仕様

2026-10-29、START2890、PG-D821予定、source17ab52b25/Main/Test非変更。開始1/3/6pp cap10、fresh29残71/reset1793774153。主F03、canonicalP01805/P01707/P01711/P01806/P00502/P01104担当費参照のみ追加予算0、原WBS/旧見積/受入/全995runtime不変更。現save3368d2ac323c7806b2194f00f7a3816b83b1d45e/push19869真正0/remote一致、normal13596/全Main静的13599同source証拠の確認再演0。

## 個別対象と期待契約

|元PMD ID|対象/期待・判定根拠|
|---|---|
|00104/00111|ApiDependencyReadiness.verify/probeのConnection/各JMS context。必須close失敗を無視せず、primaryなし→close失敗、close直接Error対非Errorprimary→Error、その他元primaryと既attachment。SS312/321/342のfatal優先。|
|03264/03269|CleanupRepository.executeのrow→statement。保留returnより先に両closeが帰還する必要、借用Connection非変更。既SQL/unknown選択を一般TWR化で変えない。|
|03274/03279|同readLogProgressのrow→statement。同primaryと固定secondaryを保持しclose失敗を成功進捗へ変換しない。SS332/341。|
|03348/03353|ExpiryAuditRepository.readのnullable rows→statement。SS332冒頭SSC310のSQL/unknown・nullable acquisition・同identity/固定secondary、成功empty/presentもclose帰還前に確定させない。|
|07190/07197|WebDependencyReadiness.verifyのConnection/JMS context。上記readinessのdirect fatal優先とHTTP開始前の必須close。Graph処理そのものの資格は対象外。|
|07345|ReplyConsumers.deliveryFailure、SS321 SSC332の既選択ErrorをonFatal通知後も同一identityで再throw。selectedFatalなしでは通知の戻り/失敗を変更しない。rollback試行は通知前、finally自体に省略されるowned cleanupなし。|
|07389|ReceiptReferenceRepository.registerのstatement、同PK readback/親transactionの前に一度close。close失敗時にinsert成功としない。QA048/SS331332。|
|07394/07399|同readのrow→statement。SQL/unknown選択とSS329の破棄前graph口を保持し、closed resultを確認してからOptional返却。|
|07408|同transactionのConnection。commit結果のpending returnもowned close帰還まで返さず、close失敗をcommit失敗確定/業務再送許可へ読み替えない。rollbackも元SQL/unknown契約を維持。|

上記六Mainの当該methodの取得～body～catch～finally～上位return/throwを点検し、Cleanup/Receiptは全Main、Expiryはreadと必須helper/constructor・関連recordを読む。Expiryの未読他methodまで全classレビュー済みとしない。JdbcResourceFailures全body、Receipt内replace全body、正常・失敗・null・同例外・未知/fatal・closeとreturnの順位を反証的に確認する。raw十五は全部保留全体join待ち、異常throwを消してPMD0を作らない。依存graphアルゴリズム/actualDB・brokerの所有/終端は別未完/HOLD。

実承認設計はorigin/main8b91944dfのSS332冒頭SSC310/199・SS321 SSC332/333を閲覧。基準7field/SQL/query/role/commit/rollback/retry/ACK/外部互換を変えない。既1253/2231と1975の後続静的資料を参照し、元実動的成功を当sourceへ移転しない。未知/Graph9依存は実行保留で、同じ検証を別caller/fixtureへ作り直さない。

13760はcurrent normal全源・raw13253 JSON・元ID10690と固定PMD半開span/ownerを結合。13762は別XMLと独立offset/負typed metadata、13764/66は原raw6247/refs3373pending2512noRef2874から十五参照だけ追記。原941論理943歴史physical/全995runtime/予算受入不変を検証。commandはchecked entry各工具、target load/fixture/PT/VM/DB/MQ/Root/native/鍵/held工具/私有raw操作0。新コード/実行PT/coverage/正式受入0、当source同byteの既compile/static参照のみ。静的判断をPT免除/代替完了/実終端・全Graph資格へ変換せず保存後も継続する。
