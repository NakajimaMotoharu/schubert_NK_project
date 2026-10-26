# Batch/Bootstrap/Web共有selector62候補の文脈レビュー

2026-10-26、群2345/G03.01、開始.5/2/6 cap10、current21228608b。PG10252の残62site/36sourceを現SHAへ照合する。以下はsource文脈の判定であり、元Testを再実行せず、DB/VM/原本/鍵/native/permit退役/Root/Graphの実証ではない。全oracle独立正常やcoverageを一括認定しない。

|source|site数|根拠/判定|
|---|---:|---|
|BackupManifestValuesTest|3|明示START/END等とfixtureで指定するStep時刻の保持・境界、JDK Instant.parseの入力保存。getter二重使用は境界と保存の補助契約。|
|BackupManifestCodecTest|1|手書きwhole manifestをdecodeし、文字列A/B/D～H各128及び全時刻/IDをliteralで比較。List.ofはJDKだけ。|
|CaddyPublicConfigurationTest|1|SS342独立GOLDEN directive全文と配備templateをTest normalでtrim/comment除去のみ。Production parserをexpectedへ使用しない。|
|DurableRecordFilesTest|1|同時公開の二partの存在XOR、残った内容は固定GOLDEN。相互排他の補助propertyで実native資格とは別。|
|MaintenanceRecordsTest|1|入力RUN.cutoff保存とSUCCESS0/WARNING10の別literal。|
|MaintenanceRetirementRecordsTest|2|入力cutoff/最大Instant保持、null/精度/時系列拒否との組合せ。|
|MaintenanceRunFilesTest|2|completionはTest固定ACTIVATION/終了Instant/指定Outcomeを構築するだけ。diskは別DONE0 literalで比較、再試行後の返却同値は補助property。|
|PostgresObservationRowsTest|2|独立構築した1000行のexpected wire、schemaRowsとmigrationsの両方を元rowsへ比較済み。同値はalias/防御copyの補助、oversize/rank gapは別literal。|
|StartupPermitFilesTest|3|invalidは固定State.INVALID/BOOT/EPOCH/ACTIVE/Optional.emptyのTest factory。revoke後のcurrent/permit bytesもINVALID/GOLD literalで別検査。今回実行しない。|
|ContinuousConditionWindowTest|11|Duration factoryはJDK。10→309.999999999の差299.999999999、gap/reset/最大値/同点並行の独立算術期待。|
|TimedFilesystemMonitorTest|1|Optional.emptyの入力保存だけ、UNKNOWN/gap/無効観測との組合せ。|
|InspectorHeldStateContractTest|1|active/sub/resultのTest側明示論理式から独立failed/quiescent期待を生成。Optional.emptyはJDK、実Unit照合ではない。|
|MorningCaddyReadinessTest|3|独立proc行literalと期待inode集合12345/空。Set.ofはJDK。|
|MorningServiceReadinessTest|5|固定IPv4/IPv6 addr/port/state/inodeを一項目ずつ変更し12345/空へ比較。Set.ofはJDK。|
|BackupTerminalObservationTest|1|明示d/c順の入力保持、別step/ref alias拒否。List.ofはJDK。|
|CleanupRepositoryTest|1|最小/最大Instant入力保存、範囲外/精度の別拒否。|
|ExpirySuccessfulScopeTest|1|Optional.emptyはJDK。admitted resourceのidentityとrelease対象を別capture/明示後条件で確認。今回JDBCや失敗経路を不実行。|
|MorningDatabaseSessionTest|1|receiptsはTest指定0/10/30の順、同receiptの終了codeをhandoffへ渡した保存property。ExpiryReceiptFixtureは手書きkernel/bus fields、元DB後条件/literal auditは別。今回fixture/gate/DBを実行しない。|
|ApiNonSecretConfigTest|1|独立GOLDEN全文を行分解し各値/別JDK hashを比較。substringはJDK parserでProduction共有ではない。|
|ServiceProcessResourcesTest|1|取得途中失敗後のcopied配列全要素ゼロという補助property。容量は独立oracleでないが、ServiceCredentialSetTestの公開pt-public-db-api等の固定copy内容・別所有契約と区別する。新key-close witnessや実行を追加しない。|
|NativeCoverageExportTest|1|物理自己fixtureのrun/output UID不変という補助property。model Root UIDを期待値へ転用しない。今回native/export/ファイル操作なし。|
|ReleaseInventoryTest|1|JDK repeatの201文字固定境界入力保存。|
|StartupProofFrameTest|1|公開合成zero64を入力し同literal期待、長さ63/65・大文字等は別拒否。|
|WebNonSecretConfigTest|2|独立GOLDEN/別JDK hash、固定URL最大byte literal。substring/repeatはJDK、今回接続なし。|
|WebAdmissionRemainderTest|1|独立GOLDEN全文/別JDK SHAとcode50/70 literal、substringはJDK。今回admission実行なし。|
|HttpRequestLoggingValveTest|1|message/correlation同値は同requestの関連property、別status/path/ID一意/秘密非露出を確認する元assertionあり。一取得値の自己比較ではない。|
|WebApiLogReplayIntegrationTest|1|固定JSON literalとDB値をJDK-adjacent Gsonで構造比較。Production builderでexpectedを生成しない。今回DB再演0。|
|WebAuditSinkContractTest|1|固定timestamp/service/action/errorCodeの独立JSON literalをGsonで構造比較。|
|ContentDispositionFactoryTest|1|明示percent-UTF8 E38182を84回、入力のあ84回と独立固定符号化、ASCII/危険文字/境界vectorあり。repeatはJDK。|
|MediaBytesMetricRecorderTest|1|Test index1～64のbytesを事前Mapへ加算し、別registry/64increment/7byte独立ownerを比較。enum.nameはlabel共有でSUT計算をexpectedへ使わない。|
|WebOutboxObservationRepositoryTest|1|固定rs/ps例外identityの順序、List.ofはJDK。今回SQL/例外graphを起動しない。|
|RevocationRetryCoordinatorTest|2|初回/再送UUID非同値の補助property、別DB件数0/1/2・確定結果・時刻literal。今回実API/DBを実行しない。|
|NotificationControllerTest|2|明示ID2/1順、同時target/context対応の補助property。各taskは入力nとpageID/reader文字列を別assertし、100request/100UUID一意も固定期待。asciiはTest byte読取だけ。|
|SessionAttributeCodecTest|1|NFD32回→独立NFCé32回の固定期待、repeatはJDK。|
|WebCsrfIntegrationTest|1|二attribute同一instanceというSpring連携契約。別固定TOKEN/遅延supplier0→1回を確認、今回HTTP/CSRF実行なし。|
|LogSearchResultsViewModelTest|1|TestのUTC時刻→明示ISO表示文字列の三pair。pair.getはTest固定期待の選択、SUT formattingを期待へ使わない。|

当62文脈で新規の製品依存expected欠陥は認定しない。API42と合わせ104共有selector候補の文脈を点検したが、直接call3492/identifier3675/constructor428（重複あり）の全件証明や要求/TestID/branch/evidence join完了ではない。メタ索引/レビューを製品PT・個別受入・工数率へ換算0。既BUG1811是正と1812の既19静的残件、元業務PT未実行/HOLDは別状態のまま。
