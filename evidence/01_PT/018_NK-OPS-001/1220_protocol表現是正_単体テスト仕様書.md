# 1220 protocol表現是正：単体テスト仕様書

Program NK-PRO-001/003、BUG1498/YKT1258/PG-D443/F03、RD MSG001～011/MQ014～038・UI232/234～237・SS322/323/333/354・411/451。修正前source6b5cea563のprotocol残八PMDは元5830 raw/全source・class証拠で保持、機能不具合とは混同しない。元3967の真正終端/独立資格を保全してからMainだけの表現是正へ進む。現在は未実装/未実行、new sourceは固定後に結果へ記す。

| 観点ID（実行Test IDは元XMLのclass/method） | class/method | 独立oracle・確認点 |
|---|---|---|
| EXPR001 | codec.FieldCodecTest.booleanAndReservedFieldsRejectUnknownBytes | byte literal0/1/space、必須/任意・未知2・長さ2/null拒否、boolean幅1不変 |
| EXPR002 | 同.textEncodeNormalizesUtf8AndPadsWithAsciiSpace / numericCodecChecksDigitsRangeAndOverflow | 正数幅1/zero長拒否、UTF-8/NFC/padding/数値最小最大とoverflow・空/null/未知 |
| EXPR003 | header.HeaderModelTest.enumsMapOnlyApprovedWireValues | UI232 literal S/A/I全方向、空/長さ2/null/未知拒否、InteractionKindの1char幅不変 |
| EXPR004 | 同.enumsMapOnlyApprovedWireValues | UI232 literal Q/S/E全方向、MessageKindの1char幅不変、EXPR003と同じ実caseを重複加算しない |
| EXPR005 | layout.LayoutMetadataTest.layoutDefinitionChecksEveryLengthAndKindInvariant / registryMatchesIndependentUi233Catalog | version1成功/2拒否・長さ/件数算式、独立64行TSVを全一致 |
| EXPR006 | layout.LayoutFieldCatalogTest.catalogMatchesIndependentUi234To236Fixture / parserRejectsMalformedUnknownAndDuplicateRows | 独立389field/8cell schema、短いrow・未知/重複/null拒否 |
| EXPR007 | 同.parserRejectsMalformedUnknownAndDuplicateRows / layoutFieldsRejectWrongAreaGapLengthAndNull | byte start/lengthの正数下限、不正整数/非正数・gap/空/型/null拒否、EXPR006の共通caseは二重加算0 |
| EXPR008 | file.LargeResultRecordCodecTest.writesAndReadsHeaderlessExactRecordsWithIndependentHash / decodeRejectsTruncationExtraHashAndIoFailure / verificationRejectsAllThirtyTwoDigestBytePositions | 4800×2 literal連結と独立JCA、37/53byte chunk・zero-read一回store/offset増加、EOF/余分byte/hash32位置/IO/null拒否 |

上記methodを含むprotocolの**全96件/20suite**と六module既定dependency guards九件の**計105/26**を`pg5844_protocol_expression_green.py`で一回実行する。Case名・oracle/resource・POMを変更せず、new case増分0。NoTests、strict warning、format、null型/SpotBugsを六module継承、六修正型のline/method/class/branch100を実XMLで要求し、未実測native/globalへ拡張しない。暗黙のVM/DB/業務起動を含まず、メモリbyte/固定Clock/literal/TSV/JCA・自己target/JVMだけの通常PTであり拒否代替ではない。

EXPR001～008はraw診断に一対一のレビュー観点IDで、新PTのaliasや追加PASSではない。実行結果は既Testのclass/method・XML hashへ一意対応させ、同じcaseを参照する複数観点も105件の母数を増やさない。

実行前にclean source・fresh枠>10・未使用namespaceを認証する。command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1 python3 -B tools/quality/pg5844_protocol_expression_green.py`、JDK25.0.4/Maven3.9.12/offline、環境/branch/commit/command/実exit/XML/coverage・hashは元manifestとallowlisted結果へ記録。期待値は上記既独立vector・SS値を維持し、定数を読むだけの水増しtestやprivate reflectionは使わない。

PG後は全851source/1666実Mainの差を宣言六owner（nested/debug含む）へ限定し、他ownerは同byte・既public ABI不変更を照合する。private命名定数はwire/JDBC/public ABIへ追加しない。PMD無除外で対象八の消失と他raw全件保持を確かめ、rule/toolを緩和しない。既3955/現3967・旧nativeをnew sourceへ合算せず、正式全scope同source/runは必要変更群の最後に閉じる。global品質/原本/VM所有/CHR/QA051final/正式1964-53は別未完のまま。
