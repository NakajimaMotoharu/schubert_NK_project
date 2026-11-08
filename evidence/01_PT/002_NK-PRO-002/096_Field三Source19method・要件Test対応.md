# Field三Source19method・要件/Test ID対応

仕様0183891、PG24660順方向/24662独立0。Main7aed/Test64f3の全120既存成功から、三Source20raw method（測定19＋標準private空ctor1）だけを対象とする。対応表はSource責任・JVM signature・関連RD/UI232/SS322・指定Caseのassert/独立期待を辿る静的参照であり、個別Caseのprobe帰属や全分岐oracleの完了を測定したものではない。新製品PT/coverage/leaf/正式の加算0。

| class/method（JVM signatureはJSON） | Source責任 | 関連RD | SS322節 | actual Caseラベル | 経路 |
|---|---|---|---|---|---|
| `String;IZ)[B` | WBS-P002-01 | MSG-002, MSG-003, MSG-007, MSG-008, MSG-010 | 4.1, 6.1, 11 | T1, G1, G2, G3, D1 | API直接 |
| `Optional;` | WBS-P002-01 | MSG-002, MSG-003, MSG-008, MSG-010 | 4.1, 6.1, 11 | T2, G1, G2, G3, D1 | API直接 |
| `FieldCodec#encodeNumeric(JIJJ)[B` | WBS-P002-01 | MSG-004, MSG-007 | 4.2, 11 | N1 | API直接 |
| `FieldCodec#decodeNumeric([BJJ)J` | WBS-P002-01 | MSG-004 | 4.2, 11 | N1, N2, N3, D1 | API直接 |
| `OptionalLong;` | WBS-P002-01 | MSG-004 | 4.2, 8, 11 | N2 | API直接 |
| `Boolean;Z)[B` | WBS-P002-01 | MSG-006 | 4.3, 11 | B1 | API直接 |
| `Optional;` | WBS-P002-01 | MSG-006 | 4.3, 11 | B1 | API直接 |
| `FieldCodec#requireSpaces([B)V` | WBS-P002-01 | MSG-003, MQ-017 | 4.1, 6, 11 | B1 | API直接 |
| `String;)V` | WBS-P002-01 | MSG-007, MSG-008 | 4.1, 11 | T1, G1, G2, G3 | caller: encodeText |
| `String;)V` | WBS-P002-01 | MSG-008 | 4.1, 11 | T2, G1, G2, G3 | caller: decodeText |
| `String;)Z` | WBS-P002-01 | MSG-008 | 4.1 | T1, T2 | caller: validateTextCharactersForEncode,validateTextCharactersForDecode |
| `FieldCodec#allBytes([BB)Z` | WBS-P002-01 | MSG-003, MSG-004, MSG-006, MQ-017 | 4.1, 4.2, 4.3, 8 | N2, B1 | caller: decodeNumericOrErrorFiller,requireSpaces |
| `FieldCodec#filled(IB)[B` | WBS-P002-01 | MSG-003, MSG-004 | 4.1, 4.2 | T1, N1 | caller: encodeText,encodeNumeric |
| `FieldCodec#requirePositiveLength(I)V` | WBS-P002-01 | MSG-002, MQ-017 | 4.1, 4.2 | T1, N1 | caller: encodeText,encodeNumeric |
| `FieldCodec#requireNonEmptyField([B)V` | WBS-P002-01 | MSG-002, MQ-017 | 4, 11 | T2, N1, N2, B1 | caller: decodeText,decodeNumeric,decodeNumericOrErrorFiller,requireSpaces |
| `String;)V` | WBS-P002-01 | MSG-007 | 11 | T1, N1, B1 | caller: encodeText,encodeNumeric,encodeBoolean |
| `CharacterCodingException;)V` | WBS-P002-01 | MSG-007 | 11 | T1, D1 | caller: encodeText |
| `String;)V` | WBS-P002-04 | MSG-002, MSG-004, MSG-006, MSG-008, MSG-010, MQ-017 | 11 | T2, N1, B1, D1 | caller: decodeText,decodeNumeric,decodeBoolean,requireSpaces |
| `Throwable;)V` | WBS-P002-04 | MSG-002, MSG-004 | 11 | T2, N1, D1 | caller: decodeText,decodeNumeric |

各ラベルのactualCaseKey・既Test ID alias・declaration行/全SourceSHA/assertbodySHA・独立期待値は `../018_NK-OPS-001/evidence/PG24660-field-three-method19-trace-v1/case-oracles.json`、method/source行・normal120のcounter・関連根拠は同 `method-trace.json` に一意対応。ラベルは新Test IDではない。

T1=Field text encode, T2=Field text decode, N1=numeric digits/range, N2=error filler, N3=semantic ceiling, D1=diagnostic/cause, G1=Hangul NFC, G2=Angstrom NFC, G3=combining NFC, B1=B/reserved。

全原Code byte/CRCとSourceは現正常Main一致。FieldCodecとFieldEncodingException二Source/17測定methodはP00201、PermanentProtocolException一Source/2methodはP00204（既割当保持、同じ測定groupを同じownerへ強制しない）。MQ017等の関連参照はRD専有担当/費用の追加を意味しない。

同一全120 execから参照した三classはL127/M19/C3/B84/I490未達0、例外二Sourceのbranch自然0はN-A/null、当参照でstrict非空Source gateを解除しない。FieldCodec私有空ctorはflags2/descriptor()V/CodeLength5/空Source body・公式report不存在の標準filter、人工呼出/手動除外0。

BUG2548/YKT2272は新工具の一律owner仮定を是正し、元descriptor/Source/Test/元scope三Source/予算を変更しない。case-body/静的caller edgeは独立逆照合済み、7metadata反証。全G13・branch期待の個別最終レビュー・全451・Root/native/CHR/正式は未受入。unique520Java416/候補114/pending12/whole93暫定/正式1964-53/工数null/全HOLD維持。
