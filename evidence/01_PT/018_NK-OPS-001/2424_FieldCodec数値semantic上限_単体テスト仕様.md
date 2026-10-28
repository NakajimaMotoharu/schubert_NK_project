# FieldCodec数値semantic上限・単体テスト仕様

Program NK-PRO-002、FieldCodec.decodeNumeric、WBS-P002-01、SS322§4.2/5/11・UI232 N型契約、既Program002 PT-PRO-002-N01/N02関連。event2791/FIELD_CODEC_SEMANTIC_CEILING1_V1、開始1/3/6pp cap10/freshused4/reset1793774153。前NFC群2423/13164はB83/1でdecodeNumericの分岐一未達、既pure protocol直接callerを検索し、FieldCodecTestの受信semantic下限拒否はあるが上限未満のwire容量とsemantic上限を分離する直接caseがないと確認した。これは追加品質境界で、既受入17の再認定や原計画の新leaf完成には数えない。

## PT-CODEC-NUMMAX001

`FieldCodecTest.numericSemanticCeilingIsIndependentOfWireAndLongCapacity`を一つ追加し、元五method/新NFC whole三の期待/操作を不変更にする。原Test全文は前source b11/normal13156 snapshotとGitへ不変更保存、新method以外の全tokenを逆変換して確認する。Mainは変更しない。

| 固定wire/入力 | maximum | 独立期待・根拠 |
| --- | --- | --- |
| ASCII 000099、最小0 | 99 | 99、上限inclusive |
| ASCII 000100、最小0 | 99 | PermanentProtocolException。6桁wireには収まるがsemantic最大99を一つ超える、切捨て/clampをしない。元byte array不変 |
| ASCII 9223372036854775806、最小0 | 9223372036854775806 | 固定long同値、上限inclusive |
| ASCII 9223372036854775807、最小0 | 9223372036854775807 | Long.MAX_VALUE、算術/19桁decode自体は成立 |
| 同じASCII 9223372036854775807 | 9223372036854775806 | PermanentProtocolException。long表現能力には収まるがsemantic上限を超える。元array不変 |

期待値は固定ASCII decimal/long literalとPython任意精度intの独立算術確認を根拠にし、production decodeをexpected生成へ使わない。例外は既receiver契約の強いPermanentProtocolException、RuntimeException等へ広げない。新method一つ/関連既八の同source/run whole九（二suite）へ進め、前source8成功/coverageを足し合わせない。

PT_DEFAULT：既閲覧済みcodec三Main・Test二のmemory/JDKだけ、実資源/DB/JMS/VM/Root/FFM/Graph9/鍵なし。専用JVM240heap768/空CWD/unique classpath、関連九/静的/六normal PT0とSB/独立一execCRC・全artifact/全1843Main同byte/旧1974Testの一class変更・他1973同byte/physical新0を確認。既NfcGoldenArtifactCoverageMeasureはProduct roots五と全artifact分母が同じなので不変更再利用、session契約のNFCGOLD識別子は工具namespaceであり新group/新runを別記する。旧8の確認再演ではなく新条件を含む当unitの必要関連回帰、NPE/null/数値他分岐は旧whole五へ一意対応。

全counter100は実測後だけ判定、未達/実行失敗は保持する。全64layout/Program002の43成果物/全451/CHR/native/正式1964-53・17-190/QA051final/工数nullは当scopeで更新しない。raw8459/corr966/参照3271pending975・元予測/NT/専有費null不変更、実日時/source/command/exit/期待実際/coverage/BUG/証跡hashは2425/manifestへ保存。
