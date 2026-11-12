# 公開canonical/AAD値 原8＋UTF16追加1 単体仕様

NK-MSG-002 / DAT009、UI241242、SS324§3-6/352。Main全CanonicalField/ResponseSnapshotIdentity、APIpackage-infoのnull契約。公開byte変換だけ、実FingerprintKeyRing/ResponseSnapshotCodec/暗号key/認可/InboxDBはHOLDのまま呼出し0。

|Test method|目的・入力・独立期待値|
|---|---|
|public001MetadataNullLexicalAndLengthBoundaries()|name1..64/type1..32 ASCII閉alphabet/null/未知/超過を拒否|
|public002CopiesNullEmptyAndTerminalWiping()|nullと空byte[]の区別・input/returnedcopy独立・terminalwipe/idempotentclose|
|public003NfcUtf8AndIndependentSignedDecimalLiterals()|NFC é日本の手書hex c3a9e697a5e69cac・long四端の独立decimal literal|
|public004DiagnosticNeverContainsSyntheticValue()|nullable/空/既知PUBLIC_ONLY値の診断redaction固定|
|public005IdentityRejectsMissingMalformedAndOutOfRangeValues()|requestID/layout8upper/version3/owner N12のnull・形式・範囲拒否|
|public006FactoriesRetainOnlyDataAndRedactDiagnostic()|公開record factories/Optionalowner1-maxと固定redacted診断|
|public007AadMatchesIndependentWholeByteVectorsAndNewBuffers()|独立全AAD102/110byteのlength-prefix/UUID16/format1/keyv1/layout/version/owner境界、戻りbuffer非共有/null key拒否|
|public008ConcurrentValueCallsUseIndependentOwnedBuffers()|4worker32buffer同値・各buffer別identity、invokeAll10/Future5/finallyshutdown-await10|
|public009MalformedUtf16AndFactoryMetadataFailuresKeepIndependentContracts()|孤立high/low・混合UTF16の固定拒否文、invalidname text/number factory例外、正常emoji手書UTF8 f09f9880|

原15を保持し公開UTF16新1だけ追加、共通実行は16であり9＋7を再度16へ加算しない。BUG2736: 二workerの無期限待ちを有限化、元全assertion保持/worker変換逆一致はPG28044。BUG2737/YKT2389: Publicだけ四literal展開・Assertions明示import・GJF、PG28048全token同一/異値拒否、他Main4/Test1はprestyle非該当。BUG2736のLogRequest3/QuestionSubmit8は実Fingerprint/DB wholeHOLDで未変更、親BUG/YKT2387を本16だけで閉じない。

独立期待値は上記固定byte/literal/範囲/状態から事前固定、production methodで生成しない。正常/境界/異常/例外/null/並行/終了/再送相当の独立bufferを扱い、実暗号/authority/DB/再送は当pureprogram非適用。RootそのままJava25/ErrorProne2.50/NullAway0.14.1/Werror Main4、一回compile、SDKはJSpecify/JUnit/SnakeYaml3.1.1だけ、Protocol/Web/APIの既jarは未使用。Main3class＋packageannotationの全physical4をcoverage/CRCに保持、独自除外0。

実行前 `python3 -B evidence/01_PT/018_NK-OPS-001/input/1979_public_config16_preflight.py`。通常 `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1977_public_config16_qualifier.py run <固定commit>`。独立 `python3 -B evidence/01_PT/018_NK-OPS-001/input/1980_public_config16_independent_post.py <同commit>`。Web公開templateは `-Dnk.pt.repository=<W/public-repository>` と二固定hashで結合し、実/etc/credentialを読まない。branch dev-foundation、Main e16500d7df27a55082f8c69a68c510414167dbb4、具体source/TestID/XML/環境/command/exit/入力・期待値・実値・四counter・hashはPG28058/60。

PMD生15は明示nullablebyteのnull/empty差2、閉YAML/Pathのsecretfree入力error catalog2、ownedJUnit pool10、既知null値CanonicalFieldの非所有0byte1をsourceanchorで個別判定、fullRoot静的適用/未分類/CS-SB-format0、抑制0（PG28054）。NoSuchAlgorithmExceptionなどJDK前提の異常伝播/環境providerに関する全工程資格は局所coverageへ換算しない。

本仕様時点は試験未実行、F/E/S/abort/flaky/notrunを合格にせず、未網羅は隠さない。全4physicalの技術測定と元190/同最終Main全451/実環境・formal1964-53・工数nullを区別する。
