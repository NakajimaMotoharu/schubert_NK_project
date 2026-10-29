# 2639 Protocol frame・payload 元whole二十四件 単体テスト仕様書

2026-10-30 JST、dev-foundation、開発Source6b53/HEADaab48284ff095e65fcda00356c73251999ffa32d、PG-D884。群3026の原18/3suite選定から、同じPayloadCodec完全Sourceのencode/decodeRecord・個別認証errorprofileを担う既存ScenarioRecordEncodingTest3/AuthenticationErrorProfileTest3を着手依存として追加し、元24method/5suiteへ実行前固定。原開始1/5/9pp cap10不変更、新codec入力/新Test ID/Production改変0。旧source成功の確認再演ではなく、当sourceの必要限定資格を元whole一回だけで測る。

全Test本文=Message744＋Payload514＋Golden224＋Scenario112＋Auth246、全initializer/helper/callbackを確認。Main HeaderCodec/FixedWidthEncoder/FixedWidthDecoder/ProtocolValidator/ExpectedRoute/TransportMetadata/TransportBodyType/MessageEncodingException/PayloadCodecの九完全Sourceを対象、PayloadCodecのcompiler synthetic enum-switch一physicalも閉包へ含む。syntheticはACC_SYNTHETIC(4128)/SourceFile PayloadCodec.java/field1・clinit Code55byte、既定JaCoCo filterによりcounter0ならgenerated metadataとして記録し、noCode interfaceと混同しない。手動除外やfilter改変なし。

Main既canonicalはHeader/ExpectedRoute/TransportMetadata/BodyType/MessageEncodingException=P002-03、Encoder/Decoder/Validator=P002-01、PayloadCodec=P002-02。Test baselineUNKNOWN/null。関連NK-PRO002/UI231232233234235236/SS322§2,4～7,11・SS323/333。必要CommonHeader全body/Immutable値DTO/既読FieldCodec/LayoutFieldCatalog constructor/parser/initializer/固定64layout経路も確認、helperの全coverageへ昇格しない。

## 独立oracle・Test ID
- PT-CODEC-FRAME001..007＝Messageの7元method。独立256byte header offset表/response・event literal、全field/profile汚損、defensive FixedPayload/WireMessage、body255/1000001/route1001境界、JMS property snapshotとroute mismatch、null/range/enum/期限/宛先closed契約。TransportMetadataは値だけでJMS接続ではない。
- PT-CODEC-PAYLOAD001..008＝Payloadの8元method。64layoutのroundtripは補助整合確認とし、それだけを独立oracleとは呼ばない。31response errorfiller、取消conflict PROCESSING/COMPLETED/ERRORとCANCELLED successの独立32byte literal、login384byte offset、固定REQUEST位置、未知/mandatory/wrongtype/record上限、null/length/filler/immutable/redaction、N1/N18/0/19の固定数値境界。
- PT-CODEC-GOLD001..003＝Goldenの3元method。全64layout min/max/errorの固定SHA-256 TSVをexpectedとし、actualだけcodec呼出。fixtureの最大入力作成にmaximumForDigitsを利用するがexpected SHAは独立TSVであり、その値をProductionから作らない。14repeating-layout最大record境界、共有codecの自己所有8thread・独立LGN384byte A位置0/64/320。
- PT-SCN-008-W03/RD02＝Scenarioの3元method。独立4800byte record、固定offset0/12/18/26/164/4260・本文UTF8・0/4799/4801/null/unknown/non-record/mandatory/不正UTF8/非NFC/reserved。
- PT-CODEC-AUTHERR001..003＝Authの3元method。独立LGN432byte retry位置167幅6＋filler3/message176幅256、retry0/1/900・-1/901/wrongtype/unknownfield filler、31response×全error codeを独立layout/field TSVからexpected算出、message256/257byte/controls/trailspace、取消例外profileも固定byteで照合。実Login/session/token発行/credential操作ではない。

## fixture・実行条件
三public固定fixture（src/schubert-nk-protocol/src/test/resources/protocol/）を当Source git blob/現file/新-onlyfresh-test-classesへ同byte copyしてclasspath先頭から読む。元TSV/Current baselineを書換えない。
- payload-golden-ui234-236.tsv SHA256 49bb76ec610216042f8e53ed548f4d5e52707a8bbf930a9fc6c93300dfa24839
- fields-ui234-236.tsv SHA256 b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b
- layouts-ui233.tsv SHA256 c4f290595f5cabf19c11877e2dea95627b4d42490116431bac3bfde58950d711

全依存はpure値/固定table/JDKcodec・declared fixture読取・自己所有有限thread。Goldenのready.await/future.getは局所timeoutなしを明示し、固定8issuer/外側JVM180秒の所有budgetで拘束する。実server性能/ITST・全fixture例外網羅へ拡大しない。実DB/ブローカー/network/HTTP/VM/Root/鍵/permit/cohort/graph9/私有rawlog操作なし、PT_DEFAULT。

予定command `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14326_protocol_frame_payload_whole_twenty_four_pt.py`。同source14216六Jar/元五Test/固定Reporter、新-only一JVM一exec、F/E/S/aborted/timeout/exit/重複XML・全input/fixture/SDK hash/元環境を保持。14328独立postで完全九Source/10physicalを測り、未達は未達、自然branch0はN/A、synthetic metadataはflags/既定filtered counter0根拠を明記。actualJMS metadataは合成snapshotのみ。結果2640へ実command/時刻/OS-JDK/SDK/hash/counter/障害を保存、現109/旧sourceの成功やexecを合成せず、全formal/工数null/QA051final/HOLD不変更。
