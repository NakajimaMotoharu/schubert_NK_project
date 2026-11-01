# Technical session row・固定例外四Source 独立単体テスト仕様

NK-WEB-001/NK-AUT-001/NK-MSG-001、FUN001/AUT001～004/MQ008010、UI226242/231251、SS314§7.2.3/331§9.1/352/321§7、PG-D1127。開始HEAD9d62d676d329831e8dc389d7a31449f99fe600b7/dev-foundation、Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備。群18250開始前1/3/6pp cap10、主F03・元owner参照費0。新製造0。

3476の独立性を前提にSessionTechnicalValueContractTest全八method一exec、対象WebSessionRow42行/固定例外13+14+14行の四Source/四physicalを測定する。公開固定UUID/hash0hex/配列29byte/版PUBLIC/Instantだけ。これは真正ciphertext/session/cookie/tokenや実期限有効性ではなくmetadata。実暗号/鍵/認証chain/発行/DB/MQ/HTTP/VM/Root/native/graphclassifier/worker/Clock.now/permit0。配列cloneは実行true・秘密でない、一般JDK初期化IO未知null。

|TECH-VALUE ID|独立入力・操作/期待|
|---|---|
|001|created=last=expiry同microsecond、TTL1/version0とTTL28800/version999999999成功。六accessorは入力identity/reference/time/数値を保持、redaction固定文字列。現在有効session認定0|
|002|last又はexpiryのnanoがmicrosecond+1を拒否、round/truncateしない|
|003|last<created又はexpiry<lastを拒否、同値と正順は成功|
|004|TTL0/28801/整数両端を固定IAE。1..28800境界は001|
|005|version−1/1000000000/long両端を固定IAE。0..999999999境界は001|
|006|identity/payload/last/expiry各nullをNPE拒否、catch正常化しない|
|007|Login rejection固定message/causeなし、operation conflict固定message/409/causeなし。HTTP応答やform再取得/UUID消費は実行しない|
|008|CommittedFatal markerはnull cause又は公開合成causeをそのまま保持し固定message。元DLQ commit/ACK/graph探索やfatal通知を実行しない|

正常/境界/null/異常/例外を上記で確認。immutable constructor/getterだけで共有更新/並行/再送は当契約非該当、実repositoryの並行/再送は免除しない。期待値はSSの1/28800/0/999999999と手書き時刻/固定文字列で作り、Productionメソッドでexpected生成0。元JDBC/SessionSavedRequest/consumer Testの抽出・改作0、N/Q/authority/Graph HOLDを解除しない。

18250 raw→18252全Source closure/counter/同source XML/CRC/session→18254独立metadata否定/八oracle/TestCRC→18258/60 registry→18262/64 WBS→18265 binder、3478へ実測保存。normal14216/static14224/JDK25.0.4を同byte固定で再利用、成功全回帰/署名再演0。actualcommand/OS-JDK/time/branchHEAD/Main/helper/Test/class/XML/exec/hash/exitをmanifestへ。Failed/flaky/skipped/not-runは合格に含めずcoverage未実測は未確認、自然branch0=N/Aを厳密四100へ加点0。正式1964/53・歴史17/190/新WBS受入0/工数null・QA051final/G07G13F03/451/全HOLD不変。障害修正前915/916起票。
