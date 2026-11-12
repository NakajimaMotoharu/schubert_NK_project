# Canonical UTF16・NKOP1 単体テスト仕様書

Program NK-MSG-002 / WBS-P006-01。対象 CanonicalField（text/number/encoded/constructor/value/close/toString）、CanonicalRequest（constructor/normalizeRequired/close/toString）、OperationFingerprint全method、WipingByteArrayOutputStream全method。関連RD MQ006010/DAT009、UI241242、SS324§3、BUG2669/YKT2349/globalYKT2328、451/487。上位仕様/HMAC binary/wire/任意raw byte契約は不変更。

|Test ID・method|入力と操作|独立期待値・根拠|
|---|---|---|
|PT-IDEM-U1601/scalar001MalformedTextNeverAliasesQuestionMarkInCanonicalInput|8不正UTF16（孤立high/low、二high/二low、ASCII前後、high-ASCII-low、有効pair+孤立high）×Field.text/Request.owner/Request.targetの24境界をassertAll。加えてtext値null|各24はIAE、nullはNPE。SS324§3「NFC後UTF8」へ不正scalarを置換して?等と衝突させない。期待値をproduction methodから生成しない|
|PT-IDEM-U1602/scalar002SupplementaryNfcAndSignedNumberMatchIndependentVectors|U10000/U10FFFFを含むNFD e+accent fieldとtarget、number Long.MIN、owner7/QSTREQ01/001、公開synthetic zero鍵32byte|Python struct big endian LP、明示NFC é+scalar、number ASCII -9223372036854775808、hmac.sha256から事前作成した固定hex2本に一致。孤立拒否と正しいsupplementary受理を両立|
|PT-IDEM001002/OperationFingerprintTest原5|原canonical/OpenSSL固定vector、NFC/null-vs-empty/clone/redaction/全null・未知metadata・shortkey、所有子JVM内のJCA provider不足|原5 method/独立assert保持。provider変更は当自己所有JVMのプロセス内限定、host設定・実鍵・認証・接続に触れずfinallyで元provider位置を復元|
|PT-IDEM-WIPE001003/SecretBufferTest原3|全capacityのgrow/reset/close/異常、0/8191/8192/8193/1050000、offset/null/超過、caller clone・canonical上限|superseded旧配列と現全capacityをzero。caller copy不変、独立DataOutputStream/JCA期待。元3全method/source保持|

fixtureは純粋4Main+packageの全5physicalと全Test2classだけ。Protocol/Storage/API/Web旧jarをclasspathに入れず、actual四classのbinary I/O/compile/init0、実DB/broker/VM/鍵/Root0。並列/再送・業務TX/性能はこの文字列・buffer境界の対象外であり、P00601本体/別工程への合格代替にしない。人工的な分岐除外・未実行加算・旧exec合算は禁止。

PG26622の独立vectorsと原5source、PG26624修正前red真正10件9成功1失敗（不正24全失敗）を保全済。PG26626でMain2のfactoryへstrict scalar不変条件を追加、OperationFingerprint writerはowner/targetの確立済invariantとlayout/field metadata ASCIIを使うため不変更。secretを符号化した確認用bufferを別途増やさずcodePointsのscalar範囲だけ検査する。

予定command: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1290_canonical_scalar_qualifier.py compile|static`、独立preflight後、固定sourceへ `run <commit>`。Java25.0.4+7/Maven3.9.12/NullAway0.14.1/ErrorProne2.50.0/PMD7.28/Checkstyle14.3/SpotBugs4.10.4/JaCoCo0.8.15。終了code/XML全10/FESabort0、classinit/CRC/session、全4executable・四counter100%、fresh静的解析指摘の個別適用性0を独立postで判定する。実結果・対象source/run・hashは別実行結果とmanifestへ記録し、本仕様で先に成功扱いしない。
