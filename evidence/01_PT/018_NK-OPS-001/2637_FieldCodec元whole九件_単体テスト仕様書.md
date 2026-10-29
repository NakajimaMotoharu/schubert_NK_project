# 2637 FieldCodec 元whole九件 単体テスト仕様書

2026-10-30 JST / dev-foundation / Production6b53 / HEADaab48284ff095e65fcda00356c73251999ffa32d / PG-D883。群3024開始0.5/2/4pp cap10、選定読取からmarkerまでの遅延をeventに記載。2422～2425/1960/2030は旧成果参照で元source80ba/PG13178の9成功・execを当sourceへ転用しない。新codec入力/新Test/Production変更は0、現source6b53必要限定資格として既存whole一回だけ。

Main FieldCodec全body/例外二class、元FieldCodecTest全156行/6method、FieldCodecNfcGoldenTest全3method/全fixture/initializerを確認。依存はJDKのUTF8 encoder/decoder/Normalizer/byte配列/Optional/HexFormatのみで、file/thread/network/JMS/DB/VM/Root/graph9/鍵等へ接続0。PT_DEFAULT。Program=FieldCodec（全encode/decode/helper15methods）＋FieldEncodingException＋PermanentProtocolException、完全三Source各一physical。Main ownerP002-01/P002-01/P002-04、Test baselineはUNKNOWN/null、関連NK-PRO002/UI232§4/SS322§4～6,11。

|Test ID/元method|独立fixture・入力/操作・期待|
|---|---|
|PT-CODEC-FIELD-01 textEncodeNormalizesUtf8AndPadsWithAsciiSpace|ABのliteral ASCIIspace、結合éのc3a9、あ/emojiのUTF8、widthexact/over、nullable optionalとrequired、trailspace/control/surrogate拒否|
|FIELD-02 textDecodeIsStrictCanonicalAndOptionalAware|literalbyte列の末尾spaceだけ除去/空optional/mandatory、c328不正UTF8・非NFC/controls/null/empty拒否|
|FIELD-03 numericCodecChecksDigitsRangeAndOverflow|0/1/999 fixedascii、width/range/非digit/+/:/dot/Long overflow/下限、期待をProductionで計算しない|
|FIELD-04 numericErrorFillerDoesNotBecomeBusinessZero|00/errorProfileはempty、正常00は0、正常01は1、null/empty例外|
|FIELD-05 booleanAndReservedFieldsRejectUnknownBytes|byte0/1/spaceのclosedflag/unknown/長さ/null、reserved全spaceのみ|
|PT-CODEC-NUMMAX001 numericSemanticCeilingIsIndependentOfWireAndLongCapacity|000099/000100とsemantic99、Long.MAX-1/MAX固定decimal/拒否後array不変。2425独立任意精度五fixtureの根拠を保持|
|PT-CODEC-NFCGOLD001 HangulJamo|固定scalar/hex eab080/eab081とliteralpadding、非canonical元wire拒否/不変|
|NFCGOLD002 Angstrom|固定scalar/hex c385、2byteexact/1byte拒否、元e284abは拒否/不変|
|NFCGOLD003 combiningOrder|固定hex71cca3cc81の順序とpadding、非canonical71cc81cca3拒否/不変|

元Testのexpectedはliteral/JDK標準charset又はHexFormatだけでProduction methodをexpectedへ呼ばない。コードpoint/バイト/NFC/control/null/未知値・桁幅/semantic別上限を保持し、再送/transaction/並行は純値codecの当scope非対象。NPEは境界契約例外としてassertしProductionでcatch正常化0。

予定 `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14322_protocol_field_whole_nine_pt.py`、同source14216六Mainと元二Test/固定Reporter/新-only一JVM一exec。14324独立postは全入力/元XML9/一sessionCRC・完全三Source/四counterを測定し、例外classのbranch自然0はN/A、手動除外・人工constructor call/exec合成0。OS/JDKは元JVM実測prefixを既tested wrapperで構造化、各command/時刻/SDK/exit/hash/結果は2638へ。先行100/全formal1964-53/17-190/工数null/QA051final/全HOLDは不変更。
