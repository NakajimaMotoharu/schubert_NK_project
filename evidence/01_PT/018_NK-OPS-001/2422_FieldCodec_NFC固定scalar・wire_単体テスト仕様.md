# FieldCodec NFC固定scalar・wire 単体テスト仕様

Program NK-PRO-002、FieldCodec.encodeText/decodeText（他field methodは関連回帰）、UI232・SS322§4/6/11・RD MQ固定長/NFC。canonical owner/cost WBS-P002-01は元485 Main rowから確認。event2789/CODEC_NFC_SCALAR_WIRE_GOLDENS3_V1、開始2/4/8pp cap10/freshused4/reset1793774153、元予測/専有費/N/T/工数null不変更。

当新三の関連RD IDはMQ-018/031/033、MSG-002/007/010（RD131/132のUTF-8 byte長・NFC先行・超過拒否）。UI232§4、SS322§4.1/6.1/11へ対応する。元五の既PT-PRO-002-X01～X03/N01/N02/B01の部分契約対応はProgram002元仕様を継承し、全64layout/全profileを当scopeで受入済みとはしない。

## 新規三case・独立oracle

期待値は以下のUnicode scalarとUTF-8 hex literalを固定し、production method/JDK Normalizerを呼んでexpectedを作らない。HexFormatは固定hexの読取だけ、入力不変更のexpected cloneも入力からだけ作る。SS322は送信NFC後にbyte上限検査・右ASCII space padding、受信非NFCは正規化せずPermanentProtocolException、送信byte超過はFieldEncodingExceptionを正とする。

| Test ID / method | 入力・操作 | 独立期待 |
| --- | --- | --- |
| PT-CODEC-NFCGOLD001 / nfcGolden001HangulJamoFitsComposedByteWidth | U+1100 U+1161、およびU+1100 U+1161 U+11A8を幅3/5/2でencode、固定wire decode | U+AC00 EA B0 80、U+AC01 EA B0 81。幅5は末尾20 20、幅2拒否。元6/9byte分解wireは受信拒否・元array不変 |
| PT-CODEC-NFCGOLD002 / nfcGolden002AngstromUsesCanonicalTwoByteScalarBeforeWidthCheck | U+212Bを幅2/3/1、固定wire decode | U+00C5 C3 85へNFC、幅3の末尾20・幅1拒否。元E2 84 AB wireは非NFC拒否・array不変 |
| PT-CODEC-NFCGOLD003 / nfcGolden003CanonicalCombiningOrderIsRequiredWithoutComposition | U+0071 U+0301 U+0323を幅5/6/4、固定wire decode | U+0071 U+0323 U+0301 =71 CC A3 CC 81（qは合成なし）。幅6末尾20・幅4拒否、元71 CC 81 CC A3は受信拒否・array不変 |

## 関連回帰と実行前判定

旧FieldCodecTestのwhole五methodは全sourceを閲覧済み、元literal期待/assertion/negativeを変更しない。new Test whole三と同source/runで当codecの影響するfield/padding/receiver/例外/null契約を関連回帰し、旧五を新規成果へ数えない。新八を旧成功に算術加算せず真正JUnit XML/終了から確認する。MainはFieldCodec/FieldEncodingException/PermanentProtocolExceptionの三source（JDK byte/charset/NFC/例外のみ）、Test二source。Main/既Test不変更、新Test一つだけ追加予定。

PT_DEFAULT：新旧wholeの副作用はmemory/JUnitのみ、実DB/JMS/VM/Root/FFM/native/Graph9/鍵/権限/業務IOなし。専用JVM/一session・上限240秒/heap768、空CWD・unique classpath、事前source/static/原五hashを固定後に通常六normal PT0、当八のみ実行、当五source static/六SB、独立一exec/XMLCRC/全artifactcounter/全1843Main旧1973Test同byte・新一physicalを確認する。old whole DB Testの抜出しなし、Current baseline不変更。

必須coverage/NPE方針451は不変更。FieldCodecのprivate utility constructor等を当群のため手動除外せず、測定未達はそのまま記録、全64layout/全source/CHR/native/正式PGPTの受入を当八だけで宣言しない。OS/JDK/tool/source/run/command/exit/input/expected/actual/coverage/BUG/証跡path/hashは2423・manifestへ保存する。正式1964/53・17/190・工数null/QA051finalと全actual/二保留工具/原本保全を維持する。
