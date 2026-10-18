# NK-OPS-001 / SSC306 Root ELF digest

WBS-P018-03.02。関連RD/UIは既NK-OPS-001追跡を継承、SS343/354/SSC137/143/306、411/451。設計only76047171b→origin/main1baf087b4（PR154、通常merge、remote照合済）。実装/全品質とは別。着手見積event1171（共有週次pp低.2/標準.8/高2.5）、実専有費/N/T/消化率null、元/v3/v4固定。

対象：RootServiceExecutableAdmission.digest(SeekableByteChannel)、内部digest(input,DigestFactory)、固定SHA-256生成。外部呼出しは従来どおり固定algorithm一つ、portはpackage内部のみ。借用channelをcloseしない、admitの所有scopeは変更しない。

|Test ID / 新RootElfDigestPortTest method|入力・操作|独立期待値 / 根拠|
|---|---|---|
|PT-ROOTELF-SSC306-001 fixedDigestFactoryIsCalledOnceAndBorrowedChannelStaysOpen|64byte公開ELF・数回read・固定SHA factory|literal hash caa6f4f58ad3ed35afa011abfdb3ef06a7799b5545082b32685f75cc9c454fe8、factory1回/readあり/close0/全借用bufferゼロ。既ELF offset0..6=127,69,76,70,2,1,1、18=62、他0、長64。expected生成に製造method不使用|
|002 unavailableAlgorithmIsRedactedAndDoesNotReadOrClose|factoryからNoSuchAlgorithmException（公開marker付き）|既固定IOExceptionメッセージroot executable unavailable、cause/suppressedなし、read/close0。port一回|
|003 unexpectedRuntimeAndErrorPreserveIdentityWithoutIo|factoryからIllegalStateException/AssertionError|同一object伝播、read/close0。未知失敗を成功/固定IOへ変換しない|
|004 nullContractsFailBeforeInputReads|input null / factory null / factory戻りnull|NPE fail-fast、input nullではfactory0、借用read/close0。NPEをcatchして正常扱いしない|
|005 oversizedReadReportIsRejectedAndBufferIsWiped|channelがbuffer8192byte書込後8193申告|StorageIoException/Reason.UNAVAILABLE、SS333の固定literal transfer storage operation failed/cause無し、借用close0、実bufferゼロ。n==positionに違反し、旧上限検査削除で拒否を失わない。provider専用messageとは区別（BUG1412是正根拠）|
|006 exactBufferBoundaryAndSplitHeaderKeepLiteralDigest|同64byte入力をchunk1/7/64/8192で読む|全て同じliteral hash、全input64byte消費、借用close0/zeroize。chunk設定はbuffer容量を変えない|
|007 readFailurePreservesIdentityAndWipesWithoutClose|実readが同一IOException / RuntimeException / Errorを投げる|同一object、読み出し開始時に捕捉したbufferが全ゼロ、借用close0|
|008 exactMaximumElfHasIndependentFixedHash|8MiB、同header/残0、chunk8192|Python標準hashlibによる独立固定vectorをtest literalへ凍結。8MiB以下の境界を厳格に維持、全bufferゼロ/close0|

008の独立算出command：`python3 -c 'import hashlib; v=bytearray(8388608);v[:7]=bytes([127,69,76,70,2,1,1]);v[18]=62;print(hashlib.sha256(v).hexdigest())'`、結果9c75e29938e99e5c154bf35e94a362e3e4de159e98ca02b25a032956e98aeca0。製造を呼ばない。005の期待値はSS333のStorageIoException固定契約とSS343のread invariant拒否保持に基づき、旧a2eccのrequire経路も独立に照合。誤期待値へMainを変更しない。

既RootServiceExecutableAdmissionTestの全caseを変更せず再実行し、旧header各offset、0/1/63/8MiB+1、zero/negative/count/EOF位置/size/IO/ACL/nullを維持。依存reactorの実storage/bootstrap suiteも選択し、NoTests/Failed/flaky/skipped/not-runは合格0。

手順：新Test先行→六module formatter gate→未実装overloadのcompile失敗をTDD REDとして記録（実装済仕様違反の障害ではない）→Main実装→再formatter→固定commitの隔離snapshotにselected Maven/PT/JaCoCo/SpotBugs。runnerのrunごと新directory、元証跡上書き0。Main byteは元PG4970/a2ecc全1650から選択compile moduleを照合し、Root outer変更＋DigestFactory SAM追加以外0を確認。既nativeは新sourceへ転用0。限定PT合格で全coverage/正式/PGPT完了を宣言しない。

結果は各run manifestに実日時/環境/command/commit/終了code/XML・log hash/対象method四counter/静的結果/差分を保存。本仕様時点でRED/GREEN未実行、BUGなし。実装済障害を発見した場合は修正前に915/必要916へ起票する。
